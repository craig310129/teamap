#!/usr/bin/env python3
"""Static file server with Google Places / Geocoding proxy."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent


def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()
API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
PORT = int(os.environ.get("PORT", "3000"))
DEFAULT_RADIUS_METERS = 5000
MAX_RADIUS_METERS = 10000
SEARCH_KEYWORDS_ZH = ("手搖飲", "珍珠奶茶")
SEARCH_KEYWORDS_EN = ("bubble tea", "boba tea")

MESSAGES = {
    "zh-TW": {
        "missing_api_key": "尚未設定 GOOGLE_MAPS_API_KEY",
        "places_search_failed": "Google Places 搜尋失敗",
        "address_not_found": "找不到這個地址，請再試一次。",
        "place_details_failed": "無法取得店家詳細資訊",
        "unnamed_place": "未命名店家",
        "address_unavailable": "地址未提供",
        "missing_address": "請輸入地址",
        "missing_place_id": "缺少店家 ID",
        "missing_photo_param": "缺少照片參數",
        "invalid_params": "請求參數不正確",
        "google_http_failed": "Google API 連線失敗，請稍後再試。",
        "google_unreachable": "無法連線到 Google API。",
    },
    "en": {
        "missing_api_key": "GOOGLE_MAPS_API_KEY is not configured",
        "places_search_failed": "Google Places search failed",
        "address_not_found": "Could not find that address. Please try again.",
        "place_details_failed": "Could not load place details",
        "unnamed_place": "Unnamed place",
        "address_unavailable": "Address unavailable",
        "missing_address": "Please enter an address",
        "missing_place_id": "Missing place ID",
        "missing_photo_param": "Missing photo parameter",
        "invalid_params": "Invalid request parameters",
        "google_http_failed": "Google API connection failed. Please try again later.",
        "google_unreachable": "Could not reach Google API.",
    },
}


def parse_language(params: dict) -> str:
    raw = (params.get("lang") or ["zh-TW"])[0].strip().lower()
    return "en" if raw.startswith("en") else "zh-TW"


def msg(language: str, key: str) -> str:
    return MESSAGES.get(language, MESSAGES["zh-TW"]).get(key, MESSAGES["zh-TW"][key])


def search_keywords(language: str) -> tuple[str, ...]:
    return SEARCH_KEYWORDS_EN if language == "en" else SEARCH_KEYWORDS_ZH


def place_category(types: list[str], language: str) -> str:
    if language == "en":
        if "cafe" in types:
            return "Cafe"
        if "meal_takeaway" in types:
            return "Takeaway drinks"
        return "Drink shop"

    if "cafe" in types:
        return "咖啡廳"
    if "meal_takeaway" in types:
        return "外帶飲料"
    return "飲料店"


def clamp_radius(radius: int) -> int:
    return max(500, min(radius, MAX_RADIUS_METERS))


def google_request(url: str, language: str = "zh-TW") -> dict:
    if not API_KEY:
        raise RuntimeError(msg(language, "missing_api_key"))

    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    from math import asin, cos, radians, sin, sqrt

    earth_radius = 6371000
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return earth_radius * 2 * asin(sqrt(a))


def normalize_place(place: dict, origin_lat: float, origin_lon: float, language: str) -> dict:
    location = place["geometry"]["location"]
    lat = location["lat"]
    lon = location["lng"]
    opening_hours = place.get("opening_hours") or {}

    return {
        "placeId": place["place_id"],
        "name": place.get("name", msg(language, "unnamed_place")),
        "address": place.get("vicinity") or place.get("formatted_address") or msg(language, "address_unavailable"),
        "lat": lat,
        "lon": lon,
        "distance": haversine_meters(origin_lat, origin_lon, lat, lon),
        "rating": place.get("rating"),
        "ratingCount": place.get("user_ratings_total"),
        "isOpen": opening_hours.get("open_now"),
        "businessStatus": place.get("business_status"),
        "googleMapsUrl": f"https://www.google.com/maps/place/?q=place_id:{place['place_id']}",
    }


def nearby_search(
    lat: float,
    lon: float,
    keyword: str,
    radius_meters: int,
    language: str,
    page_token: str | None = None,
) -> tuple[list[dict], str | None]:
    params = {
        "location": f"{lat},{lon}",
        "radius": str(radius_meters),
        "keyword": keyword,
        "language": language,
        "key": API_KEY,
    }
    if page_token:
        params["pagetoken"] = page_token

    query = urllib.parse.urlencode(params)
    data = google_request(
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?{query}",
        language,
    )

    status = data.get("status")
    if status not in {"OK", "ZERO_RESULTS"}:
        message = data.get("error_message") or status or msg(language, "places_search_failed")
        raise RuntimeError(message)

    return data.get("results", []), data.get("next_page_token")


def collect_keyword_places(
    lat: float,
    lon: float,
    keyword: str,
    radius_meters: int,
    language: str,
) -> list[dict]:
    results, _page_token = nearby_search(lat, lon, keyword, radius_meters, language)
    places: list[dict] = []

    for place in results:
        place_id = place.get("place_id")
        if not place_id:
            continue

        normalized = normalize_place(place, lat, lon, language)
        if normalized["distance"] <= radius_meters:
            places.append(normalized)

    return places


def collect_nearby_places(lat: float, lon: float, radius_meters: int, language: str) -> list[dict]:
    seen: dict[str, dict] = {}
    keywords = search_keywords(language)

    with ThreadPoolExecutor(max_workers=len(keywords)) as executor:
        futures = [
            executor.submit(collect_keyword_places, lat, lon, keyword, radius_meters, language)
            for keyword in keywords
        ]

        for future in as_completed(futures):
            for place in future.result():
                seen[place["placeId"]] = place

    return sorted(seen.values(), key=lambda item: item["distance"])


def geocode_address(address: str, language: str) -> dict:
    params = urllib.parse.urlencode(
        {
            "address": address,
            "language": language,
            "region": "tw",
            "key": API_KEY,
        }
    )
    data = google_request(f"https://maps.googleapis.com/maps/api/geocode/json?{params}", language)

    if data.get("status") != "OK" or not data.get("results"):
        message = data.get("error_message") or msg(language, "address_not_found")
        raise RuntimeError(message)

    result = data["results"][0]
    location = result["geometry"]["location"]
    return {
        "lat": location["lat"],
        "lon": location["lng"],
        "label": result.get("formatted_address", address),
    }


def place_photo_proxy_url(photo_reference: str, max_width: int = 1200) -> str:
    query = urllib.parse.urlencode(
        {
            "ref": photo_reference,
            "maxwidth": str(max_width),
        }
    )
    return f"/api/place-photo?{query}"


def photo_proxy_from_name(photo_name: str, max_width: int = 1600) -> str:
    query = urllib.parse.urlencode(
        {
            "name": photo_name,
            "maxwidth": str(max_width),
        }
    )
    return f"/api/place-photo?{query}"


def fetch_google_menu_photos(place_id: str, classic_result: dict | None = None) -> tuple[list[str], str]:
    """Return all place photos from Google Places API (up to 10 per request)."""
    photos: list[str] = []
    seen: set[str] = set()
    google_maps_photos_uri = ""

    def add_photo(url: str, dedupe_key: str) -> None:
        if not url or dedupe_key in seen:
            return
        seen.add(dedupe_key)
        photos.append(url)

    try:
        request = urllib.request.Request(
            f"https://places.googleapis.com/v1/places/{place_id}",
            headers={
                "X-Goog-FieldMask": "photos,googleMapsLinks",
                "X-Goog-Api-Key": API_KEY,
            },
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        google_maps_photos_uri = (data.get("googleMapsLinks") or {}).get("photosUri", "")

        for photo in data.get("photos") or []:
            photo_name = photo.get("name")
            if photo_name:
                add_photo(photo_proxy_from_name(photo_name, 1600), photo_name)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError):
        pass

    if classic_result:
        for photo in classic_result.get("photos") or []:
            photo_reference = photo.get("photo_reference")
            if photo_reference:
                add_photo(place_photo_proxy_url(photo_reference, 1600), photo_reference)

    return photos, google_maps_photos_uri


def get_place_details(place_id: str, language: str) -> dict:
    fields = ",".join(
        [
            "name",
            "formatted_address",
            "formatted_phone_number",
            "website",
            "opening_hours",
            "rating",
            "user_ratings_total",
            "url",
            "types",
            "photos",
        ]
    )
    params = urllib.parse.urlencode(
        {
            "place_id": place_id,
            "fields": fields,
            "language": language,
            "key": API_KEY,
        }
    )
    data = google_request(f"https://maps.googleapis.com/maps/api/place/details/json?{params}", language)

    if data.get("status") != "OK" or not data.get("result"):
        message = data.get("error_message") or msg(language, "place_details_failed")
        raise RuntimeError(message)

    result = data["result"]
    opening_hours = result.get("opening_hours") or {}
    weekday_text = opening_hours.get("weekday_text") or []
    types = result.get("types") or []
    category = place_category(types, language)

    menu_photos, google_maps_photos_uri = fetch_google_menu_photos(place_id, result)
    if not google_maps_photos_uri:
        google_maps_photos_uri = result.get("url", "")

    return {
        "placeId": place_id,
        "name": result.get("name", msg(language, "unnamed_place")),
        "address": result.get("formatted_address", msg(language, "address_unavailable")),
        "phone": result.get("formatted_phone_number", ""),
        "website": result.get("website", ""),
        "rating": result.get("rating"),
        "ratingCount": result.get("user_ratings_total"),
        "isOpen": opening_hours.get("open_now"),
        "hoursToday": weekday_text[0] if weekday_text else "",
        "weekdayText": weekday_text,
        "googleMapsUrl": result.get("url") or f"https://www.google.com/maps/place/?q=place_id:{place_id}",
        "category": category,
        "menuPhotos": menu_photos,
        "googleMapsPhotosUri": google_maps_photos_uri,
    }


def reverse_geocode(lat: float, lon: float, language: str) -> str:
    params = urllib.parse.urlencode(
        {
            "latlng": f"{lat},{lon}",
            "language": language,
            "key": API_KEY,
        }
    )
    data = google_request(f"https://maps.googleapis.com/maps/api/geocode/json?{params}", language)

    if data.get("status") == "OK" and data.get("results"):
        return data["results"][0].get("formatted_address", f"{lat:.5f}, {lon:.5f}")

    return f"{lat:.5f}, {lon:.5f}"


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        language = "zh-TW"
        try:
            language = parse_language(params)

            if parsed.path == "/api/config":
                self.send_json(
                    {
                        "hasKey": bool(API_KEY),
                        "apiKey": API_KEY,
                        "radiusMeters": DEFAULT_RADIUS_METERS,
                        "maxRadiusMeters": MAX_RADIUS_METERS,
                    }
                )
                return

            if parsed.path == "/api/nearby":
                lat = float(params["lat"][0])
                lon = float(params["lon"][0])
                radius = clamp_radius(int(params.get("radius", [str(DEFAULT_RADIUS_METERS)])[0]))
                places = collect_nearby_places(lat, lon, radius, language)
                self.send_json({"places": places, "count": len(places), "radiusMeters": radius})
                return

            if parsed.path == "/api/geocode":
                address = params.get("address", [""])[0].strip()
                if not address:
                    raise RuntimeError(msg(language, "missing_address"))
                self.send_json(geocode_address(address, language))
                return

            if parsed.path == "/api/reverse-geocode":
                lat = float(params["lat"][0])
                lon = float(params["lon"][0])
                self.send_json({"label": reverse_geocode(lat, lon, language)})
                return

            if parsed.path == "/api/place-details":
                place_id = params.get("placeId", [""])[0].strip()
                if not place_id:
                    raise RuntimeError(msg(language, "missing_place_id"))
                self.send_json(get_place_details(place_id, language))
                return

            if parsed.path == "/api/place-photo":
                photo_reference = params.get("ref", [""])[0].strip()
                photo_name = params.get("name", [""])[0].strip()
                max_width = int(params.get("maxwidth", ["1200"])[0])

                if photo_name:
                    media_url = (
                        f"https://places.googleapis.com/v1/{photo_name}/media?"
                        + urllib.parse.urlencode(
                            {
                                "maxWidthPx": str(max_width),
                                "key": API_KEY,
                            }
                        )
                    )
                elif photo_reference:
                    media_url = (
                        "https://maps.googleapis.com/maps/api/place/photo?"
                        + urllib.parse.urlencode(
                            {
                                "maxwidth": str(max_width),
                                "photo_reference": photo_reference,
                                "key": API_KEY,
                            }
                        )
                    )
                else:
                    raise RuntimeError(msg(language, "missing_photo_param"))

                request = urllib.request.Request(media_url)
                with urllib.request.urlopen(request, timeout=20) as response:
                    image_data = response.read()
                    content_type = response.headers.get("Content-Type", "image/jpeg")

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "public, max-age=86400")
                self.end_headers()
                self.wfile.write(image_data)
                return
        except (KeyError, ValueError, IndexError):
            self.send_json({"error": msg(language, "invalid_params")}, status=400)
            return
        except RuntimeError as error:
            self.send_json({"error": str(error)}, status=400)
            return
        except urllib.error.HTTPError:
            self.send_json({"error": msg(language, "google_http_failed")}, status=502)
            return
        except urllib.error.URLError:
            self.send_json({"error": msg(language, "google_unreachable")}, status=502)
            return

        super().do_GET()

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        if str(args[0]).startswith("GET /api/"):
            super().log_message(format, *args)


def main() -> None:
    if not API_KEY:
        print("警告：尚未設定 GOOGLE_MAPS_API_KEY，請先建立 .env 或 export 環境變數。")
        print("可複製 .env.example 為 .env 並填入你的 Google API 金鑰。")

    server = ThreadingHTTPServer(("0.0.0.0", PORT), AppHandler)
    print(f"Server running at http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
