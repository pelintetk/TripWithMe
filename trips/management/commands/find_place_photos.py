
import requests

from django.core.management.base import BaseCommand
from trips.models import Place
from trips.photo_service import search_place_photos


class Command(BaseCommand):
    help = "Find photo candidates for places"

    def add_arguments(self, parser):
        parser.add_argument("city", type=str)

    def handle(self, *args, **options):
        city = options["city"]

        places = Place.objects.filter(
            city__iexact=city,
            photo_url=""
        ).order_by("id")[:3]

        if not places:
            self.stdout.write("No places without photos found.")
            return

        for place in places:
            self.stdout.write(f"\nSearching: {place.name}")

            try:
                photos = search_place_photos(
                    place.name,
                    place.city
                )
            except requests.RequestException as error:
                self.stderr.write(f"Search failed: {error}")
                continue

            if photos:
                photo = photos[0]

                self.stdout.write(f"Candidate: {photo['title']}")
                self.stdout.write(f"URL: {photo['url']}")
                self.stdout.write(
                    f"Source: {photo['description_url']}"
                )
                self.stdout.write(f"License: {photo['license']}")
            else:
                self.stdout.write("No photo found.")
