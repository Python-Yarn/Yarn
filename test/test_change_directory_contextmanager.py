#!/usr/bin/env python

import os
import unittest
from yarn.api import env, cd


class TestChangeDirectory(unittest.TestCase):

    def test_empty_working_directory(self):
        assert env.working_directory == list()

    def test_simple_cd(self):
        with cd("testdir"):
            assert env.working_directory == ["testdir"]

    def test_nested_cd(self):
        with cd("first"):
            with cd("second"):
                with cd("third"):
                    assert env.working_directory == ["first", "second", "third"]

    def test_nested_popped(self):
        with cd("first"):
            with cd("second"):
                with cd("third"):
                    pass
            assert env.working_directory == ["first"]

