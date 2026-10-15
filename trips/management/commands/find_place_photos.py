
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
                for index, photo in enumerate(photos, start=1):
                    self.stdout.write(
                        f"\n{index}. {photo['title']}"
                    )
                    self.stdout.write(
                        f"   Photo: {photo['url']}"
                    )
                    self.stdout.write(
                        f"   Source: {photo['description_url']}"
                    )
                    self.stdout.write(
                        f"   License: {photo['license']}"
                    )

                choice = input(
                    "Choose a photo (1-5), or 0 to skip: "
                ).strip()

                if not choice.isdigit():
                    self.stdout.write("Invalid choice.")
                    continue

                choice = int(choice)

                if choice == 0:
                    self.stdout.write("Skipped.")
                    continue

                if choice > len(photos):
                    self.stdout.write("Invalid choice.")
                    continue

                selected_photo = photos[choice - 1]

                if not selected_photo["url"]:
                    self.stdout.write("Photo URL missing.")
                    continue

                place.photo_url = selected_photo["url"]
                place.photo_source_url = (
                    selected_photo["description_url"] or ""
                )
                place.photo_license = (
                    selected_photo["license"] or ""
                )
                place.photo_artist = (
                    selected_photo["artist"] or ""
                )

                place.save()

                self.stdout.write(
                    self.style.SUCCESS("Photo saved!")
                )
            else:
                self.stdout.write("No photo found.")