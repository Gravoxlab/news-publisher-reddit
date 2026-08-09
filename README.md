# news-publisher-reddit
Python AWS Lambda application for publishing original journalism to Reddit.
# News Publisher — Reddit Prototype

An AWS Lambda/Python prototype for distributing original journalism
and news analysis to Reddit.

## Current Status

This repository contains a **prototype** of the Reddit publishing
workflow.

The current Reddit publishing function is mocked. It **does not make
requests to Reddit's API and does not publish anything to Reddit**.

The prototype:

1. Reads eligible articles from Amazon DynamoDB.
2. Selects articles that have not already been processed for Reddit.
3. Builds a proposed Reddit title and post body.
4. Records the generated content in DynamoDB as `mock_published`.

## Intended Production Architecture

The planned production workflow is:

```text
News publishing workflow
        |
        v
Amazon DynamoDB
        |
        v
AWS Lambda / Python
        |
        v
Reddit OAuth / API
        |
        v
Reddit account
