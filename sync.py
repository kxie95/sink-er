#!/usr/bin/env python3

import sys
import os
import json
import hashlib
import datetime
import time

def do_sync(arg_one, arg_two):
    """Check arguments and take appropriate action."""
    arg_one_is_dir = os.path.isdir(arg_one)
    arg_two_is_dir = os.path.isdir(arg_two)

    # Both arguments are invalid
    if not arg_one_is_dir and not arg_two_is_dir:
        print('Usage: sync directory1 directory2')

    # Both arguments are valid
    elif arg_one_is_dir and arg_two_is_dir:
        sync_dirs(arg_one, arg_two)

    # One argument is not a directory (create in sync_dirs)
    else:
        if arg_one_is_dir:
            # Arg one is directory
            sync_dirs(arg_one, arg_two)
        else:
            # Arg two is directory
            sync_dirs(arg_two, arg_one)

def sync_dirs(dir_one, dir_two):
    """Syncs from one directory to another directory."""

    # Make new directory if needed
    if not os.path.isdir(dir_two):
        os.makedirs(dir_two)
        print('Made new dir: ' + dir_two)

    # write_json_to_file('file1_2.txt', [[12, 12],[33,33]], from_sync_file)

    # Update sync files for both folders
    update_sync_file(dir_one)
    #update_sync_file(dir_two)

def update_sync_file(directory):
    """Scans a given directory for files and updates its sync file."""

    # Get files in directory
    files = get_files_in_dir(directory)

    # Create sync file if it doesn't exist
    sync_file = directory + "/.sync"
    print(sync_file)
    if not os.path.isfile(sync_file):
        open(sync_file, "w+").close()

    # Data for putting into JSON file
    data = None

    # If sync file is not empty, there is data.
    if os.stat(sync_file).st_size > 0:
        with open(sync_file, "r+") as sync_f:
            data = json.load(sync_f)
            for f in files:
                if f in data:
                    print('FOUND YOU')
                else:
                    write_json_to_file(f, update_file_history(f))

    # Sync file is empty, check if there are files in dir to add.
    else:
        # If no files to add, nothing to update so return.
        if not files:
            return

        data = dict()

        for f in files:
            f_history = make_entry_for_file(f, directory)
            data[f] = f_history

    # Place data in json (sync) file
    with open(sync_file, "r+") as f:
        json.dump(data, f, indent=4, separators=(',', ': '))

def rel_path(directory, filename):
    """Get relative path for a file."""
    rel_dir = os.path.relpath(directory)
    print(os.path.join(rel_dir, filename))
    return os.path.join(rel_dir, filename)

def update_file_history(file_history_list):
    """Adds arrays to history list for a file."""
    print('Update.')

#--------------------------------------
# Modification time and hash functions
#--------------------------------------
def get_mod_and_hash(filename):
    """Gets the latest modification date and creates sha256 hash for file.
    Returns an array with time at the first index and hash at the second index.
    """
    time_and_hash = []

    time_and_hash.append(modification_timestamp(filename))

    # Create digest from contents of file
    with open(filename, "r") as f:
        file_contents = f.read()
        m = hashlib.sha256(file_contents)
        time_and_hash.append(m.hexdigest())

    return time_and_hash

def modification_timestamp(filename):
    """Get the last modified time in the format specified in the assignment."""
    last_mod_time = os.path.getmtime(filename)
    return time.strftime("%Y-%m-%d %H:%M:%S +1200", time.gmtime(last_mod_time))

def get_files_in_dir(directory):
    """Gets files, excluding dirs, inside a given directory as a list."""
    files = []
    for f in os.listdir(directory):
        if not f.startswith('.'):
            files.append(f)
    return files

def make_entry_for_file(filename, directory):
    """Makes a 2D array for a list of mod and hashes for a file."""
    file_path = rel_path(directory, filename)
    print(file_path)
    file_history = []
    file_history.append(get_mod_and_hash(file_path))
    return file_history

do_sync(sys.argv[1], sys.argv[2])
