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

    #write_json_to_file('file1_2.txt', [[12, 12],[33,33]], from_sync_file)

    files = get_files_in_dir(from_dir)
    if not files:
        print('list is empty')
    for f in files:
        print(f)

    update_sync_file(from_dir)

def update_sync_file(directory):
    """Scans a given directory for files and updates its sync file."""

    # Get files in directory
    files = get_files_in_dir(directory)

    sync_file = directory + "/.sync"
    print(sync_file)

    # Load sync file
    with open(sync_file, "r+") as sync_f:
        data = json.load(sync_f)
        for f in files:
            if f in data:
                print('FOUND YOU')
    return files

def get_files_in_dir(directory):
    """Gets files, excluding dirs, inside a given directory as a list."""
    files = []
    for f in os.listdir(directory):
        if not f.startswith('.'):
            files.append(f)
    return files

def write_json_to_file(key, value, json_file):
    """Writes a key value pair to a json file."""
    with open(json_file, "a+") as f:
        json.dump({key: value}, f, indent=4, separators=(',', ': '))

do_sync(sys.argv[1], sys.argv[2])
