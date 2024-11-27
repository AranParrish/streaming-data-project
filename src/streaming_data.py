import boto3, logging, json
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
        logger.error("ClientError: Invalid secret name or region name")


API_KEY = get_api_key(secret=SECRET_NAME, region=REGION_NAME)


def streaming_data(search_term, message_broker, date_from=None):
    pass
