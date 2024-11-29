import pytest, boto3, logging, os
from moto import mock_aws
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError
from src.streaming_data import get_api_key, api_results


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
            assert "ResourceNotFoundException" in caplog.text


@pytest.mark.describe("API results function tests")
class TestAPIResults:

    @pytest.mark.it("Inputs are not mutated")
    def test_inputs_not_mutated(self):
        test_search_term = "machine learning"
        copy_test_search_term = "machine learning"
        test_message_broker = "guardian_content"
        copy_test_message_broker = "guardian_content"
        test_date_from = "2023-01-01"
        copy_test_date_from = "2023-01-01"
        api_results(test_search_term, test_message_broker, test_date_from)
        assert test_search_term == copy_test_search_term
        assert test_message_broker == copy_test_message_broker
        assert test_date_from == copy_test_date_from

    @pytest.mark.it("Result is a list not exceeding 10 in length")
    def test_result_is_list_of_10_or_fewer(self):
        test_search_term = "machine learning"
        test_message_broker = "guardian_content"
        result = api_results(test_search_term, test_message_broker)
        assert len(result) <= 10

    @pytest.mark.it("Results contain correct fields")
    def test_results_contain_correct_fields(self):
        test_search_term = "machine learning"
        test_message_broker = "guardian_content"
        result = api_results(test_search_term, test_message_broker)
        for data in result:
            assert "webPublicationDate" in data.keys()
            assert "webTitle" in data.keys()
            assert "webUrl" in data.keys()

    @pytest.mark.it("Returns exact match results")
    def test_returns_exact_match_results(self):
        test_search_term = "machine learning"
        test_message_broker = "guardian_content"
        result = api_results(test_search_term, test_message_broker, exact_match=True)
        for data in result:
            assert "webPublicationDate" in data.keys()
            assert "webTitle" in data.keys()
            assert "webUrl" in data.keys()


# API tests
#   - check that response is 200 (i.e. valid API key)
#   - check orderBy is "newest"
#   - check that currentPage is 1
#   - check that length of results is 10
