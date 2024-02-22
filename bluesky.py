import requests
import json
import re
from typing import List, Dict
from datetime import datetime, timezone

from atproto import Client, client_utils

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
        self.bluesky_login()
        return

    def bluesky_login(self):
        """Start new login auth session."""
        # TODO: Add error handling
        self._bsky_session = Client()
        self._bsky_session.login(self._username, self._auth)
        return

    def bluesky_flutter(self, msg_text):
        """Post text message to existing session."""
        # TODO: Need to identify and refresh expired sessions
        msg_facets = self.parse_facets(msg_text)
        self._bsky_session.send_post(text=msg_text, facets=msg_facets)
        return True

    def parse_mentions(self, text: str) -> List[Dict]:
        spans = []
        # regex based on: https://atproto.com/specs/handle#handle-identifier-syntax
        mention_regex = rb"[$|\W](@([a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)"
        text_bytes = text.encode("UTF-8")
        for m in re.finditer(mention_regex, text_bytes):
            spans.append(
                {
                    "start": m.start(1),
                    "end": m.end(1),
                    "handle": m.group(1)[1:].decode("UTF-8"),
                }
            )
        return spans

    def parse_urls(self, text: str) -> List[Dict]:
        spans = []
        # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
        # tweaked to disallow some training punctuation
        url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
        text_bytes = text.encode("UTF-8")
        for m in re.finditer(url_regex, text_bytes):
            spans.append(
                {
                    "start": m.start(1),
                    "end": m.end(1),
                    "url": m.group(1).decode("UTF-8"),
                }
            )
        return spans

    # Parse facets from text and resolve the handles to DIDs
    def parse_facets(self, text: str) -> List[Dict]:
        facets = []
        for m in self.parse_mentions(text):
            resp = requests.get(
                "https://bsky.social/xrpc/com.atproto.identity.resolveHandle",
                params={"handle": m["handle"]},
            )
            # If the handle can't be resolved, just skip it!
            # It will be rendered as text in the post instead of a link
            if resp.status_code == 400:
                continue
            did = resp.json()["did"]
            facets.append(
                {
                    "index": {
                        "byteStart": m["start"],
                        "byteEnd": m["end"],
                    },
                    "features": [
                        {"$type": "app.bsky.richtext.facet#mention", "did": did}
                    ],
                }
            )
        for u in self.parse_urls(text):
            facets.append(
                {
                    "index": {
                        "byteStart": u["start"],
                        "byteEnd": u["end"],
                    },
                    "features": [
                        {
                            "$type": "app.bsky.richtext.facet#link",
                            # NOTE: URI ("I") not URL ("L")
                            "uri": u["url"],
                        }
                    ],
                }
            )
        return facets
