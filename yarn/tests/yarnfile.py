#!/usr/bin/env python

from yarn.api import cd
from yarn.api import env
from yarn.api import run
from yarn.api import put
from yarn.api import get
from yarn.api import sudo
from yarn.api import local


def test():
    # run("mkdir yarntesting")
    # put(__file__, "yarntesting/testfile.py")
    # with cd("yarntesting"):
    #     print(run("ls -1 *py"))
    #     run("echo $HOSTNAME >> {}".format(run("ls -1 *.py")))
    # get("yarntesting/testfile.py", "{}.testfile".format(env.host_string))
    # print("SUDO ENV")
    # print(sudo("env"))
    # print("SUDO IFCONFIG")
    # print(sudo("uname -r"))
    # print("ENV")
    # print(run("env"))
    print(local("env"))
