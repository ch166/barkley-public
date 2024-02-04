#

import requests
import json
from datetime import datetime, timezone

# from bsky_bridge import BskySession
# from bsky_bridge import post_text
# from bsky_bridge import post_image

class BlueSky:
    _username = None
    _auth = None
    _bsky_session = None

    def __init__(self, user_name, user_auth):
        """Setup new session and record userid/pass details."""
        self._username = user_name
        self._auth = user_auth
        # self._bsky_session = BskySession(self._username, self._auth)

        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.server.createSession",
            json={"identifier": self._username, "password": self._auth},
        )
        resp.raise_for_status()
        self._bsky_session = resp.json()

        return

    def bluesky_flutter(self, msg_text, url_start, url_end, url_string):
        """Post text message to existing session."""
        # TODO: Need to refresh expired sessions

        # print(session["accessJwt"])

        # Fetch the current time
        # Using a trailing "Z" is preferred over the "+00:00" format
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Required fields that each post must include
        post_json = {
            "$type": "app.bsky.feed.post",
            "text": msg_text,
            "createdAt": now,
            "facets": [
                {
                    "index": {"byteStart": url_start, "byteEnd": url_end},
                    "features": [
                        {"$type": "app.bsky.richtext.facet#link", "uri": url_string}
                    ],
                }
            ],
        }

        resp = requests.post(
            "https://bsky.social/xrpc/com.atproto.repo.createRecord",
            headers={"Authorization": "Bearer " + self._bsky_session["accessJwt"]},
            json={
                "repo": self._bsky_session["did"],
                "collection": "app.bsky.feed.post",
                "record": post_json,
            },
        )
        print(json.dumps(resp.json(), indent=2))
        resp.raise_for_status()
        # print(response)

        return True
