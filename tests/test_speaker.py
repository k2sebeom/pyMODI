#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `modi` package."""

import modi
import unittest
import time

from modi.module.speaker import Speaker


class TestSpeaker(unittest.TestCase):
    """Tests for `Speaker` class."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.modi_inst = modi.MODI()
        self.speaker = self.modi_inst.speakers[0]

    def tearDown(self):
        """Tear down test fixtures, if any."""
        self.speaker.set_tune(0, 0)
        self.modi_inst.exit()
        time.sleep(1)

    def test_init(self):
        """Test initialization of speaker module"""
        self.assertIsInstance(self.speaker, Speaker)

    def test_basic_tune(self):
        """Test tune method with pre-defined inputs"""
        expected_values = (self.speaker.Scale.F_RA_6.value, 50)
        self.speaker.set_tune(*expected_values)
        # TODO: remove delaying function
        time.sleep(2)
        actual_values = self.speaker.set_tune()
        self.assertEqual(expected_values, actual_values)

    def test_custom_tune(self):
        """Test tune method with custom inputs"""
        expected_values = (2350, 50)
        self.speaker.set_tune(*expected_values)
        time.sleep(2)
        actual_values = self.speaker.set_tune()
        self.assertEqual(expected_values, actual_values)

    def test_get_frequency(self):
        """Test frequency method"""
        expected_frequncy = self.speaker.Scale.F_RA_6.value
        self.speaker.set_frequency(frequency_value=expected_frequncy)
        time.sleep(2)
        actual_frequency = self.speaker.set_frequency()
        self.assertEqual(expected_frequncy, actual_frequency)

    def test_get_volume(self):
        """Test volume method"""
        expected_volume = 70
        self.speaker.set_volume(expected_volume)
        time.sleep(2)
        actual_volume = self.speaker.set_volume()
        self.assertEqual(expected_volume, actual_volume)


if __name__ == "__main__":
    unittest.main()
