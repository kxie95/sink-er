#!/usr/bin/env python3

import sys
import os
import json

def do_sync(arg_one, arg_two):
    """Check arguments and take appropriate action."""
    arg_one_is_dir = os.path.isdir(arg_one)
    arg_two_is_dir = os.path.isdir(arg_two)

    if not arg_one_is_dir and not arg_two_is_dir:
        print('Both args not dir.')
    elif arg_one_is_dir and arg_two_is_dir:
        sync_dirs(arg_one, arg_two)  
    else:
        if arg_one_is_dir:
            print('Arg1 is dir.')
            sync_dirs(arg_one, arg_two)
        else:
            print('Arg2 is dir')
            sync_dirs(arg_two, arg_one)

def sync_dirs(from_dir, to_dir):
    """Syncs from one directory to another directory."""

    # Make new directory if needed
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
        print('Made new dir: ' + to_dir)

    # Check if directories contain sync files
    from_sync_file = from_dir + "/.sync"
    to_sync_file = from_dir + "/.sync"

    # with open(from_dir + "/.sync", "a+") as f:
    #     data = {
    #         "file1_2.txt": [
    #             [
    #              "2015-08-26 16:53:53 +1200",
    #              "deleted"
    #             ],
    #             [
    #             "2015-08-26 16:52:56 +1200",
    #             "a8299b688d515f86123fcb56b797f9a10988d5c359f3b99734ca43f67913887d"
    #             ]
    #         ]
    #     }    
    #     json.dump(data, f, indent=4)

    files = get_files_in_dir(from_dir)
    if not files:
        print('list is empty')
    for f in files:
        print(f)

def update_sync_file(directory):
    """Scans a given directory for files and updates its sync file."""
    print(directory)

def get_files_in_dir(directory):
    """Gets files, excluding dirs, inside a given directory as a list."""
    files = []
    for f in os.listdir(directory):
        if not f.startswith('.'):
            files.append(f)
    return files

do_sync(sys.argv[1], sys.argv[2])
