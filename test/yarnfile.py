#!/usr/bin/env python

from yarn.api import cd
from yarn.api import env
from yarn.api import run


def test():
    with cd("/usr/bin/"):
        print(run("ls -l pyth*"))
