# Streaming Data Backend Application

## Purpose

This backend data application can be used to post search results from the Guardian API in an AWS SQS queue (a message broker).  It is intended to be used as a component in a data platform that includes a means for passing in the arguments for the Guardian API search query.

The entry point for the application is the function "streaming_data", which takes a search_term (string) and message_broker_id (string).  You can optionally pass the date_from argument (as a datetime or a valid ISO 8601 format date string) and/or the exact_match argument (boolean).  These are the inputs for the desired Guardian API search query to be published.

Returns the AWS SQS queue URL, which can be used by other applications to consume the results (or alternatively use the queue name "guardian_content_queue").

The results stored are up to the 10 most recent articles.  Data is persisted in the AWS SQS queue for up to 3 days.  Results are stored in the following JSON format:

{  
&nbsp;&nbsp;"ID": "string",  
&nbsp;&nbsp;"Search Term": "string",  
&nbsp;&nbsp;"Date From": "None or string",  
&nbsp;&nbsp;"Exact Match?": "boolean",  
&nbsp;&nbsp;"Results":  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\[  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webPublicationDate": "string"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "string"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "string"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]  
}

## Prerequisites

1. Python v3.11.1
2. A [Guardian API key](https://open-platform.theguardian.com/)
3. An AWS account

## Local enviornment setup

Before deploying this code, it is recommended that you take a local copy to make further developments as needed (e.g. to adapt the code for your particular usage) and to run the test suite to check for any errors.

1. Fork and clone this repo.
2. Ensure you have Make installed.
3. From the root directory, run "make requirements".  This will create a virtual environment with the necessary dependencies (compiled from the file "requirements.in" and then installed from "requirements.txt").
4. Next, run "make dev-setup".  This will install "bandit" and "safety" to do security tests, as well as "black" to ensure code is PEP8 compliant, and finally "coverage" to check test coverage.  Note that you will need a safety account (you should be prompted to register or login when first attempting to run the test suite, as detailed in stage 5 below).
5. To execute the full range of checks (security tests, PEP8 compliance, and the test suite), run "make run-checks".

The provided source code (stored in the "src" folder) and test suite (stored in the "test" folder) gives a test coverage of 100%.  If you make any further refinements to the source code, you should ensure these are tested prior to deployment.

## Cloud deployment

If you have already done the "Local environment setup", you can skip step 1 and instead deploy the application from your local environment.

1. Fork and clone this repo.
2. Store your Guardian API key in your AWS Secrets Manager under a secret named "api_keys" as a key-value pair with the key named "guardian_api_key" and your Guardian API key assigned to the value.  Ensure that your AWS credentials are configured in your local development environment (e.g. your "config" and "credentials" files are set in the directory "~/.aws").
3. Deploy the code as part of your application (e.g. as an AWS Lambda function).  The entry point is the function streaming_data, but you will need to include the remainder of the code as this function uses other helper functions to run as well as global variables.
4. Pass your search_term and message_broker_ID to the streaming_data function.  You can optionally pass the date_from argument (as a datetime or a valid ISO 8601 format date string) and/or the exact_match argument (boolean).

After successfully executing, your search results will be stored in an AWS SQS queue named "guardian_content_queue" with the passed in message broker ID.  Any errors will be logged, as will info on each successful stage.

## Example

The following example shows the expected data (as of 21 January 2025) stored in the AWS SQS queue when the inputs are passed to the "streaming_data" function after it has been deployed.  Note that the function itself returns the AWS SQS queue URL, which allows other consuming applications to retrieve the results.

Inputs:  
&nbsp;&nbsp;search_term = "machine learning",  
&nbsp;&nbsp;message_broker_id = "guardian_content",  
&nbsp;&nbsp;date_from = "2023-01-01",  
&nbsp;&nbsp;exact_match = True

AWS SQS queue contents:  
{  
&nbsp;&nbsp;"ID": "guardian_content",  
&nbsp;&nbsp;"Search Term": "machine learning",  
&nbsp;&nbsp;"Date From": None,
&nbsp;&nbsp;"Exact Match?": True,  
&nbsp;&nbsp;"Results":  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;\[  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webPublicationDate": "2025-01-20T14:21:52Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "Delivery apps urged to lift lid on ‘black-box algorithms’ affecting UK couriers"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/business/2025/jan/20/food-delivery-apps-ubereats-deliveroo-justeat-urged-to-reveal-how-algorithms-affect-uk-courierss-work"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2025-01-20T08:00:19Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "One drop at a time: how a new water sensor is helping to detect leaks and save you money"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/a-better-home-for-everyone-everywhere/2025/jan/20/one-drop-at-a-time-how-a-new-water-sensor-is-helping-to-detect-leaks-and-save-you-money"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2025-01-13T19:03:18Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "Ministers mull allowing private firms to make profit from NHS data in AI push"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/society/2025/jan/13/ministers-mull-allowing-private-firms-to-make-profit-from-nhs-data-in-ai-push"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2025-01-10T06:00:33Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "Streeting defends NHS use of private sector but says it must ‘pull its weight"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/society/2025/jan/10/wes-streeting-defends-nhs-use-private-sector-but-pull-its-weight"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},    
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2025-01-05T07:00:13Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "New year, new deal: the buyout boom poised to take over City lawyers’ lives"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/business/2025/jan/05/new-year-new-deal-the-buyout-boom-poised-to-take-over-city-lawyers-lives"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2024-12-28T06:00:32Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "Algorithm could help prevent thousands of strokes in UK each year"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/society/2024/dec/28/algorithm-could-help-prevent-thousands-of-strokes-in-uk-each-year"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2024-12-27T12:13:44Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "Listen up! Why 2024 was the year of the audiobook"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/books/2024/dec/27/year-of-the-audiobook-spotify-audible-ai"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2024-12-19T14:38:25Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "UK arts and media reject plan to let AI firms use copyrighted material"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/technology/2024/dec/19/uk-arts-and-media-reject-plan-to-let-ai-firms-use-copyrighted-material"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2024-12-18T18:06:38Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "UK politics: Waspi campaign accuses Starmer of misinformation over claim 90% of women knew pension age to rise – as it happened"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/politics/live/2024/dec/18/pmqs-starmer-badenoch-labour-tories-waspi-women"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
"webPublicationDate": "2024-12-17T13:47:34Z"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webTitle": "Amazon-hosted AI tool for UK military recruitment ‘carries risk of data breach’"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"webUrl": "https://www.theguardian.com/technology/2024/dec/17/amazon-hosted-ai-tool-for-uk-military-recruitment-carries-risk-of-data-breach"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}   
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]  
}