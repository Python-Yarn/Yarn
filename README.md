# Yarn
A python2/3 library for host actuation via SSH.  It was inspired by Fabric, as will be evident by the similarity in commands and environment options.  I have used - and loved - Fabric for many years.  But, I needed python3 support; so I wrote my own minimal system.  


Yarn is intended as a minimal subset of common-use commands.  The current list of commands is:
* run - Run a command on the command line
* get - Download a file from a remote path
* put - Upload a file to a remote path

A single context manager (cd) is provided for running commands in a particular directory.

#### Module-Use Example:
```
from yarn.api import env, cd, run


env.host_string = '192.168.1.2'
env.user = 'yarn'
env.password = 'yarn_is_aw3some!'

with cd("/usr/bin"):
    print(run("ls -al pytho*"))

```


This example shows how simple the interface really is.  This would be the same as connecting to the host (192.168.1.2) with the user (yarn) and the password (yarn_is_aw3some!), then changing directory to ```/usr/bin``` and running ```ls -al pytho*```.  


Of course, you could have nested the 'cd' contextmanager thusly:

```
with cd("/usr"):
    with cd("bin"):
        print(run("ls -al pytho*"))

```

And it would have worked the same.


#### Yarnfile Example:
```
from yarn.api import env, cd, run


def test():
    with cd("/usr/bin"):
        print(run("ls -al pytho*"))

```

Then on the command line you would run:
```yarn --user yarn -H 192.168.1.2 test```

The output might look like:

```
[2015-10-23 16:30:05,119] DEBUG - run: RUNNING 'cd /usr/bin/ && ls -l pyth*' on '192.168.1.2'
lrwxrwxrwx 1 root root       9 Mar 16  2015 python -> python3.4
lrwxrwxrwx 1 root root       9 Mar 16  2015 python2 -> python2.7
-rwxr-xr-x 1 root root 3345416 Mar  1  2015 python2.7
lrwxrwxrwx 1 root root       9 Mar 16  2015 python3 -> python3.4
-rwxr-xr-x 1 root root 3709944 Mar  1  2015 python3.4

```

This would output the same as the previous module example.  Of note, is that the yarn command line does not take a password on the command line.  It will, however, query you for it.  This is done to keep a password out of your history.


### The Environment
The 'env' namespace contains several variables which can be set by the developer.
* host_string - (String) This is the host to which the system is going to connect.  DNS names (if dns is working) can be used here.
* host_port - (Integer) This is the port on the remove machine accepting incoming SSh connections.
* user - (String) This is the username to use when connecting to the host.
* password - (String) This is the password for the user.  If you have already copied an SSH key to the remote host, this is not required.
* key - (String) Path to RSA key file to use to authenticate with remote host.
* passphrase - (String) Password to use the key file.

### Using a RSA key to authenticate

```
from yarn.api import env, cd, run

env.host_string = "192.168.1.2"
env.host_port = 22
env.user = "root"
env.key = "/home/user/.ssh/id_rsa"
env.passphrase = "example_passphrase"

print(run("uname"))

```

Output:

```
[2015-10-26 12:27:00,865] DEBUG - run: RUNNING 'uname' on '192.168.1.2'
Linux
```

### Getting parallel
It is now possible to execute tasks in parallel.  You can do this via the ```@parallel``` decorator, or via the command line switch ```-P```.

#### Module-Use Example:
```
from yarn.api import env, cd, run, parallel


@parallel
def find_python():
    with cd("/usr/bin"):
        print(run("ls -al pytho*"))


env.host_string = '192.168.1.2'
env.user = 'yarn'
env.password = 'yarn_is_aw3some!'
find_python()
env.host_string = '192.168.1.3'
find_python()

```

This would, when executed, run the ```find_python``` function on both hosts in parallel.  Now a yarnfile example:
#### Yarnfile Example:
```
from yarn.api import env, cd, run
from random import randint

def find_python():
    # This is so that we will actually see that there was parallel execution
    # The second host in the queue may finish execution before the first 
    run("sleep {}".format(randint(2,10)))
    with cd("/usr/bin"):
        print(run("ls -al pytho*"))

```

Then on the command line you would run:

```yarn --user yarn -P -H 192.168.1.2,192.168.1.3 find_python```

If you wish to use parallel execution, but don't have the same username to use across all hosts, you can use username@hostname, So you could run:

```yarn -P -H yarn@192.168.1.2,yarn@192.168.1.3 find_python```

The output might look like:

```
[2015-10-30 21:55:01,429] DEBUG - run: 'sleep 5' on 'yarn@192.168.1.2'
[2015-10-30 21:55:01,442] DEBUG - run: 'sleep 3' on 'yarn@192.168.1.3'
[2015-10-30 21:55:04,633] DEBUG - run: 'cd /usr/bin/ && ls -l pyth*' on 'yarn@192.168.1.3'
lrwxrwxrwx 1 root root       9 Mar 16  2015 python -> python2.7
lrwxrwxrwx 1 root root       9 Mar 16  2015 python2 -> python2.7
-rwxr-xr-x 1 root root 3785928 Mar  1  2015 python2.7
[2015-10-30 21:55:06,583] DEBUG - run: 'cd /usr/bin/ && ls -l pyth*' on 'yarn@192.168.1.2'
lrwxrwxrwx 1 root root       9 Mar 16  2015 python -> python2.7
lrwxrwxrwx 1 root root       9 Mar 16  2015 python2 -> python2.7
-rwxr-xr-x 1 root root 3785928 Mar  1  2015 python2.7
```
