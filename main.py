# main method

from src.core.azure_observability_sdk import AzureObservabilitySDK, show_logs_demo
from src.models import Environment

# Main execution for testing
if __name__ == "__main__":
    try:
        # Initialize SDK for QA environment
        print(" Initializing Azure SDK...")
        sdk = AzureObservabilitySDK(Environment.OPTUMQA)
        print(" SDK initialized successfully\n")

        # Specific Function App to analyze
        target_application_name = "fnc-aep-martech-directmail-optumqa"

        # show_function_app_info(sdk, target_application_name)
        show_logs_demo(sdk, target_application_name)
        # show_metrics_demo(sdk, target_application_name)

    except Exception as e:
        print(f" Error during testing: {e}")
        import traceback
        traceback.print_exc()