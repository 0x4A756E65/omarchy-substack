import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


BACKEND_PATH = Path(__file__).resolve().parents[1] / "substack_backend.py"
SPEC = importlib.util.spec_from_file_location("substack_backend", BACKEND_PATH)
backend = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(backend)


RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>Small Hours</title>
    <item>
      <title>A useful post &amp; its title</title>
      <link>https://smallhours.substack.com/p/useful-post</link>
      <guid>post-42</guid>
      <dc:creator>Robin Writer</dc:creator>
      <pubDate>Fri, 28 Aug 2026 13:03:10 GMT</pubDate>
      <description><![CDATA[<p>A clean <strong>description</strong>.</p>]]></description>
      <enclosure url="https://substackcdn.com/image.jpg" type="image/jpeg" />
    </item>
  </channel>
</rss>"""


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        backend.STATE_ROOT = root
        backend.STATE_FILE = root / "state.json"
        backend.CONFIG_FILE = root / "config.json"
        backend.STATE_LOCK = root / "state.lock"
        backend.CONFIG_LOCK = root / "config.lock"
        backend.DAEMON_LOCK = root / "daemon.lock"
        backend.REFRESH_REQUEST = root / "refresh.request"
        backend.ensure_dirs()
        backend.atomic_json(backend.STATE_FILE, backend.default_state())

    def tearDown(self):
        self.temporary.cleanup()

    def publication(self):
        return {
            "id": "smallhours",
            "name": "Small Hours",
            "author": "Robin Writer",
            "feed_url": "https://smallhours.substack.com/feed",
        }

    def test_subscription_response_becomes_canonical_rss(self):
        recognized, publications = backend.parse_publications(
            {
                "subscriptions": [{"publication_id": 42, "membership_state": "free_signup"}],
                "publications": [
                    {
                        "id": 42,
                        "name": "Small Hours",
                        "subdomain": "smallhours",
                        "custom_domain": "smallhours.example",
                        "author_name": "Robin Writer",
                        "logo_url": "https://cdn.example/small-hours.png",
                    }
                ],
            }
        )
        self.assertTrue(recognized)
        self.assertEqual(publications[0]["url"], "https://smallhours.example")
        self.assertEqual(publications[0]["feed_url"], "https://smallhours.substack.com/feed")
        self.assertEqual(publications[0]["logo_url"], "https://cdn.example/small-hours.png")

    def test_page_v2_marks_admin_publications_as_owned(self):
        recognized, publications = backend.parse_publications(
            {
                "subscriptions": [
                    {"publication_id": 42, "membership_state": "subscribed"},
                    {"publication_id": 99, "membership_state": "free_signup"},
                ],
                "publications": [
                    {"id": 42, "name": "My Essays", "subdomain": "my-essays"},
                    {"id": 99, "name": "Someone Else", "subdomain": "someone-else"},
                ],
                "publicationUsers": [
                    {"publication_id": 42, "role": "admin", "is_primary": True},
                ],
            }
        )
        self.assertTrue(recognized)
        self.assertEqual(
            [(publication["id"], publication["owned"]) for publication in publications],
            [("my-essays", True), ("someone-else", False)],
        )

    def test_wrapped_subscription_shape_and_publication_map_are_supported(self):
        recognized, publications = backend.parse_publications(
            {
                "result": {
                    "subscriptions": [{"publication_id": "42", "membership_state": "paid"}],
                    "publicationMap": {
                        "42": {
                            "id": "42",
                            "name": "Small Hours",
                            "subdomain": "smallhours",
                            "logo_url": "https://cdn.example/logo.png",
                        }
                    },
                }
            }
        )
        self.assertTrue(recognized)
        self.assertEqual(publications[0]["id"], "smallhours")
        self.assertEqual(publications[0]["membership"], "paid")

    def test_rss_metadata_is_safely_normalized(self):
        articles = backend.parse_feed(RSS, self.publication())
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "A useful post & its title")
        self.assertEqual(articles[0]["excerpt"], "A clean description.")
        self.assertEqual(articles[0]["publication"], "Small Hours")
        self.assertRegex(articles[0]["id"], r"^[0-9a-f]{24}$")

    def test_first_sync_seeds_and_second_sync_marks_only_new_article_unread(self):
        publication = self.publication()

        def seed(state):
            state["subscriptions"] = [
                {
                    **publication,
                    "seen_ids": [],
                    "last_checked": 0,
                    "next_poll": 0,
                }
            ]

        backend.mutate_state(seed)
        initial = backend.parse_feed(RSS, publication)
        self.assertEqual(backend.merge_feed("smallhours", initial, 100), [])
        self.assertEqual(backend.load_state()["unread_count"], 0)

        newer = dict(initial[0])
        newer["id"] = "a" * 24
        newer["title"] = "A genuinely new post"
        newer["published_ts"] += 100
        notified = backend.merge_feed("smallhours", [newer, initial[0]], 200)
        state = backend.load_state()
        self.assertEqual([item["title"] for item in notified], ["A genuinely new post"])
        self.assertEqual(state["unread_count"], 1)
        self.assertEqual(state["articles"][0]["title"], "A genuinely new post")

    def test_magic_link_is_restricted_to_substack_sign_in(self):
        self.assertTrue(backend.magic_link_allowed("https://substack.com/sign-in?token=header.payload.signature"))
        self.assertTrue(backend.magic_link_allowed("https://www.substack.com/sign-in?token=abc"))
        self.assertFalse(backend.magic_link_allowed("http://substack.com/sign-in?token=abc"))
        self.assertFalse(backend.magic_link_allowed("https://substack.example/sign-in?token=abc"))
        self.assertFalse(backend.magic_link_allowed("https://substack.com/library?token=abc"))
        self.assertFalse(backend.magic_link_allowed("https://substack.com/sign-in"))


if __name__ == "__main__":
    unittest.main()
