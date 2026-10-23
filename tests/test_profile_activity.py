"""Regressão: dashboard oficial GitHub com token read:user (sem rede)."""
import io
import json
import os
import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_activity_svg as activity


def fixture_data():
    start = date(2025, 10, 19)  # Domingo: 53 semanas, 371 dias
    weeks = []
    for w in range(53):
        days = []
        for i in range(7):
            day = start + timedelta(days=7 * w + i)
            days.append({
                "date": day.isoformat(),
                "contributionCount": (w + i) % 8,
            })
        weeks.append({"contributionDays": days})
    return {
        "startedAt": "2025-10-19T00:00:00Z",
        "endedAt": "2026-10-24T00:00:00Z",
        "totalCommitContributions": 2199,
        "totalIssueContributions": 18,
        "totalPullRequestContributions": 28,
        "totalPullRequestReviewContributions": 11,
        "totalRepositoriesWithContributedCommits": 17,
        "contributionCalendar": {
            "totalContributions": sum(
                d["contributionCount"]
                for week in weeks for d in week["contributionDays"]
            ),
            "weeks": weeks,
        },
    }


class GitHubActivityTests(unittest.TestCase):
    def test_render_valid_complete_calendar(self):
        svg = activity.render(
            fixture_data(), generated_at=datetime(2026, 10, 23, 18, 20,
                                                  tzinfo=timezone.utc)
        )
        self.assertIn("<svg", svg)
        self.assertIn("2199".replace("2199", "2.199"), svg)
        self.assertIn("REPOS COM COMMITS", svg)
        self.assertIn("23/10/2026 18:20 UTC", svg)
        self.assertTrue(svg.rstrip().endswith("</svg>"))
        self.assertNotIn("token-test", svg)

    def test_rejects_calendar_without_full_year(self):
        data = fixture_data()
        data["contributionCalendar"]["weeks"] = data["contributionCalendar"]["weeks"][:2]
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_rejects_negative_commit_count(self):
        data = fixture_data()
        data["totalCommitContributions"] = -1
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_rejects_string_as_daily_count(self):
        data = fixture_data()
        data["contributionCalendar"]["weeks"][0]["contributionDays"][0]["contributionCount"] = "999"
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_rejects_duplicate_calendar_day(self):
        data = fixture_data()
        days = data["contributionCalendar"]["weeks"][0]["contributionDays"]
        days[1]["date"] = days[0]["date"]
        with self.assertRaises(ValueError):
            activity.render(data)

    def test_rejects_naive_timestamp(self):
        with self.assertRaises(ValueError):
            activity.render(fixture_data(), generated_at=datetime(2026, 10, 23))

    def test_token_not_set(self):
        with patch.dict(os.environ, {"PROFILE_STATS_TOKEN": ""}):
            with self.assertRaises(ValueError):
                activity.fetch_activity()

    def test_token_must_match_profile(self):
        payload = {"data": {"viewer": {
            "login": "another-account",
            "contributionsCollection": fixture_data(),
        }}}
        with patch.object(activity, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())):
            with self.assertRaises(ValueError):
                activity.fetch_activity(token="token-test")

    def test_authentic_own_contributions(self):
        own = fixture_data()
        payload = {"data": {"viewer": {
            "login": "caiocezar-dev", "contributionsCollection": own,
        }}}
        with patch.object(activity, "urlopen", return_value=io.BytesIO(json.dumps(payload).encode())):
            self.assertEqual(activity.fetch_activity(token="token-test"), own)

    def test_graphql_error_must_fail(self):
        with patch.object(activity, "urlopen", return_value=io.BytesIO(
            json.dumps({"errors": [{"message": "denied"}]}).encode()
        )):
            with self.assertRaises(ValueError):
                activity.fetch_activity(token="token-test")

    def test_network_error_must_fail(self):
        with patch.object(activity, "urlopen", side_effect=URLError("offline")):
            with self.assertRaises(RuntimeError):
                activity.fetch_activity(token="token-test")

    def test_query_cannot_reveal_repo_identity(self):
        self.assertIn("viewer", activity.QUERY)
        self.assertNotIn("commitContributionsByRepository", activity.QUERY)
        self.assertNotIn("repository {", activity.QUERY)
        self.assertNotIn("message", activity.QUERY)


if __name__ == "__main__":
    unittest.main()
