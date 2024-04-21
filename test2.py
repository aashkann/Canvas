"""Run integration tests with a speckle server."""

import secrets
import string

import pytest
from gql import gql
from speckle_automate import (
    AutomationContext,
    AutomationRunData,
    AutomationStatus,
    run_function,
)
from specklepy.api.client import SpeckleClient
from specklepy.objects.base import Base

from main import FunctionInputs, automate_function

SPECKLE_TOKEN = "8b821b4eff2d9f4b60604bbaf66313116197ce4674"
SPECKLE_URL= "https://latest.speckle.systems/"


def crypto_random_string(length: int) -> str:
    """Generate a semi crypto random string of a given length."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def register_new_automation(
    project_id: str,
    model_id: str,
    speckle_client: SpeckleClient,
    automation_id: str,
    automation_name: str,
    automation_revision_id: str,
):
    """Register a new automation in the speckle server."""
    query = gql(
        """
        mutation CreateAutomation(
            $projectId: String! 
            $modelId: String! 
            $automationName: String!
            $automationId: String! 
            $automationRevisionId: String!
        ) {
                automationMutations {
                    create(
                        input: {
                            projectId: $projectId
                            modelId: $modelId
                            automationName: $automationName 
                            automationId: $automationId
                            automationRevisionId: $automationRevisionId
                        }
                    )
                }
            }
        """
    )
    params = {
        "projectId": project_id,
        "modelId": model_id,
        "automationName": automation_name,
        "automationId": automation_id,
        "automationRevisionId": automation_revision_id,
    }
    speckle_client.httpclient.execute(query, params)


def test_client() -> SpeckleClient:
    """Initialize a SpeckleClient for testing."""
    test_client = SpeckleClient(
        SPECKLE_URL, True
    )
    test_client.authenticate_with_token(SPECKLE_TOKEN)
    return test_client


def test_object() -> Base:
    """Create a Base model for testing."""
    root_object = Base()
    root_object.foo = "bar"
    return root_object



def fake_automation_run_data(test_client: SpeckleClient) -> AutomationRunData:
    SERVER_URL = SPECKLE_URL

    project_id = "9a079d8ace"
    model_id = "d265590641"

    function_name = "Automate Density Check"

    automation_id = crypto_random_string(10)
    automation_name = "Local Test Automation"
    automation_revision_id = crypto_random_string(10)

    register_new_automation(
        project_id,
        model_id,
        test_client,
        automation_id,
        automation_name,
        automation_revision_id,
    )

    fake_run_data = AutomationRunData(
        project_id=project_id,
        model_id=model_id,
        branch_name="main",
        version_id="cd9d570c74",
        speckle_server_url=SERVER_URL,
        # These ids would be available with a valid registered Automation definition.
        automation_id=automation_id,
        automation_revision_id=automation_revision_id,
        automation_run_id=crypto_random_string(12),
        # These ids would be available with a valid registered Function definition. Can also be faked.
        function_id="12345",
        function_name=function_name,
        function_logo=None,
    )

    return fake_run_data


def test_function_run(fake_automation_run_data: AutomationRunData):
    """Run an integration test for the automate function."""
    context = AutomationContext.initialize(fake_automation_run_data, SPECKLE_TOKEN)

    automate_sdk = run_function(
        context,
        automate_function,
        FunctionInputs(forbidden_speckle_type="Wall", whisper_message="Hello World!"),
    )

    assert automate_sdk.run_status == AutomationStatus.FAILED


test_function_run(fake_automation_run_data(test_client()))
