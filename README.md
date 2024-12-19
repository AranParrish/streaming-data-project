# Streaming Data Backend Application

## Purpose

This backend application can be used to post search results from the Guardian in an AWS SQS queue.

The results stored are up to the 10 most recent articles.

## Prerequisites

1. Python
2. Make
3. A [Guardian API key](https://open-platform.theguardian.com/)
4. An AWS account

## Executing

1. Fork and clone this repo
3. Store your Guardian API key in your AWS Secrets Manager.  Assign the name of this secret to the global variable "SECRET_NAME".
4. Deploy the code as part of your application (e.g. as an AWS Lambda function).
5. Pass your search term and message broker ID to the streaming_data function.  You can optionally pass a date from argument (in the format YYYY-MM-DD) and/or an exact match argument (boolean).
6. This will get the search results using your Guardian API key and store them in an AWS SQS queue named "guardian_content_queue".
7. Any errors will be logged, as will info for each successful stage.