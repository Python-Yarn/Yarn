#!/usr/bin/env python

import os
import sys
import getpass
import argparse
if sys.version_info.major == 2:
    from api import env, run, parallel
else:
    from yarn.api import env, run, parallel


def parse_host_list(host_list):
    return host_list.split(",")

def parse_yarn_file_path(yarnfile):
    return os.path.abspath(yarnfile)


def execute(tasks, command, run_parallel=False):
    @parallel
    def parallel_execution(*args, **kwargs):
        tasks = kwargs['tasks']
        command = args[0]
        try:
            tasks[command]()
        except KeyError:
            print(run(command))

    def serial_execution(*args, **kwargs):
        tasks = kwargs['tasks']
        command = args[0]
        try:
            tasks[command]()
        except KeyError:
            print(run(command))

    if run_parallel:
        parallel_execution(command, tasks=tasks)
    else:
        serial_execution(command, tasks=tasks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', '-H', type=parse_host_list, help="Host(s) separated by commas")
    parser.add_argument('--user', '-U', type=str, help="Username to use for connecting, defaults to current username")
    parser.add_argument('--parallel', '-P', dest="parallel", action="store_true", help="Run commands in parallel", default=False)
    parser.add_argument('--yarn-file', '-f', type=parse_yarn_file_path, help="Yarn file to use, defaults to yarnfile.py", default="./yarnfile.py")
    parser.add_argument('--warn-only', '-w', action="store_true", dest="warn_only", help="Do not halt upon finding an error", default=False)
    parser.add_argument('--quiet', '-q', action="store_true", dest="quiet", help="Suppress extra output.", default=False)
    parser.add_argument(nargs='+', dest='commands')

    args = parser.parse_args()
    tasks = dict()
    if os.path.isfile(args.yarn_file):
        directory, yarnfile = os.path.split(os.path.abspath(args.yarn_file))
        sys.path.insert(0, directory)
        tasks = vars(__import__(yarnfile.split(".")[0]))

    if args.user:
        env.user = args.user
    env.quiet = args.quiet
    env.warn_only = args.warn_only
    if args.hosts:
        for host in args.hosts:
            env.host_string = host
            if "@" in host:
                # This is to handle the ability to have username@hostname on the command line
                env.user, env.host_string = host.split("@")
            for command in args.commands:
                execute(tasks, command, args.parallel)
    else:
        for command in args.commands:
            execute(tasks, command, args.parallel)




if __name__ == '__main__':
    main()
