#!/usr/bin/env python3
"""
add_flight.py — add or update a tracked flight in the flight_pricing DynamoDB table.

Usage:
    python add_flight.py "DL 846" "https://www.google.com/travel/flights/booking?tfs=..."

This only touches the 'flight' and 'url' attributes. It never overwrites an
existing 'price' field, so re-running this for a flight that's already being
tracked (e.g. to update its URL) won't reset its baseline price.
"""

import sys
import boto3

TABLE_NAME = "flight_pricing"
REGION = "us-east-1"


def add_flight(flight_id: str, url: str):
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)

    # update_item with SET only touches 'url' — if the item already exists
    # (e.g. it has a 'price' from prior checks), that field is left alone.
    # If the item doesn't exist yet, update_item creates it.
    table.update_item(
        Key={"flight": flight_id},
        UpdateExpression="SET #u = :url",
        ExpressionAttributeNames={"#u": "url"},
        ExpressionAttributeValues={":url": url},
    )

    print(f"Added/updated flight '{flight_id}' with URL:\n  {url}")


def main():
    if len(sys.argv) != 3:
        print('Usage: python add_flight.py "FLIGHT_ID" "URL"')
        print('Example: python add_flight.py DL846 "https://www.google.com/travel/flights/booking?tfs=..."')
        sys.exit(1)

    flight_id = sys.argv[1]
    url = sys.argv[2]

    add_flight(flight_id, url)


if __name__ == "__main__":
    main()