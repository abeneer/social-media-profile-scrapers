import argparse
import json
import time

import requests
from fake_headers import Headers


class Pinterest:
    @staticmethod
    def _endpoint() -> str:
        return "https://www.pinterest.com/resource/UserResource/get/"

    @staticmethod
    def _params(username: str) -> dict:
        data = {
            "options": {
                "field_set_key": "profile",
                "username": username,
                "is_mobile_fork": True,
            },
            "context": {},
        }

        return {
            "source_url": f"/{username}/",
            "data": json.dumps(data, separators=(",", ":")),
            "_": str(int(time.time() * 1000)),
        }

    @staticmethod
    def _make_request(username: str, debug: bool = False) -> requests.Response:
        headers = Headers(browser="chrome", os="mac").generate()
        headers.update(
            {
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-GB,en;q=0.9",
                "Referer": "https://www.pinterest.com/",
            }
        )

        url = Pinterest._endpoint()
        params = Pinterest._params(username)

        resp = requests.get(url, params=params, headers=headers, timeout=30)

        if debug:
            print("[DEBUG] URL:", resp.url)
            print("[DEBUG] Status:", resp.status_code)
            print("[DEBUG] Content-Type:", resp.headers.get("content-type"))
            print("[DEBUG] Snippet:", resp.text[:300])

        return resp

    @staticmethod
    def scrap(username: str, debug: bool = False) -> str:
        resp = Pinterest._make_request(username, debug=debug)

        if resp.status_code != 200:
            return json.dumps(
                {
                    "error": "Failed to fetch Pinterest data",
                    "status_code": resp.status_code,
                    "hint": "Pinterest may block automated requests (403/429). Use --debug to inspect.",
                }
            )

        try:
            payload = resp.json()
        except Exception:
            return json.dumps(
                {
                    "error": "Response was not JSON",
                    "status_code": resp.status_code,
                    "hint": "Pinterest might be serving HTML/captcha. Use --debug to see snippet.",
                }
            )

        data = payload.get("resource_response", {}).get("data", {})
        return json.dumps(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="username to search")
    parser.add_argument("--debug", action="store_true", help="print debug info")
    args = parser.parse_args()

    print(Pinterest.scrap(args.username, debug=args.debug))



