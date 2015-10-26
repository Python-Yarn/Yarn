#!/usr/bin/env python

import os
import sys
import getpass
import argparse
import importlib
from yarn.api import env


def parse_host_list(host_list):
    return host_list.split(",")

parser = argparse.ArgumentParser()
parser.add_argument('--hosts', '-H', type=parse_host_list, help="Host(s) separated by commas")
parser.add_argument('--user', '-U', type=str, help="Username to use for connecting, defaults to current username", default=getpass.getuser())
parser.add_argument('--yarn-file', '-f', type=str, help="Yarn file to use, defaults to yarnfile.py", default="yarnfile.py")
parser.add_argument(nargs='+', dest='commands')

args = parser.parse_args() 

if __name__ == '__main__':
    if not args.hosts:
        raise Exception("Host list was empty")
    if not os.path.isfile(args.yarn_file):
        raise Exception("Yarn file {} couldn't be found".format(args.yarn_file))
    sys.path.append(os.path.dirname(os.path.abspath(args.yarn_file)))
    import yarnfile
    env.user = args.user
    env.quiet = False
    for host in args.hosts:
        env.host_string = host
        try:
            [eval("yarnfile.{}()".format(a)) for a in args.commands]
        except AttributeError:
            print("No command called '{}' in the yarnfile".format(",".join(args.commands)))


