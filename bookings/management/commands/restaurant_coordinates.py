from django.core.management.base import BaseCommand

from bookings import restaurants_coordinates


class Command(BaseCommand):
    help = "Geocode restaurants and update DynamoDB table"

    def handle(self, *args, **options):
        # Delegate to the helper function in bookings/restaurants_coordinates.py
        # This keeps the logic testable and runnable both via manage.py and
        # directly as a script.
        self.stdout.write("Starting geocoding of restaurants...\n")
        restaurants_coordinates.restaurant_coordinates()
        self.stdout.write("Done.\n")