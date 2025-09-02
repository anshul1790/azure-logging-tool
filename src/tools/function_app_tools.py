import os
from dotenv import load_dotenv
from ..core.azure_observability_sdk import AzureObservabilitySDK
from ..models import Environment

from langchain.tools import tool

load_dotenv()

@tool
def list_function_apps() -> str:
    """List all the available function apps in a given azure subscription."""
    environment = os.getenv("AZURE_ENVIRONMENT", "optumqa")

    # sdk = AzureObservabilitySDK(Environment(environment.lower()))
    # apps = sdk.list_function_apps()
    # if not apps:
    #     return "No function apps found in the subscription."
    # app_list = "Available Function Apps:\n"
    # for i, app in enumerate(apps, 1):
    #     # Handle both dict/object and string cases
    #     if hasattr(app, 'name') and hasattr(app, 'resource_group'):
    #         app_list += f"{i}. {app.name} (Resource Group: {app.resource_group})\n"
    #     elif isinstance(app, dict) and 'name' in app and 'resource_group' in app:
    #         app_list += f"{i}. {app['name']} (Resource Group: {app['resource_group']})\n"
    #     else:
    #         app_list += f"{i}. {str(app)}\n"
    # return app_list
    apps = [
        {"name": "fnc-aep-martech-directmail-optumqa", "resource_group": "rg-martech"},
        {"name": "fnc-aep-martech-guid-gen-optumqa", "resource_group": "rg-martech"},
        {"name": "fnc-aep-martech-hygieme-optumqa", "resource_group": "rg-martech"}
    ]

    app_list = "Available Function Apps:\n"
    for i, app in enumerate(apps, 1):
        app_list += f"{i}. {app['name']} (Resource Group: {app['resource_group']})\n"

    return app_list.strip()


@tool
def function_app_details(function_app_name: str) -> str:
    """Get the details of a given function app."""
    environment = os.getenv("AZURE_ENVIRONMENT", "optumqa")

    # try:
    #     sdk = AzureObservabilitySDK(Environment(environment.lower()))
    #     details = sdk.get_function_app_info(function_app_name)
    #
    #     if not details:
    #         return f"Function app '{function_app_name}' not found."
    #
    #     return f"Function App Details for {function_app_name}:\n{details}"
    # except Exception as e:
    #     return f"Error getting details for {function_app_name}: {str(e)}"
    dummy_details = {
        "fnc-aep-martech-directmail-optumqa": {
            "status": "Running",
            "region": "East US",
            "runtime": "Python 3.10",
            "last_updated": "2025-09-01 12:30:00"
        },
        "fnc-aep-martech-guid-gen-optumqa": {
            "status": "Stopped",
            "region": "West US",
            "runtime": "Java 11",
            "last_updated": "2025-08-29 09:15:00"
        },
        "fnc-aep-martech-hygieme-optumqa": {
            "status": "Running",
            "region": "Central US",
            "runtime": "Node.js 18",
            "last_updated": "2025-09-02 10:00:00"
        }
    }

    details = dummy_details.get(function_app_name)
    if not details:
        return f"Function app '{function_app_name}' not found."

    return (
        f"Function App Details for {function_app_name}:\n"
        f"Status: {details['status']}\n"
        f"Region: {details['region']}\n"
        f"Runtime: {details['runtime']}\n"
        f"Last Updated: {details['last_updated']}"
    )
