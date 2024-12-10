import pytest, boto3, logging, os, json
from moto import mock_aws
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError
from src.streaming_data import get_api_key, api_results, create_queue, streaming_data


@pytest.fixture(scope="function")
def test_api_results_inputs():
    return {"search_term": "machine learning", "date_from": None, "exact_match": False}


@pytest.fixture(scope="function")
def test_streaming_data_inputs():
    return {"search_term": "machine learning", "message_broker_id": "guardian_content"}


@pytest.fixture(scope="function")
def mock_aws_credentials():
    """Mocked AWS Credentials for moto."""

    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def mock_sqs_client(mock_aws_credentials):
    with mock_aws():
        yield boto3.client("sqs")


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

    @pytest.mark.it("Result is a list not exceeding 10 in length")
    def test_result_is_list_of_10_or_fewer(self, test_api_results_inputs):
        result = api_results(**test_api_results_inputs)
        assert len(result) <= 10

    @pytest.mark.it("Results contain correct fields")
    def test_results_contain_correct_fields(self, test_api_results_inputs):
        result = api_results(**test_api_results_inputs)
        for data in result:
            assert "webPublicationDate" in data.keys()
            assert "webTitle" in data.keys()
            assert "webUrl" in data.keys()

    @pytest.mark.it("Logs error for invalid api key")
    def test_logs_error_invalid_api_key(self, caplog, test_api_results_inputs):
        with patch("src.streaming_data.requests.get") as mock_request:
            mock_request.return_value.status_code = 401
            with caplog.at_level(logging.ERROR):
                api_results(**test_api_results_inputs)
            assert "Invalid api key" in caplog.text

    @pytest.mark.it("Logs HTTP error for other api responses")
    def test_logs_HTTP_error(self, caplog, test_api_results_inputs):
        with patch("src.streaming_data.requests.get") as mock_request:
            mock_request.return_value.status_code = 500
            mock_request.return_value.text = json.dumps("404 Not Found")
            with caplog.at_level(logging.ERROR):
                api_results(**test_api_results_inputs)
            assert "404 Not Found" in caplog.text


@pytest.mark.describe("Create queue function tests")
class TestCreateQueue:

    @pytest.mark.it("Creates queue with input name")
    def test_create_queue_with_input_name(self, mock_sqs_client):
        test_queue_name = "test_queue"
        result = create_queue(test_queue_name)
        assert test_queue_name in result["QueueUrl"]

    @pytest.mark.it("Creates queue with 3-day retention period")
    def test_create_queue_retention_period(self, mock_sqs_client):
        test_queue_name = "test_queue"
        expected_retention_period = str(60 * 60 * 24 * 3)
        test_queue_url = create_queue(test_queue_name)["QueueUrl"]
        queue_attributes = mock_sqs_client.get_queue_attributes(
            QueueUrl=test_queue_url, AttributeNames=["MessageRetentionPeriod"]
        )
        assert (
            queue_attributes["Attributes"]["MessageRetentionPeriod"]
            == expected_retention_period
        )

    @pytest.mark.it("Logs error if unable to create queue")
    def test_logs_error_unable_to_create_queue(self, mock_sqs_client, caplog):
        test_queue_name = "test_queue"
        with patch("boto3.client") as mock_sqs:
            mock_sqs.return_value.create_queue.side_effect = ClientError(
                {
                    "Error": {
                        "Code": "UnsupportedOperation",
                        "Message": "The operation is not supported.",
                    }
                },
                "ClientError",
            )
            with caplog.at_level(logging.ERROR):
                create_queue(test_queue_name)
                assert "Couldn't create queue" in caplog.text


# @pytest.mark.describe("Streaming data function tests")
# class TestStreamingData:
