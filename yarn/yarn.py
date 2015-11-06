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
    """This is simply meant to parse the host list"""
    return host_list.split(",")


def parse_yarn_file_path(yarnfile):
    return os.path.abspath(yarnfile)

# This is set to parallel so that if there is a command line request for it,
# it can run in parallel.  This is due to the env.run_parallel setting.  If a
# developer wants to explicitly disallow parallel execution of a task, they can
# omit the @parallel call on any function they wish.
@parallel
def execute_task(*args, **kwargs):
    tasks, command = args
    if command in tasks:
        return tasks[command]()
    else:
        return print(run(command))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', '-H', type=parse_host_list,
                        help="Host(s) separated by commas.")
    parser.add_argument('--user', '-U', type=str,
                        help="Username to use for connecting, defaults to current username.")
    parser.add_argument('--parallel', '-P', dest="parallel", action="store_true",
                        help="Run commands in parallel.",
                        default=False)
    parser.add_argument('--port', '-p', dest="port", type=int,
                        help="What port to use for connecting to the remote host. Defaults to 22",
                        default=22)
    parser.add_argument('--yarn-file', '-f', type=parse_yarn_file_path,
                        help="Yarn file to use, defaults to yarnfile.py.",
                        default="./yarnfile.py")
    parser.add_argument('--warn-only', '-w', action="store_true", dest="warn_only",
                        help="Do not halt upon finding an error.",
                        default=False)
    parser.add_argument('--quiet', '-q', action="store_true", dest="quiet",
                        help="Suppress extra output.",
                        default=False)
    parser.add_argument(dest='commands', nargs=argparse.REMAINDER)

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
    env.run_parallel = args.parallel
    if args.hosts:
        for host in args.hosts:
            env.host_string = host
            if "@" in host:
                # This is to handle the ability to have username@hostname on the command line
                env.user, env.host_string = host.split("@")
            if ":" in env.host_string:
                # This is to handle the ability to have hostname:port on the command line
                host_string, port = env.host_string.split(":")
                env.host_string = host_string
                env.port = int(port)
            for command in args.commands:
                execute_task(tasks, command)
    else:
        for command in args.commands:
            execute_task(tasks, command)




if __name__ == '__main__':
    main()
