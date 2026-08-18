import unittest
from unittest.mock import patch

from backend.routers import activities


class FakeActivitiesCollection:
    def __init__(self, documents):
        self.documents = documents
        self.last_query = None

    def find(self, query):
        self.last_query = query
        return [document.copy() for document in self.documents]


class GetActivitiesDifficultyTests(unittest.TestCase):
    def test_beginner_filter_includes_all_level_activities(self):
        fake_collection = FakeActivitiesCollection(
            [
                {"_id": "Programming Class", "difficulty": "Beginner"},
                {"_id": "Chess Club"}
            ]
        )

        with patch.object(activities, "activities_collection", fake_collection):
            result = activities.get_activities(difficulty="beginner")

        self.assertEqual(
            fake_collection.last_query,
            {
                "$or": [
                    {"difficulty": "Beginner"},
                    {"difficulty": {"$exists": False}}
                ]
            }
        )
        self.assertIn("Programming Class", result)
        self.assertIn("Chess Club", result)

    def test_all_levels_filter_only_queries_activities_without_difficulty(self):
        fake_collection = FakeActivitiesCollection([{"_id": "Chess Club"}])

        with patch.object(activities, "activities_collection", fake_collection):
            activities.get_activities(day="Monday", difficulty="all-levels")

        self.assertEqual(
            fake_collection.last_query,
            {
                "schedule_details.days": {"$in": ["Monday"]},
                "difficulty": {"$exists": False}
            }
        )

    def test_invalid_difficulty_filter_raises_http_error(self):
        fake_collection = FakeActivitiesCollection([])

        with patch.object(activities, "activities_collection", fake_collection):
            with self.assertRaises(activities.HTTPException) as context:
                activities.get_activities(difficulty="expert")

        self.assertEqual(context.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
