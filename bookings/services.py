import json
import os
import boto3
import requests
from dotenv import load_dotenv

load_dotenv()

RECOMMENDATION_API_URL = os.getenv("RECOMMENDATION_API_URL")
CARD_API_URL = os.getenv("CARD_API_URL")
PUBLIC_API_URL = os.getenv("PUBLIC_API_URL")
SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

sqs_client = boto3.client("sqs", region_name=AWS_REGION)

class RecommendationAPIClient:
    def get_recommendations(self, payload):
        response = requests.post(
            f"{RECOMMENDATION_API_URL}/recommend",
            json=payload,
            timeout=20
        )
        response.raise_for_status()
        return response.json()

class CardAPIClient:
    def generate_card(self, payload):
        if not CARD_API_URL:
            return {}

        try:
            response = requests.post(
                CARD_API_URL,
                json=payload,
                timeout=30
            )
            if not response.ok:
                print("Card API status code:", response.status_code)
                print("Card API response body:", response.text)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print("Card API error:", e)
            return {}

class BookingQueueProducer:
    def send_booking_job(self, payload):
        if not SQS_QUEUE_URL:
            print("SQS_QUEUE_URL is not configured.")
            return None

        response = sqs_client.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(payload)
        )
        return response

class PublicAPIClient:
    def get_extra_details(self, restaurant_name):
        if not PUBLIC_API_URL:
            return {}

        try:
            response = requests.get(
                PUBLIC_API_URL,
                params={"q": restaurant_name},
                timeout=20
            )
            if response.status_code == 200:
                return response.json()
        except requests.RequestException as e:
            print("Public API error:", e)

        return {}