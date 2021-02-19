import pathlib
from spur.results import ExecutionResult

import spurplus
from spurplus import SshShell

from typing import Union, Optional


from invoke import task
from invoke import Collection


def get_shell(host_alias="redtapi2") -> SshShell:

    if host_alias != "redtapi2":
        print(f"Host {host_alias} not yet supported")

    sh = spurplus.connect_with_retries(
        hostname='safeisland.hesusruiz.org',
        username='ubuntu',
        private_key_file='../telsiusin2/awsnode/AWSAlastriaIN2.pem',
        retries=5,
        connect_timeout=5,
        )
    return sh

# Connect to the remote server and update global variable
sh = get_shell(host_alias="redtapi2")


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
def restartx(c):
    """Restart NGINX
    """

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
    """Update the production frontend
    """

    if production:

        print("PRODUCTION!!")

        # Update locally the workbox files
        c.run("workbox generateSW workbox-config.js")

        local_dir = "frontend"
        remote_dir = "/var/www/safeisland.hesusruiz.org/html"

        print("\n==> Synchronize frontend files")
        sh.sync_to_remote(local_dir, remote_dir)

    else:

        local_dir = "backend/statictest"
        remote_dir = "/home/ubuntu/backend_test/statictest"

        print("\n==> Synchronize testing frontend files")
        sh.sync_to_remote(local_dir, remote_dir)





@task
def uback(c, production=False):
    """Update backend
    """

    if production:

        print("PRODUCTION!!")

        local_dir = "backend"
        remote_dir = "/home/ubuntu/backend"

        print("\n==> Synchronize backend files")
        sh.sync_to_remote(local_dir, remote_dir)

    else:

        local_dir = "backend"
        remote_dir = "/home/ubuntu/backend_test"

        print("\n==> Synchronize backend files")
        sh.sync_to_remote(local_dir, remote_dir)


@task
def restart(c, production=False):
    """Restart the gunicorn server
    """

    if production:

        print("PRODUCTION!!")

        result = sh.run(["pkill", "-HUP", "-F", "gunicorn.pid"],
            cwd="/home/ubuntu/backend",
            allow_error=True)

        if result.return_code != 0:
            print(f"==== Error =====\n{result.stderr_output}")
            return

        print(f"Gunicorn restarted")

    else:

        result = sh.run(["pkill", "-HUP", "-F", "gunicorn.pid"],
            cwd="/home/ubuntu/backend_test",
            allow_error=True)

        if result.return_code != 0:
            print(f"==== Error =====\n{result.stderr_output}")
            return

        print(f"Gunicorn restarted")


@task
def start(c, production=False):
    """Start the web server
    """

    if production:
        
        print("PRODUCTION!!")

        cmd_start = ["/home/ubuntu/.local/bin/gunicorn", "--daemon", "-p", "gunicorn.pid", "fmain:app", "-k",  "uvicorn.workers.UvicornWorker"]
        result = sh.run(cmd_start,
            cwd="/home/ubuntu/backend",
            allow_error=True)


        if result.return_code != 0:
            print(f"==== Error =====\n{result.stderr_output}")
            return

        print(f"{result.output}")

    else:

        cmd_start = ["/home/ubuntu/.local/bin/gunicorn", "--daemon", "-b", "127.0.0.1:8080", "-p", "gunicorn.pid", "fmain:app", "-k",  "uvicorn.workers.UvicornWorker"]
        result = sh.run(cmd_start,
            cwd="/home/ubuntu/backend_test",
            allow_error=True)


        if result.return_code != 0:
            print(f"==== Error =====\n{result.stderr_output}")
            return

        print(f"{result.output}")        


@task
def stop(c, production=False):
    """Stop the gunicorn server
    """

    if production:

        print("PRODUCTION!!")

        result = sh.run(["pkill", "-F", "gunicorn.pid"],
            cwd="/home/ubuntu/backend",
            allow_error=True)

        if result.return_code != 0:
            print(f"==== Error =====\n{result.stderr_output}")
            return

        print(f"{result.output}")

    else:

        result = sh.run(["pkill", "-F", "gunicorn.pid"],
            cwd="/home/ubuntu/backend_test",
            allow_error=True)

        if result.return_code != 0:
            print(f"==== Error =====\n{result.stderr_output}")
            return

        print(f"{result.output}")        



@task
def check(c):
    """Check if gunicorn is running
    """
    result = sh.run(["ps", "-C", "gunicorn"],
        cwd="/home/ubuntu/backend",
        allow_error=True)        

    if result.return_code == 1:
        print(f"Gunicorn not running")
    elif result.return_code == 0:
        print(f"{result.output}")
    else:
        print(f"Return code: {result.return_code}")

