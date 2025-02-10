# Streaming Data Backend Application

## Purpose

This backend data application can be used to post search results from the Guardian API in an AWS SQS queue (a message broker).  It is intended to be used as a component in a data platform that includes a means for passing in the arguments for the Guardian API search query.

The entry point for the application is the function "streaming_data", which takes a search_term (string) and message_broker_id (string).  You can optionally pass the date_from argument (as a datetime or a valid ISO 8601 format date string) and/or the exact_match argument (boolean).  These are the inputs for the desired Guardian API search query to be published.

Returns the AWS SQS queue URL, which can be used by other applications to consume the results (or alternatively use the queue name "guardian_content_queue").

The results stored are up to the 10 most recent articles.  Data is persisted in the AWS SQS queue for up to 3 days.  Results are stored in the following JSON format:
```json
{  
    "ID": "string",  
    "Search Term": "string",  
    "Date From": "None or string",  
    "Exact Match?": "boolean",  
    "Results":  
        [  
            {  
                "webPublicationDate": "string",
                "webTitle": "string",
                "webUrl": "string"  
            },  
            ...  
        ]  
}
```

## Prerequisites

1. Python v3.11.1
2. A [Guardian API key](https://open-platform.theguardian.com/)
3. An AWS account

## Local enviornment setup

Before deploying this code, it is recommended that you take a local copy to make further developments as needed (e.g. to adapt the code for your particular usage) and to run the test suite to check for any errors.

1. Fork and clone this repo.
2. Ensure you have Make installed.
3. From the root directory, run the below command:
   
   ```sh
   make requirements
   ```
   
   This will create a virtual environment with the necessary dependencies (compiled from the file "requirements.in" and then installed from "requirements.txt").

4. Next, run:
   
   ```sh
   make dev-setup
   ```

   This will install "bandit" and "safety" to do security tests, as well as "black" to ensure code is PEP8 compliant, and finally "coverage" to check test coverage.  Note that you will need a safety account (you should be prompted to register or login when first attempting to run the test suite, as detailed in stage 5 below).
5. To execute the full range of checks (security tests, PEP8 compliance, and the test suite), run:

   ```sh
   make run-checks
   ```

The provided source code (stored in the file "src/streaming_data.py") and test suite (stored in the file "test/test_streaming_data") gives a test coverage of 100%.  If you make any further refinements to the source code, you should ensure these are tested prior to deployment.

## Command line deployment

To deploy the application from the command line on your local machine, you will need to have firstly followed the above steps on "local environment setup".  Then follow the below steps.

1. Store your Guardian API key in your AWS Secrets Manager under a secret named "api_keys" as a key-value pair with the key named "guardian_api_key" and your Guardian API key assigned to the value.  Ensure that your AWS credentials are configured in your local development environment (e.g. your "config" and "credentials" files are set in the directory "~/.aws").

2. Activate the virtual environment:

   ```sh
   source venv/bin/activate
   ```

3. Run the execute_from_cli.py script from the src folder with the below arguments:

   1. "search_term" (required) - Your search query. Provided as a string in quotes with terms separated by a single space.
   2. "message_broker_id" (required) - Your ID used to identify the results in the AWS SQS queue. Provided as a string enclosed in quotes.
   3. -d or --date_from "YYYY-MM-DD" (optional) - Restrict search results to those from a specific date.  Provided as a string enclosed in quotes in ISO 8601 format, such as YYYY-MM-DD.
   4. -e or --exact_match (optional flag) - Run the search query as an exact match.  This is a flag, so providing either -e or --exact_match will do the query as an exact match, omitting will not.
    
    Example usage:

    ```sh
    python src/execute_from_cli.py "machine learing" "guardian_content" --date_from "2025-01-01" -e
    ```
   
   After successfully executing, your search results will be stored in an AWS SQS queue named "guardian_content_queue" with the passed in message broker ID.

4. Once you have finished running your queries, you should finish by deactivating your virtual environment:

    ```sh
    deactivate
    ```

You can view the results by following the steps below:

1. Open the AWS console.
2. Navigate to the SQS service (e.g. by typing "SQS" into the search bar)
3. This should show your list of queues.  Click on the one named "guardian_content_queue".
4. Click on the button "Send and receive messages".
5. Under "Receive messages" you should be able to see that there is at least 1 message available (more will be available if you have run multiple search queries).
6. Click the button "Poll for messages".  This will allow you to view the messages in the console by then clicking on the ID listed (this is a unique ID generated by AWS, not to be confused with the "message_broker_id", which will be part of the JSON results within the message).

## Cloud deployment

If you have already done the "Local environment setup", you can skip step 1 and instead deploy the application from your local environment.

1. Fork and clone this repo.
2. Store your Guardian API key in your AWS Secrets Manager under a secret named "api_keys" as a key-value pair with the key named "guardian_api_key" and your Guardian API key assigned to the value.  Ensure that your AWS credentials are configured in your local development environment (e.g. your "config" and "credentials" files are set in the directory "~/.aws").
3. Deploy the code as part of your application (e.g. as an AWS Lambda function).  The entry point is the function streaming_data, but you will need to include the remainder of the code as this function uses other helper functions to run as well as global variables.
4. Pass your search_term and message_broker_ID to the streaming_data function.  You can optionally pass the date_from argument (as a datetime or a valid ISO 8601 format date string) and/or the exact_match argument (boolean).

After successfully executing, your search results will be stored in an AWS SQS queue named "guardian_content_queue" with the passed in message broker ID.  Any errors will be logged, as will info on each successful stage.