import unittest
from musicplayer.core.helpers import time

class TimeHelperTest(unittest.TestCase):
    def test_seconds_to_string(self):
        self.assertEqual(time.seconds_to_string(3), '00:03')
        self.assertEqual(time.seconds_to_string(60), '01:00')
        self.assertEqual(time.seconds_to_string(62), '01:02')
        self.assertEqual(time.seconds_to_string(78), '01:18')
        self.assertEqual(time.seconds_to_string(None), '00:00')
        self.assertEqual(time.seconds_to_string(0), '00:00')

