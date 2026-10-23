"""Testes locais e sem rede para o painel de atividade GitHub.

Execução: python3 -m unittest discover -s tests -p 'test_*.py'
"""
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_activity_svg as activity


def fixture_data():
    return {
        "totalCommitContributions": 234,
        "totalIssueContributions": 12,
        "totalPullRequestContributions": 18,
        "totalPullRequestReviewContributions": 8,
        "totalRepositoriesWithContributedCommits": 9,
        "contributionCalendar": {
            "totalContributions": 280,
            "weeks": [{
                "contributionDays": [
                    {"date": f"2026-10-{day:02d}", "contributionCount": day % 5}
                    for day in range(18, 25)
                ]
            }]
        }
    }


class ProfileActivityTests(unittest.TestCase):
    def test_render_produces_svg_with_personal_numbers(self):
        svg = activity.render(fixture_data())
        self.assertIn("<svg", svg)
        self.assertIn("234", svg)
        self.assertIn("280", svg)
        self.assertIn("REPOS COM COMMITS", svg)
        self.assertNotIn("private-repo-name", svg)
        self.assertTrue(svg.rstrip().endswith("</svg>"))

    def test_rejects_empty_calendar(self):
        data = fixture_data()
        data["contributionCalendar"]["weeks"] = []
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_rejects_negative_metrics(self):
        data = fixture_data()
        data["totalCommitContributions"] = -1
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_rejects_noninteger_daily_counts(self):
        data = fixture_data()
        data["contributionCalendar"]["weeks"][0]["contributionDays"][0]["contributionCount"] = "100"
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_missing_token_fails_without_network(self):
        with patch.dict(os.environ, {"PROFILE_STATS_TOKEN": ""}):
            with self.assertRaises(SystemExit):
                activity.fetch_activity()

    def test_rejects_token_from_other_user(self):
        payload = {
            "data": {
                "viewer": {"login": "wrong-user"},
                "user": {"contributionsCollection": fixture_data()},
            }
        }
        with patch.dict(os.environ, {"PROFILE_STATS_TOKEN": "test-only"}):
            with patch.object(activity, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())):
                with self.assertRaises(SystemExit):
                    activity.fetch_activity()

    def test_accepts_own_authorized_collection(self):
        data = fixture_data()
        payload = {
            "data": {
                "viewer": {"login": "caiocezar-dev"},
                "user": {"contributionsCollection": data},
            }
        }
        with patch.dict(os.environ, {"PROFILE_STATS_TOKEN": "test-only"}):
            with patch.object(activity, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())):
                self.assertEqual(activity.fetch_activity(), data)

    def test_rejects_graphql_errors_without_publish(self):
        payload = {"errors": [{"message": "invalid"}]}
        with patch.dict(os.environ, {"PROFILE_STATS_TOKEN": "test-only"}):
            with patch.object(activity, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())):
                with self.assertRaises(SystemExit):
                    activity.fetch_activity()


if __name__ == "__main__":
    unittest.main()
