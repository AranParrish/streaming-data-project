import boto3, logging, json, requests
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "https://content.guardianapis.com/search?order-by=newest&q="
SECRET_NAME = "guardian_api_key"
REGION_NAME = "eu-west-2"


def get_api_key(secret, region):

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret)
        secret_value = json.loads(get_secret_value_response["SecretString"])
        return secret_value
    except ClientError as e:
        logger.error(e)


API_KEY = get_api_key(secret=SECRET_NAME, region=REGION_NAME)


def api_results(search_term, date_from, exact_match):

    search_results = []
    html_search_query = search_term.replace(" ", "%20")
    if exact_match:
        html_search_query = f'"{html_search_query}"'

    api_url = "".join(
        [BASE_URL, html_search_query, "&api-key=", API_KEY["guardian_api_key"]]
    )

    api_response = requests.get(api_url)

    if api_response.status_code == 200:
        json_response = json.loads(api_response.text)
        for result in json_response["response"]["results"]:
            selected_data = {
                "webPublicationDate": result["webPublicationDate"],
                "webTitle": result["webTitle"],
                "webUrl": result["webUrl"],
            }
            search_results.append(selected_data)
        logger.info(
            f"""Succesfully got results from guardian_api for '{search_term}'
         (Date from = {date_from}, Exact match = {exact_match})"""
        )
        return search_results

    if api_response.status_code == 401:
        logger.error("Invalid api key")

    else:
        json_response = json.loads(api_response.text)
        logger.error(json_response)


def create_queue(name):
    """
    Creates an Amazon SQS queue that persists for 3 days.

    :param name: The name of the queue. This is part of the URL assigned to the queue.
    :return: A Queue object that contains metadata about the queue and that can be used
             to perform queue operations like sending and receiving messages.
    """
    sqs = boto3.client("sqs")
    try:
        queue = sqs.create_queue(
            QueueName=name, Attributes={"MessageRetentionPeriod": "259200"}
        )
        logger.info(f"Created queue '{name}' with URL={queue['QueueUrl']}")
        print(queue["QueueUrl"])
    except ClientError as error:
        logger.error(f"Couldn't create queue named '{name}'. {error}.")
    else:
        return queue


def streaming_data(search_term, message_broker_id, date_from=None, exact_match=False):
    pass
