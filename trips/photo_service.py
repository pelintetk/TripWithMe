
import requests


def search_place_photos(place_name, city):
    url = "https://commons.wikimedia.org/w/api.php"

    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f'filetype:bitmap "{place_name}" {city}',
        "gsrnamespace": 6,
        "gsrlimit": 5,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata",
        "iiurlwidth": 600,
        "format": "json",
    }

    headers = {
        "User-Agent": "TripWithMeStudentProject/1.0 (contact: pelintetik5@gmail.com)"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()
    pages = data.get("query", {}).get("pages", {})

    photos = []

    for page in pages.values():
        info = page.get("imageinfo", [{}])[0]
        metadata = info.get("extmetadata", {})

        photos.append({
            "title": page.get("title"),
            "url": info.get("thumburl", info.get("url")),
            "description_url": info.get("descriptionurl"),
            "license": metadata.get("LicenseShortName", {}).get("value"),
            "artist": metadata.get("Artist", {}).get("value"),
        })

    return photos

def save_place_photo(place):
    if place.photo_url:
        return True

    photos = search_place_photos(place.name, place.city)

    for photo in photos:
        if not photo.get("url"):
            continue

        place.photo_url = photo["url"]
        place.photo_source_url = photo.get("description_url") or ""
        place.photo_license = photo.get("license") or ""
        place.photo_artist = photo.get("artist") or ""

        place.save(update_fields=[
            "photo_url",
            "photo_source_url",
            "photo_license",
            "photo_artist",
        ])

        return True

    return False
