import random
import time
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr


# DynamoDB configuration
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("news_articles")

# Publishing configuration
PLATFORM = "reddit"
MIN_DELAY = 10
MAX_DELAY = 20
MAX_ITEMS = 3


def mock_publish_reddit(article):
    """
    Prototype only.

    This function does NOT connect to Reddit.
    It builds the content that a future Reddit API
    integration could publish after approved OAuth/API access.
    """
    title = article.get("title", "")[:200]

    enriched = article.get("enriched_context", {}) or {}
    perspectives = enriched.get("perspectives", [])

    points = "\n".join(
        f"- {perspective}" for perspective in perspectives[:3]
    )

    selftext = (
        "An in-depth analysis on this topic just dropped.\n\n"
        "Key takeaways:\n\n"
        f"{points}\n\n"
        "What's your take?\n\n"
        "[Link to full article]"
    )

    return {
        "title": f"[Discussion] {title}",
        "selftext": selftext,
    }


def lambda_handler(event, context):
    """
    AWS Lambda entry point.

    The current implementation is a prototype. It reads eligible
    articles from DynamoDB and generates mock Reddit content.
    It does not make requests to Reddit.
    """

    time.sleep(random.uniform(0, 5))

    response = table.scan(
        FilterExpression=(
            Attr("master_draft").exists()
            & Attr("enriched_context").exists()
        )
    )

    all_articles = response.get("Items", [])

    articles = [
        article
        for article in all_articles
        if article.get("platform_posts", {})
        .get(PLATFORM, {})
        .get("status") != "published"
    ][:MAX_ITEMS]

    print(f"Processing {len(articles)} articles for {PLATFORM}")

    processed = 0

    for article in articles:
        article_id = article["article_id"]

        try:
            content = mock_publish_reddit(article)

            table.update_item(
                Key={"article_id": article_id},
                UpdateExpression="SET platform_posts.#plat = :val",
                ExpressionAttributeNames={
                    "#plat": PLATFORM,
                },
                ExpressionAttributeValues={
                    ":val": {
                        "status": "mock_published",
                        "content": content,
                        "processed_at": datetime.now(
                            timezone.utc
                        ).isoformat(),
                    }
                },
            )

            processed += 1

            print(
                f"MOCK publish to {PLATFORM}: "
                f"{article.get('title', '')[:80]}"
            )

        except Exception as exc:
            print(f"Error processing {article_id}: {exc}")

        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    print(f"Done: {processed} articles processed for {PLATFORM}")

    return {
        "statusCode": 200,
        "body": (
            f"{processed} articles processed "
            f"for {PLATFORM} (prototype mode)"
        ),
    }
