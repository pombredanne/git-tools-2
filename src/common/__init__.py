from __future__ import print_function

from hashlib import sha1
import sys
import os
import os.path
from subprocess import Popen, PIPE


BUFSIZE = 16 * 1024 * 1024


def message(msg):
    print(msg, file=sys.stderr)


def binary_in_path(binary):
    return any(os.path.exists(os.path.join(path, binary)) for path in set(os.environ["PATH"].split(':')))


def test_for_required_binaries(needed_binaries):
    found = [(binary, binary_in_path(binary)) for binary in needed_binaries]
    if not all(found_binary for _, found_binary in found):
        message("Certain additional binaries are required to run:")
        for binary, found_binary in found:
            message("\t{0}: {1}".format(binary, "Found" if found_binary else "Not found"))
        sys.exit(1)


def sha1_file(filename):
    with open(filename) as f:
        return sha1(f.read()).hexdigest()


def git_commit(fullpath, comment, dryrun, verbose, author=None):
    cmd = ["git", "commit", fullpath, "-m", "{0}: {1}".format(fullpath, comment)]
    if author:
        cmd += ["--author", author]

    if dryrun or verbose:
        message(" ".join(cmd))
    if not dryrun:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=BUFSIZE)
        _, errors = p.communicate()
        if p.returncode:
            raise Exception(errors)


def get_filelist(start_dir, recurse, ext=None):
    if recurse:
        file_list = [
            os.path.join(root, f)
            for root, _, files in os.walk(start_dir)
            for f in files
        ]
    else:
        file_list = os.listdir(start_dir)
    return file_list if not ext else [path for path in file_list if os.path.splitext(path)[1] == ext]


__all__ = [
    "message",
    "sha1_file",
    "test_for_required_binaries",
    "git_commit",
    "get_filelist",
]