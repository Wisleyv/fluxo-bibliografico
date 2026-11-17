import unittest

from scripts.coletar_openalex_restrita_20261115 import validate_page


def page(ids, cursor="*", next_cursor="next", date="2024-01-01"):
    return {
        "request_cursor": cursor,
        "response": {
            "meta": {"count": 2, "next_cursor": next_cursor},
            "results": [{"id": identifier, "publication_date": date} for identifier in ids],
        },
    }


class ValidatePageTest(unittest.TestCase):
    def test_cursor_sequence_and_completion(self):
        seen = set()
        cursor = validate_page(page(["W1"]), "*", seen)
        cursor = validate_page(page(["W2"], cursor=cursor, next_cursor=None), cursor, seen)
        self.assertIsNone(cursor)
        self.assertEqual(seen, {"W1", "W2"})

    def test_duplicate_and_invalid_date_are_rejected(self):
        for sample, seen in (
            (page(["W1", "W1"]), set()),
            (page(["W1"]), {"W1"}),
            (page(["W2"], date="2026-11-09"), set()),
            (page(["W2"], cursor="wrong"), set()),
            (page([], next_cursor="next"), set()),
        ):
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                validate_page(sample, "*", seen)


if __name__ == "__main__":
    unittest.main()
