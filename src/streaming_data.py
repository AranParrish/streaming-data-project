import boto3, logging, json, requests
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_URL = "https://content.guardianapis.com/search?order-by=newest&q="
SECRET_NAME = "guardian_api_key"
SECRET_KEY = "guardian_api_key"


def get_api_key(secret) -> dict:
    """Retrieves input secret from AWS Secrets Manager

    Args:
        secret: AWS secret name (string)

    Returns:
        A dictionary with the key-value pairs of the secret(s)

    Error logs:
        ClientError message if unable to retrieve secret(s)
    """

    sm = boto3.client("secretsmanager")

    try:
        get_secret_value_response = sm.get_secret_value(SecretId=secret)
        secret_value = json.loads(get_secret_value_response["SecretString"])
        return secret_value
    except ClientError as e:
        logger.error(e)


API_KEY = get_api_key(secret=SECRET_NAME)[SECRET_KEY]


def api_results(search_term, date_from, exact_match) -> list:
    """Gets search term results from Guardian API

    Extracts the search results from Guardian API for the given search term.
    Limits results to those after a certain date if given.  Can run the search
    as an exact match or not.  Returns 10 most recent results.

    Args:
        search_term: The search term to be queried (string)
        date_from: Limit results to those after this date if truthy (None, string, datetime)
        exact_match: Whether to run the search term as an exact match (boolean)

    Returns:
        Search results with a dictionary giving the publication date, article title,
        and web url for each result(list)

    Error logs:
        Logs 'invalid api key' if server returns a 401 response.
        Logs the response text for all other errors.
    """

    search_results = []
    html_search_query = search_term.replace(" ", "%20")
    if exact_match:
        html_search_query = f'"{html_search_query}"'

    api_url = "".join([BASE_URL, html_search_query, "&api-key=", API_KEY])

    if date_from:
        api_url = "".join([api_url, "&from-date=", date_from])

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
    """Creates an Amazon SQS queue that persists for 3 days.

    Args:
        name: The name of the queue. This is part of the URL assigned to the queue.
    Returns:
        A Queue object that contains metadata about the queue and that can be used
        to perform queue operations like sending and receiving messages.

    Error logs:
        Returns AWS error log if attempted queue creation fails.
    """

    sqs = boto3.client("sqs")
    try:
        queue = sqs.create_queue(
            QueueName=name, Attributes={"MessageRetentionPeriod": "259200"}
        )
        logger.info(f"Created queue '{name}' with URL={queue['QueueUrl']}")
        return queue["QueueUrl"]
    except ClientError as error:
        logger.error(f"Couldn't create queue named '{name}'. {error}.")


def streaming_data(search_term, message_broker_id, date_from=None, exact_match=False):
    """Main function that stores search results from the Guardian in an AWS queue.

    Uses helper function "api_results" to obtain article results from the Guardian
    and adds these along with additional query info to be posted in JSON format to
    the message broker.  Then uses the helper function "create_queue" to generate an
    AWS SQS queue named "guardian_content_queue".  Finally, posts query result to the
    queue.

    Args:
        search_term: The article search term (string)
        message_broker_id: ID used to identify the search results by any consuming application (string)
        date_from (optional): Allows search results to be limited to those after this date (datetime or date_string)
        exact_match (optional): Determine whether to do an exact match of the search string (boolean)

    Returns:
        queue_url: The URL of the queue to enable consuming applications to retrieve the results

    Error logs:
        AWS ClientError if unable to add query results to the AWS SQS queue.
    """

    api_content = api_results(search_term, date_from, exact_match)
    query_results = {
        "ID": message_broker_id,
        "Search Term": search_term,
        "Date From": date_from,
        "Exact Match?": exact_match,
        "Results": api_content,
    }
    json_query_results = json.dumps(query_results)

    queue_url = create_queue("guardian_content_queue")
    sqs = boto3.client("sqs")
    try:
        sqs.send_message(QueueUrl=queue_url, MessageBody=json_query_results)
        logger.info(
            f"""Successfully added API results to queue for '{search_term}'
         (Date from = {date_from}, Exact match = {exact_match}) with the ID '{message_broker_id}'"""
        )
    except ClientError as error:
        logger.error(f"Failed to store API results in queue {queue_url}. {error}")

    return queue_url
