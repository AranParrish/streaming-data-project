import pytest, boto3, logging, os, json
from moto import mock_aws
from unittest.mock import Mock, patch
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

    @pytest.mark.it("Logs ResourceNotFoundException for invalid secret name")
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
        test_date_from = "2023-01-01"
        copy_test_date_from = "2023-01-01"
        test_exact_match = False
        copy_test_exact_match = False
        api_results(test_search_term, test_date_from, test_exact_match)
        assert test_search_term == copy_test_search_term
        assert test_date_from == copy_test_date_from
        assert test_exact_match == copy_test_exact_match

    @pytest.mark.it("Result is a list not exceeding 10 in length")
    def test_result_is_list_of_10_or_fewer(self):
        test_search_term = "machine learning"
        test_from_date = None
        test_exact_match = False
        result = api_results(test_search_term, test_from_date, test_exact_match)
        assert len(result) <= 10

    @pytest.mark.it("Results contain correct fields")
    def test_results_contain_correct_fields(self):
        test_search_term = "machine learning"
        test_from_date = None
        test_exact_match = False
        result = api_results(test_search_term, test_from_date, test_exact_match)
        for data in result:
            assert "webPublicationDate" in data.keys()
            assert "webTitle" in data.keys()
            assert "webUrl" in data.keys()

    @pytest.mark.it("Logs error for invalid api key")
    def test_logs_error_invalid_api_key(self, caplog):
        test_search_term = "machine learning"
        test_from_date = None
        test_exact_match = False
        with patch("src.streaming_data.requests.get") as mock_request:
            mock_request.return_value.status_code = 401
            with caplog.at_level(logging.ERROR):
                api_results(test_search_term, test_from_date, test_exact_match)
            assert "Invalid api key" in caplog.text

    @pytest.mark.it("Logs HTTP error for other api responses")
    def test_logs_HTTP_error(self, caplog):
        test_search_term = "machine learning"
        test_from_date = None
        test_exact_match = False
        with patch("src.streaming_data.requests.get") as mock_request:
            mock_request.return_value.status_code = 500
            mock_request.return_value.text = json.dumps("404 Not Found")
            with caplog.at_level(logging.ERROR):
                api_results(test_search_term, test_from_date, test_exact_match)
            assert "404 Not Found" in caplog.text


# API tests
#   - check that response is 200 (i.e. valid API key)
#   - check orderBy is "newest"
#   - check that currentPage is 1
#   - check that length of results is 10
