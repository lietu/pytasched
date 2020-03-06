from __future__ import unicode_literals

from unittest import TestCase

from pytasched.tasks import Task


class TestTask(TestCase):
    def test_things(self):
        t = Task("test")
        self.assertEqual(t.id, None)
        self.assertEqual(t.task, "test")
        self.assertEqual(t.get_args(), [])
        self.assertEqual(t.get_kwargs(), {})

        t = Task("test", args=[1, 2, 3])
        self.assertEqual(t.get_args(), [1, 2, 3])

        t = Task("test", kwargs={"a": "b"})
        self.assertEqual(t.get_kwargs(), {"a": "b"})

        t = Task("test", args=[1, 2, 3], kwargs={"a": "b"})
        self.assertEqual(t.get_args(), [1, 2, 3])
        self.assertEqual(t.get_kwargs(), {"a": "b"})

        t = Task("test", wait=4)
        self.assertEqual(t.wait, 4)

        t = Task("test", days=1)
        self.assertEqual(t.wait, 86400)

        self.assertEqual(t.recurring, False)

        t = Task("test", recurring=True)
        self.assertEqual(t.recurring, True)

        t = Task("test", id="abc123")
        self.assertEqual(t.id, "abc123")
