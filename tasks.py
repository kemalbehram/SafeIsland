import pathlib
import subprocess as sp

from spur.results import ExecutionResult

import spurplus
from spurplus import SshShell

from typing import Union, Optional

from invoke import task
from invoke import Collection

sh: SshShell = None

def get_shell(production=False) -> SshShell:

    global sh
    if sh is not None:
        return sh

    if production:
        hostname = "safeisland.hesusruiz.org"
        print("=== Operating in PRODUCTION!!")
    else:
        hostname = "safeislandtest.hesusruiz.org"
        print("=== Operating in DEVELOPMENT!!")

    sh = spurplus.connect_with_retries(
        hostname=hostname,
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

    num_diffs = len(diff.differing_files) + len(diff.local_only_files) + len(diff.remote_only_files)
    return num_diffs


################################################
# NGINX
################################################

@task
def restartx(c, production=False):
    """Restart NGINX
    """

    sh = get_shell(production)

    result = sh.run(["sudo", "systemctl", "restart", "nginx"],
        cwd="/home/ubuntu/backend",
        allow_error=True)

    if result.return_code != 0:
        print(f"==== Error =====\n{result.stderr_output}")
        return

    print(f"NGINX restarted")        


################################################
# PRODUCTION
################################################

@task
def ufront(c, production=False):
    """Update the frontend
    """

    sh = get_shell(production)

    if production:

        # Update locally the workbox files
        c.run("workbox generateSW workbox-config.js")

        local_dir = "frontend"
        remote_dir = "/var/www/safeisland.hesusruiz.org/html"

        print("\n==> Synchronize frontend files")
        sh.sync_to_remote(local_dir, remote_dir)

    else:

        local_dir = "backend/statictest"
        remote_dir = "/var/www/safeislandtest.hesusruiz.org/html"

        print("\n==> Synchronize testing frontend files")
        sh.sync_to_remote(local_dir, remote_dir)



@task
def uback(c, production=False):
    """Update backend
    """

    if production:
        local_dir = "backend/"
        remote_dir = "ubuntu@safeisland:/home/ubuntu/backend"
    else:
        local_dir = "backend/"
        remote_dir = "ubuntu@safeislandtest:/home/ubuntu/backend"

    rsync_args = ["rsync",
        "-a",   # same as -rlptgoD: recurse, preserve links, permissions, modification times, group, owner, special files
        "-u",   # skip files which exist on the destination and have a modified time that is newer than the source file
        "-z",   # compress when transmitting
        "-i",   # output a change-summary for all updates
        "--exclude-from=rsync_exclude.txt",
        local_dir,
        remote_dir
    ]
    result = sp.run(rsync_args, capture_output=False, text=True, check=False)

@task
def showdiff(c, production=False):
    """Update backend
    """

    if production:
        local_dir = "backend/"
        remote_dir = "ubuntu@safeisland:/home/ubuntu/backend"
    else:
        local_dir = "backend/"
        remote_dir = "ubuntu@safeislandtest:/home/ubuntu/backend"

    rsync_args = ["rsync",
        "-n",   # perform a trial run with no changes made
        "-a",   # same as -rlptgoD: recurse, preserve links, permissions, modification times, group, owner, special files
        "-z",   # compress when transmitting
        "-iv",   # output a change-summary for all updates
        "--delete",
        "--exclude-from=rsync_exclude.txt",
        local_dir,
        remote_dir
    ]
    result = sp.run(rsync_args, capture_output=False, text=True, check=False)


@task
def diff(c, production=False):
    """Display differences
    """

    if production:
        local_dir = "backend"
        remote_dir = "ubuntu@safeisland:/home/ubuntu/backend/"
    else:
        local_dir = "backend"
        remote_dir = "ubuntu@safeislandtest:/home/ubuntu/backend/"

    rsync_args = ["rsync",
        "-n",   # perform a trial run with no changes made
        "-a",   # same as -rlptgoD: recurse, preserve links, permissions, modification times, group, owner, special files
        "-u",   # skip files which exist on the destination and have a modified time that is newer than the source file
        "-z",   # compress when transmitting
        "-iv",   # output a change-summary for all updates
        "--exclude-from=rsync_exclude.txt",
        remote_dir,
        local_dir
    ]
    result = sp.run(rsync_args, capture_output=False, text=True, check=False)




@task
def restart(c, production=False):
    """Restart the gunicorn server
    """

    sh = get_shell(production)

    result = sh.run(["pkill", "-HUP", "-F", "gunicorn.pid"],
        cwd="/home/ubuntu/backend",
        allow_error=True)

    if result.return_code != 0:
        print(f"==== Error =====\n{result.stderr_output}")
        return

    print(f"Gunicorn restarted")



@task
def start(c, production=False):
    """Start the web server
    """

    sh = get_shell(production)

    cmd_start = ["/home/ubuntu/.local/bin/gunicorn", "--daemon", "-p", "gunicorn.pid", "fmain:app", "-k",  "uvicorn.workers.UvicornWorker"]
    result = sh.run(cmd_start,
        cwd="/home/ubuntu/backend",
        allow_error=True)


    if result.return_code != 0:
        print(f"==== Error =====\n{result.stderr_output}")
        return

    print(f"{result.output}")



@task
def stop(c, production=False):
    """Stop the gunicorn server
    """

    sh = get_shell(production)

    result = sh.run(["pkill", "-F", "gunicorn.pid"],
        cwd="/home/ubuntu/backend",
        allow_error=True)

    if result.return_code != 0:
        print(f"==== Error =====\n{result.stderr_output}")
        return

    print(f"{result.output}")



@task
def check(c, production=False):
    """Check if gunicorn is running
    """
    sh = get_shell(production)

    result = sh.run(["ps", "-C", "gunicorn"],
        cwd="/home/ubuntu/backend",
        allow_error=True)        

    if result.return_code == 1:
        print(f"Gunicorn not running")
    elif result.return_code == 0:
        print(f"{result.output}")
    else:
        print(f"Return code: {result.return_code}")

