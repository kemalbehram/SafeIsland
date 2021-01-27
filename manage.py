import pathlib

import spurplus
from spurplus import SshShell

from typing import Union, Optional


from invoke import task

@task
def restart(c):
    print("Restarted the server")

@task
def start(c):
    print("Started from scratch")



def get_shell(host_alias="redtapi2") -> SshShell:

    if host_alias != "redtapi2":
        print(f"Host {host_alias} not yet supported")

    sh = spurplus.connect_with_retries(
        hostname='ec2-35-180-204-223.eu-west-3.compute.amazonaws.com',
        username='ubuntu',
        private_key_file='../telsiusin2/awsnode/AWSAlastriaIN2.pem',
        retries=5,
        connect_timeout=5,
        )
    return sh

def compare(sh: SshShell, local_path: Union[str, pathlib.Path], remote_path: Union[str, pathlib.Path]) -> int:

    diff = sh.directory_diff(local_path, remote_path)

    if len(diff.differing_files) > 0:
        print("\n   => Differing files")
        for f in diff.differing_files:
            print(f"  {f.name}")

    if len(diff.local_only_files) > 0:
        print("\n   => Local Only")
        for f in diff.local_only_files:
            print(f"  {f.name}")

    if len(diff.remote_only_files) > 0:
        print("\n   => Remote Only")
        for f in diff.remote_only_files:
            print(f"  {f.name}")

    num_diffs = len(diff.differing_files) + len(diff.local_only_files) + len(diff.remote_only_files)
    return num_diffs

def update_frontend(sh: SshShell):

    local_dir = "frontend"
    remote_dir = "/var/www/safeisland.hesusruiz.org/html"

    print("=== Compare frontend files before synchronization")
    print("=================================================")
    num_diffs = compare(sh, local_dir, remote_dir)
    if num_diffs == 0:
        print(f"   Local and remote are synched!")
        return

    print("Synchronize frontend files")
    sh.sync_to_remote(local_dir, remote_dir)

    print("Compare again to check synchronization")
    num_diffs = compare(sh, local_dir, remote_dir)
    if num_diffs == 0:
        print(f"   Local and remote are synched!")
        return


def update_backend(sh: SshShell):

    local_dir = "backend"
    remote_dir = "/home/ubuntu/backend"

    print("\n=== Compare backend files before synchronization")
    print("=================================================")
    num_diffs = compare(sh, local_dir, remote_dir)
    if num_diffs == 0:
        print(f"   Local and remote are synched!")
        return

    print("Synchronize backend files")
    sh.sync_to_remote(local_dir, remote_dir)

    print("Compare again to check synchronization")
    num_diffs = compare(sh, local_dir, remote_dir)
    if num_diffs == 0:
        print(f"   Local and remote are synched!")
        return

# Connect to the remote server
sh = get_shell(host_alias="redtapi2")

with sh:

    # Get remote user
    me = sh.whoami()

    # Check current directory
    result = sh.run(["pwd"],
        cwd="/home/ubuntu/backend",
        allow_error=False,
        stdout=None,
        stderr=None,
        encoding='utf-8',
        use_pty=False)

    print(f"Connected to REDTAPI2 as user {me} in directory {result.output}")

    # Restart the web server
    result = sh.run(["./restart"],
        cwd="/home/ubuntu/backend",
        allow_error=False,
        stdout=None,
        stderr=None,
        encoding='utf-8',
        use_pty=False)

    print(f"{result.output}")

#update_frontend(sh)

#update_backend(sh)

