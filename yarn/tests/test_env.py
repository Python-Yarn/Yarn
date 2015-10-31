#!/usr/bin/env python

import os
import unittest
from yarn.api import env

print(dir(env))

class TestEnv(unittest.TestCase):

    def test_env_port(self):
        env.host_port = 66
        assert env._port == 66 and env.host_port == 66

    def test_env_port_non_int(self):
        with self.assertRaises(AttributeError):
            env.host_port = "test"
#        def set_port_non_int():
#            env.host_port = "test"
#        self.assertRaises(AttributeError, set_port_non_int)

    def test_env_port_bad_int(self):
        with self.assertRaises(AttributeError):
            env.host_port = 111111
#        def set_port_bad_int():
#            env.host_port = 111111
#        self.assertRaises(AttributeError, set_port_bad_int)

    def test_env_user_autoset(self):
        assert env.user == os.environ["USERNAME"]

    def test_env_username_bad_input(self):
        with self.assertRaises(AttributeError):
            env.user = 12
#        def set_bad_username():
#            env.user = 12
#        self.assertRaises(AttributeError, set_bad_username)

    def test_env_password_bad_input(self):
        with self.assertRaises(AttributeError):
            env.password = 12
#        def set_bad_password():
#            env.password = 12
#        self.assertRaises(AttributeError, set_bad_password)
