
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
