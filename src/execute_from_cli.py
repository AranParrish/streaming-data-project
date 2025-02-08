import streaming_data, argparse


def execute_from_cli():
    """Runs the streaming_data application using the argparse module to pass in arguments from the command line.

    Creates an argument parser with help messages to guide the user through usage.
    Args:
        None.
    Returns:
        None, but successful execution results in the search query being stored in an AWS SQS queue.
    """

    parser = argparse.ArgumentParser(
        description="Post up to 10 post recent search results from the Guardian API in an AWS SQS queue"
    )
    parser.add_argument("search_term", help="Enter your search term (string)", type=str)
    parser.add_argument(
        "message_broker_id",
        help="The ID used to identify the search results in your AWS SQS queue (string)",
        type=str,
    )
    parser.add_argument(
        "-d",
        "--date_from",
        required=False,
        help="Optionally restrict search results from after this date (valid ISO 8601 format date string, such as YYYY-MM-DD)",
        type=str,
    )
    parser.add_argument(
        "-e",
        "--exact_match",
        required=False,
        help="Optional flag to do an exact match on the search term",
        action="store_true",
    )
    args = parser.parse_args()
    streaming_data.streaming_data(
        search_term=args.search_term,
        message_broker_id=args.message_broker_id,
        date_from=args.date_from,
        exact_match=args.exact_match,
    )


if __name__ == "__main__":
    execute_from_cli()
