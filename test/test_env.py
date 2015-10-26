#!/usr/bin/env python

import unittest
from yarn.api import env


class TestEnv(unittest.TestCase):

    def test_env_port(self):
        env.host_port = 66
        assert env._port == 66 and env.host_port == 66

    def test_env_port_non_int(self):
        def set_port_non_int():
            env.host_port = "test"
        self.assertRaises(AttributeError, set_port_non_int)

    def test_env_port_bad_int(self):
        def set_port_bad_int():
            env.host_port = 111111
        self.assertRaises(AttributeError, set_port_bad_int)