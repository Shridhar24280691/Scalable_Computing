import os
import time
import requests
import boto3
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

GOOGLE_GEOCODING_API_KEY = os.getenv("GOOGLE_GEOCODING_API_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=AWS_DEFAULT_REGION)
table = dynamodb.Table("Restaurants")


def geocode_restaurant(name, location):
    address = f"{name}, {location}, Ireland"
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_GEOCODING_API_KEY
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    status = data.get("status")

    if status == "OK" and data.get("results"):
        geometry = data["results"][0]["geometry"]["location"]
        return geometry["lat"], geometry["lng"]

    print(f"Geocoding failed for {name} ({location}). Status: {status}")
    return None, None


def restaurant_coordinates():
    response = table.scan()
    items = response.get("Items", [])

    for item in items:
        restaurant_id = item.get("restaurant_id")
        name = item.get("name")
        location = item.get("location")

        if not restaurant_id or not name or not location:
            print(f"Skipping item with missing fields: {item}")
            continue

        # Skip if coordinates already exist
        if "latitude" in item and "longitude" in item:
            print(f"Skipping {name} - coordinates already exist")
            continue

        print(f"Geocoding: {name}, {location}")

        lat, lng = geocode_restaurant(name, location)

        if lat is not None and lng is not None:
            table.update_item(
                Key={"restaurant_id": restaurant_id},
                UpdateExpression="SET latitude = :lat, longitude = :lng",
                ExpressionAttributeValues={
                    ":lat": Decimal(str(lat)),
                    ":lng": Decimal(str(lng))
                }
            )
            print(f"Updated {name} with lat={lat}, lng={lng}")
        else:
            print(f"Could not update {name}")

        # small delay to avoid hammering the API
        time.sleep(1)


if __name__ == "__main__":
    restaurant_coordinates()