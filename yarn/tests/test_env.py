#!/usr/bin/env python

import os
import getpass
import unittest
from yarn.api import env

class TestEnv(unittest.TestCase):

    def test_env_port(self):
        env.host_port = 66
        assert env._port == 66 and env.host_port == 66

    def test_env_port_non_int(self):
        with self.assertRaises(AttributeError):
            env.host_port = "test"

    def test_env_port_bad_int(self):
        with self.assertRaises(AttributeError):
            env.host_port = 111111

    def test_env_user_autoset(self):
        assert env.user == getpass.getuser(), "Didn't get correct user.  FOUND: {} ENV: {}".format(env.user, os.environ["USERNAME"])

    def test_env_username_bad_input(self):
        with self.assertRaises(AttributeError):
            env.user = 12

    def test_env_password_bad_input(self):
        with self.assertRaises(AttributeError):
            env.password = 12
