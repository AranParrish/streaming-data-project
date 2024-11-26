import pytest, boto3, logging, os
from moto import mock_aws
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError
from src.streaming_data import get_api_key, streaming_data

@pytest.fixture(scope="function")
def mock_aws_credentials():
    """Mocked AWS Credentials for moto."""

    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"

@pytest.mark.describe("Get API key function tests")
class TestGetAPIKey:

    @pytest.mark.it("Retrieves key for valid secret name")
    def tests_retrieve_secret_valid_name(self):
        secret_name = "guardian_api_key"
        region = "eu-west-2"
        assert isinstance(get_api_key(secret_name, region), dict)

    @pytest.mark.it("Logs ClientError for invalid secret name")
    def test_retrieve_secret_invalid_name(self, caplog):
        invalid_secret_name = "invalid_secret_name"
        region = "eu-west-2"
        with caplog.at_level(logging.ERROR):
            get_api_key(invalid_secret_name, region)
            assert "ClientError" in caplog.text

# Lookup how to mock secrets manager client and test functionality that way

# API tests
#   - check that response is 200 (i.e. valid API key)
#   - check orderBy is "newest"
#   - check that currentPage is 1
#   - check that length of results is 10