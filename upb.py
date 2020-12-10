import pathlib

import spurplus
from spurplus import SshShell

from typing import Union, Optional

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

def compare(sh: SshShell, local_path: Union[str, pathlib.Path], remote_path: Union[str, pathlib.Path]):

    diff = sh.directory_diff(local_path, remote_path)

    if len(diff.differing_files) > 0:
        print("\n=> Differing files")
        for f in diff.differing_files:
            print(f"  {f.name}")

    if len(diff.local_only_files) > 0:
        print("\n=> Local Only")
        for f in diff.local_only_files:
            print(f"  {f.name}")

    if len(diff.remote_only_files) > 0:
        print("\n=> Remote Only")
        for f in diff.remote_only_files:
            print(f"  {f.name}")

def update_frontend(sh: SshShell):

    local_dir = "frontend"
    remote_dir = "/var/www/safeisland.hesusruiz.org/html"

    print("Compare frontend files before synchronization")
    compare(sh, local_dir, remote_dir)

    print("Synchronize frontend files")
    sh.sync_to_remote(local_dir, remote_dir)

    print("Compare again to check synchronization")
    compare(sh, local_dir, remote_dir)

def is_excluded():
    excluded_list = [
        ".pyc",

    ]

def update_backend(sh: SshShell):

    local_dir = "backend"
    remote_dir = "/home/ubuntu/backend"

    print("Compare backend files before synchronization")
    compare(sh, local_dir, remote_dir)

    print("Synchronize backend files")
    sh.sync_to_remote(local_dir, remote_dir)

    print("Compare again to check synchronization")
    compare(sh, local_dir, remote_dir)

def sync_to_remote(self,
                    local_path: Union[str, pathlib.Path],
                    remote_path: Union[str, pathlib.Path],
                    consistent: bool = True,
                    ) -> None:
    """
    Sync all the files beneath the ``local_path`` to ``remote_path``.

    Both local path and remote path are directories. If the ``remote_path`` does not exist, it is created. The
    files are compared with MD5 first and only the files whose MD5s mismatch are copied.

    Mind that the directory lists and the mapping (path -> MD5) needs to fit in memory for both the local path and
    the remote path.

    :param local_path: path to the local directory
    :param remote_path: path to the remote directory
    :param consistent: if set, writes to a temporary remote file first on each copy, and then renames it.
    :return:
    """
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-branches
    local_pth = local_path if isinstance(local_path, pathlib.Path) else pathlib.Path(local_path)

    remote_pth = remote_path if isinstance(remote_path, pathlib.Path) else pathlib.Path(remote_path)

    if not local_pth.exists():
        raise FileNotFoundError("Local path does not exist: {}".format(local_pth))

    if not local_pth.is_dir():
        raise NotADirectoryError("Local path is not a directory: {}".format(local_pth))

    dir_diff = self.directory_diff(local_path=local_pth, remote_path=remote_pth)

    # Create directories missing on the remote
    for rel_pth in dir_diff.local_only_directories:
        self.mkdir(remote_path=remote_pth / rel_pth)

    for rel_pths in [dir_diff.local_only_files, dir_diff.differing_files]:
        for rel_pth in rel_pths:

            # Check for exclusions
            

            self.put(
                local_path=local_pth / rel_pth,
                remote_path=remote_pth / rel_pth,
                create_directories=False,
                consistent=consistent)




sh = get_shell()
#update_frontend(sh)
update_backend(sh)