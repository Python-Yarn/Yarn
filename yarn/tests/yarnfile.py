#!/usr/bin/env python

from yarn.api import cd
from yarn.api import env
from yarn.api import run
from yarn.api import put
from yarn.api import get


def test():
    run("mkdir yarntesting")
    put(__file__, "yarntesting/testfile.py")
    with cd("yarntesting"):
        print(run("ls -1 *py"))
        run("echo $HOSTNAME >> {}".format(run("ls -1 *.py")))
    get("yarntesting/testfile.py", "{}.testfile".format(env.host_string))
