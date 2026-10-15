
import os
import requests

from dotenv import load_dotenv
from django.core.management.base import BaseCommand, CommandError

from trips.models import Place


class Command(BaseCommand):
    help = "Import places from Geoapify into the database"

    def add_arguments(self, parser):
        parser.add_argument("city", type=str)
        parser.add_argument("country", type=str)

    def handle(self, *args, **options):
        load_dotenv()

        api_key = os.getenv("GEOAPIFY_API_KEY")

        if not api_key:
            raise CommandError("Geoapify API key not found.")

        city = options["city"]
        country = options["country"]

        headers = {
            "User-Agent": "TripWithMeStudentProject/1.0 (contact: pelintetik5@gmail.com)"
        }

        try:
            location_response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "city": city,
                    "country": country,
                    "format": "json",
                    "limit": 1
                },
                headers=headers,
                timeout=20
            )
            location_response.raise_for_status()

            locations = location_response.json()

            if not locations:
                raise CommandError("City not found.")

            lat = locations[0]["lat"]
            lon = locations[0]["lon"]

            categories = {
                "catering.restaurant": "food",
                "catering.cafe": "cafe",
                "tourism.attraction": "attraction",
                "commercial.shopping_mall": "shopping",
            }

            created_count = 0

            for api_category, local_category in categories.items():
                response = requests.get(
                    "https://api.geoapify.com/v2/places",
                    params={
                        "categories": api_category,
                        "filter": f"circle:{lon},{lat},5000",
                        "bias": f"proximity:{lon},{lat}",
                        "limit": 10,
                        "apiKey": api_key,
                    },
                    timeout=20,
                )

                response.raise_for_status()

                for feature in response.json().get("features", []):
                    properties = feature.get("properties", {})

                    place_id = properties.get("place_id")
                    name = properties.get("name")

                    if not place_id or not name:
                        continue

                    _, created = Place.objects.get_or_create(
                        geoapify_id=place_id,
                        defaults={
                            "name": name,
                            "city": city,
                            "category": local_category,
                        },
                    )

                    if created:
                        created_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Imported {created_count} new places for {city}."
                )
            )

        except requests.RequestException as error:
            raise CommandError(f"API error: {error}")
