import unittest
from datetime import date
from review import review

CONTROL = [{"control_id": "A", "owner": "Platform", "max_age_days": "5"}]
AS_OF = date(2026, 11, 6)


def record(day, result="pass"):
    return dict(control_id="A", checked_on=day, result=result, reference="demo")


class ReviewTests(unittest.TestCase):
    def test_inclusive_age_limit(self):
        self.assertEqual(review(CONTROL, [record("2026-11-01")], AS_OF)[0][2], "current")
        self.assertEqual(review(CONTROL, [record("2026-10-31")], AS_OF)[0][2], "stale")

    def test_ignore_future_and_keep_latest(self):
        rows = [record("2026-11-07"), record("2026-10-30", "fail"), record("2026-10-01")]
        self.assertEqual(review(CONTROL, rows, AS_OF)[0][2], "failed")
        self.assertEqual(review(CONTROL, rows[:1], AS_OF)[0][2], "missing")

    def test_duplicate_observation(self):
        with self.assertRaises(ValueError):
            review(CONTROL, [record("2026-11-01")] * 2, AS_OF)

    def test_unknown_control(self):
        with self.assertRaises(ValueError):
            review(CONTROL, [dict(record("2026-11-01"), control_id="X")], AS_OF)
