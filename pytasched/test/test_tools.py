from unittest2 import TestCase
from pytasched.tools import get_duration, load_from_module, TickManager


class TestTools(TestCase):
    def test_get_duration(self):
        self.assertEqual(get_duration(days=1.5), 86400 * 1.5)
        self.assertEqual(get_duration(hours=1.5), 3600 * 1.5)
        self.assertEqual(get_duration(minutes=1.5), 60 * 1.5)
        self.assertEqual(get_duration(seconds=1.5), 1.5)
        self.assertEqual(get_duration(millis=1500.5), 1.5005)

        combined = get_duration(
            days=1.5,
            hours=1.5,
            minutes=1.5,
            seconds=1.5,
            millis=1.5
        )

        expected = (1.5 * 86400) + (1.5 * 3600) + (1.5 * 60) + 1.5 + 0.0015

        self.assertEqual(combined, expected)

    def test_load_from_module(self):
        tc = load_from_module("unittest2:TestCase")
        self.assertEqual(tc, TestCase)

    def test_TickManager(self):
        tm = TickManager(0.0001)
        self.assertTrue(tm.tick())
        self.assertTrue(tm.tick())
        tm.stop()
        self.assertFalse(tm.tick())
