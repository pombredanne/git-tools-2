#!/usr/bin/env python
from subprocess import Popen, PIPE, STDOUT

from src.common import (
    message,
    sha1_file,
    get_filelist,
    test_for_required_binaries,

    git_commit,
)


BUFSIZE = 16 * 1024 * 1024

# These rules are listed in non-ascending order.
# I think it is better because
ERRORS = [
    ("W391", "blank line at end of file"),
    ("W291", "trailing whitespace"),
    ("W293", "blank line contains whitespace"),
    ("W191", "indentation contains tabs"),
    ("E101", "indentation contains mixed spaces and tabs"),
    # Never seen this rule applied
    # ("E111", "Reindent all lines."),

    # Line spacing
    ("E301", "expected 1 blank line, found 0"),
    ("E302", "line spacing between functions and classes"),
    ("E303", "linespacing between functions and classes"),
    ("E304", "Remove blank line following function decorator."),

    # Whitespace
    ("E211", "Remove extraneous whitespace."),
    ("E221", "Fix extraneous whitespace around keywords."),
    ("E222", "Fix extraneous whitespace around keywords."),
    ("E223", "Fix extraneous whitespace around keywords."),
    ("E224", "Remove extraneous whitespace around operator."),
    ("E225", "Fix missing whitespace around operator."),
    ("E226", "Fix missing whitespace around operator."),
    ("E227", "Fix missing whitespace around operator."),
    ("E228", "Fix missing whitespace around operator."),
    ("E231", "Add missing whitespace."),

    ("E261", "whitespace after inline comment"),
    ("E241", "Fix extraneous whitespace around keywords."),
    ("E242", "Remove extraneous whitespace around operator."),
    ("E251", "Remove whitespace around parameter '=' sign."),
    ("E261", "Fix spacing after comment hash."),
    ("E262", "Fix spacing after comment hash."),

    ("E203", "whitespace before colon"),
    ("E201", "whitespace around [ and ]"),
    ("E202", "whitespace around [ and ]"),

    ("E251", "unexpected whitespace around parameter equals"),
    ("E271", "Fix extraneous whitespace around keywords."),
    ("E272", "Fix extraneous whitespace around keywords."),
    ("E273", "Fix extraneous whitespace around keywords."),
    ("E274", "Fix extraneous whitespace around keywords."),

    # Multiple statements
    ("E701", "multiple statements on one line (colon)"),
    ("E702", "Put semicolon-separated compound statement on separate lines."),
    ("E703", "Put semicolon-separated compound statement on separate lines."),

    # Multiple imports
    ("E401", "multiple imports on one line"),

    # ("E501", "Try to make lines fit within --max-line-length characters."),
    ("E502", "the backslash is redundant between brackets"),
    ("W601", ".has_key() is deprecated, use 'in'"),
    ("W602", "Fix deprecated form of raising exception."),
    ("W603", "Replace <> with !=."),
    ("W604", "Replace backticks with repr()."),

    # These require --aggressive be sent to autopep8 command line
    ("E711", "comparison to None should be 'if cond is None:'"),
    ("E712", "comparison to True should be 'if cond is True:' or 'if cond:'"),

    # Never seen this rule applied to code.
    # ("E721", "Switch to use isinstance()."),

    # Indentation
    ("E121", "continuation line indentation is not a multiple of four"),

    # I don't like these rules because autopep8 does not really give good
    # transformations
    ("E122", "Add absent indentation for hanging indentation").
    ("E123", "closing bracket does not match indentation of opening bracket's line"),
    ("E124", "closing bracket does not match visual indentation"),
    ("E125", "continuation line does not distinguish itself from next logical line"),
    ("E126", "continuation line over-indented for hanging indent"),
    ("E127", "continuation line over-indented for visual indent"),
    ("E128", "continuation line under-indented for visual indent"),
]


def loop_params(file_list):
    for i, (error_no, error_comment) in enumerate(ERRORS, start=1):
        message("{2} of {3}: {0} {1}".format(
            error_no, error_comment, i, len(ERRORS)))
        for fullpath in file_list:
            hash_before = sha1_file(fullpath)
            yield (fullpath, hash_before, error_no, error_comment)


def run_command(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=STDOUT, bufsize=BUFSIZE)
    output, errors = p.communicate()
    if p.returncode:
        raise Exception(errors)
    else:
        return output


def run_autopep8(start_dir=".", ext=".py", recurse=True,
                 dryrun=False, verbose=False, autopep8=None, author=None):
    autopep8 = autopep8 or "autopep8"
    file_list = get_filelist(start_dir, recurse, ext)
    i = 0
    for fullpath, hash_before, error_no, error_comment in loop_params(file_list):
        cmd = [autopep8, "--in-place", "--verbose",
               "--select={0}".format(error_no), fullpath]
        if verbose or dryrun:
            message(" ".join(cmd))
        if not dryrun:
            output = run_command(cmd)
            if hash_before != sha1_file(fullpath):
                # I can't tell if autopep8 has modified a file from the return code,
                # so I do it the hard way...
                message(output)
                git_commit(
                    fullpath,
                    "{0} {1}".format(error_no, error_comment),
                    dryrun, verbose, author)
                i += 1
    message("# {0} files scanned/modified".format(i))


def option_parser():
    from optparse import OptionParser, make_option
    option_list = [
        make_option('-r', '--recurse', dest='recurse', action='store_true',
                    default=False, help='Recurse down directories from STARTDIR'),
        make_option('-e', '--ext', dest='extensions', action='store',
                    default=".py", help='Specify file extension to work on'),
        make_option('-d', '--dryrun', dest='dryrun', action='store_true',
                    default=False, help='Do dry run -- do not modify files'),
        make_option('-s', '--startdir', dest='startdir', action='store',
                    default=".", help='Specify directory to start in'),
        make_option('-v', '--verbose', dest='verbose',
                    action='store_true', default=False, help='Verbose output'),
        make_option('-a', '--autopep8', dest='autopep8', action='store',
                    default="autopep8", help='Specify path to autopep8 instance'),
        make_option('-u', '--author', dest='author',
                    action='store', help='Change git author'),
    ]
    return OptionParser(option_list=option_list)


def main():
    # Parse Command line options
    parser = option_parser()
    (o, _) = parser.parse_args()

    # Test for needed binaries. Exit if missing.
    needed_binaries = [
        "git",
        o.autopep8,
        "pep8"
    ]
    test_for_required_binaries(needed_binaries)

    # Do the business
    run_autopep8(
        start_dir=o.startdir, ext=o.extensions, recurse=o.recurse,
        dryrun=o.dryrun, verbose=o.verbose,
        autopep8=o.autopep8,
        author=o.author
    )


if __name__ == '__main__':
    main()