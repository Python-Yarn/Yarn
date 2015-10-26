#!/usr/bin/env python

import os
import sys
import getpass
import argparse
import importlib
from yarn.api import env
from yarn.api import run

def parse_host_list(host_list):
    return host_list.split(",")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', '-H', type=parse_host_list, help="Host(s) separated by commas")
    parser.add_argument('--user', '-U', type=str, help="Username to use for connecting, defaults to current username", default=getpass.getuser())
    parser.add_argument('--yarn-file', '-f', type=str, help="Yarn file to use, defaults to yarnfile.py", default="yarnfile.py")
    parser.add_argument(nargs='+', dest='commands')

    args = parser.parse_args() 

    if not args.hosts:
        raise Exception("Host list was empty")
    if not os.path.isfile(args.yarn_file):
        raise Exception("Yarn file {} couldn't be found".format(args.yarn_file))
    directory, yarnfile = os.path.split(os.path.abspath(args.yarn_file))
    sys.path.insert(0, directory)
    tasks = vars(__import__(yarnfile.split(".")[0]))
    env.user = args.user
    env.quiet = False
    for host in args.hosts:
        env.host_string = host
        for command in args.commands:
            try:
                tasks[command]()
            except KeyError:
                print(run(command))



if __name__ == '__main__':
    main()

    
