# azure_logging_agent.py

from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain.chains.summarize import load_summarize_chain
from tiktoken import encoding_for_model

from ..core.openai_client import get_openai_llm
from ..tools.logging_tools import LoggingTools
from ..tools.function_app_tools import FunctionAppTool

from ..models import Environment

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

class AzureHubLoggingAgent:
    def __init__(self, thread_id: str = "default-thread", environment:str = Environment.OPTUMQA):
        self.thread_id = thread_id
        self.environment = environment
        self.max_tokens = 2000
        self.encoder = encoding_for_model("gpt-3.5-turbo")
        self.llm = get_openai_llm()
        self.summarizer_llm = ChatOpenAI(temperature=0.0, model="gpt-3.5-turbo")

        # Create tool instances with environment
        logging_tools = LoggingTools(self.environment)
        function_app_tools = FunctionAppTool(self.environment)

        self.tools = [
            logging_tools.get_application_logs,
            function_app_tools.list_function_apps,
            function_app_tools.function_app_details,
        ]

        self.react_prompt = hub.pull("hwchase17/react")
        self.agent = create_react_agent(self.llm, self.tools, self.react_prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

        self.summary_chain = load_summarize_chain(
            self.summarizer_llm,
            chain_type="map_reduce",
            verbose=False,
        )

        self.memory = MemorySaver()
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(state_schema=MessagesState)
        workflow.add_node("summarize", self._summarize_old_messages)
        workflow.add_node("agent", self._safe_call_agent)
        workflow.add_edge(START, "summarize")
        workflow.add_edge("summarize", "agent")
        return workflow.compile(checkpointer=self.memory)

    def _summarize_old_messages(self, state: MessagesState):
        messages = state["messages"]
        total_tokens = sum(len(self.encoder.encode(m.content)) for m in messages)
        logger.info("Summarizing messages: %d tokens", total_tokens)

        if total_tokens < self.max_tokens:
            return {"messages": messages}

        summary = self.summary_chain.invoke({"input": messages})["output"]
        logger.info("Summary generated: %s", summary[:100])
        new_history = messages[-5:] + [AIMessage(content=summary)]
        return {"messages": new_history}

    def _call_agent(self, state: MessagesState):
        logger.info("Calling agent with %d messages", len(state["messages"]))
        # Inject environment into every tool call
        input_messages = state["messages"]
        # Wrap the input so that every tool gets environment
        # This assumes the agent expects a dict with 'input' as messages
        # and will pass environment to all tools
        response = self.agent_executor.invoke({
            "input": input_messages,
            "environment": self.environment
        })
        output = response.get("output", "").strip()
        logger.info("Agent response: %s", output[:100])
        return {"messages": input_messages + [AIMessage(content=output)]}

    def _safe_call_agent(self, state: MessagesState):
        try:
            result = self._call_agent(state)
            last_msg = result["messages"][-1].content.strip()

            if not last_msg or "I don't know" in last_msg.lower():
                fallback = AIMessage(
                    content="🤔 I'm not sure how to help with that yet, but I'm learning every day. Could you rephrase or ask something else?")
                return {"messages": state["messages"] + [fallback]}

            return result

        except Exception as e:
            logger.error("Agent call failed: %s", str(e), exc_info=True)
            err = AIMessage(content=f"⚠️ Oops, something went wrong: {e}")
            return {"messages": state["messages"] + [err]}

    def get_history(self) -> list[str]:
        """Returns the current message history as plain text."""
        checkpoint = self.memory.get({"configurable": {"thread_id": self.thread_id}})
        if not checkpoint or "messages" not in checkpoint:
            return []
        return [f"{getattr(msg, 'type', 'AI')}: {getattr(msg, 'content', str(msg))}" for msg in checkpoint["messages"]]

    def chat(self, user_input: str):
        logger.info("Received user input: %s", user_input)
        initial_state = {"messages": [HumanMessage(content=user_input)]}
        result = self.app.invoke(
            initial_state,
            config={"configurable": {"thread_id": self.thread_id}},
        )
        return result["messages"][-1].content
