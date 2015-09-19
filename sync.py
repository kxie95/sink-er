#!/usr/bin/env python3

import sys
import os
import json
import hashlib
import datetime
import time
import shutil

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

    # Update sync files for both folders
    update_sync_file(dir_one)
    update_sync_file(dir_two)

    # Merge directories
    merge_dirs(dir_one, dir_two)

def merge_dirs(dir_one, dir_two):
    dir_one_data = get_data_from_sync_file(dir_one + "/.sync")
    dir_two_data = get_data_from_sync_file(dir_two + "/.sync")

    for key in dir_one_data:
        file_data = dir_one_data[key]
        file_data_2 = dir_two_data[key]

        # Latest modification times
        mod_time = string_to_time(file_data[0][0])
        mod_time_2 = string_to_time(file_data_2[0][0])

        # TODO Same digest, different mod times
        if file_data[0][1] == file_data_2[0][1]:
            if not mod_time == mod_time_2:
                if mod_time < mod_time_2:
                    shutil.copyfile(dir_one+"/"+key, dir_two+"/"+key)
                    update_sync_file(dir_two)
                else:
                    shutil.copyfile(dir_two+"/"+key, dir_one+"/"+key)
                    update_sync_file(dir_one)

        # Different digest
        else:
            if mod_time_1 < mod_time_2:
                for x in range(file_data_2):
                    if file_data_2[x][0] == file_data[0][0]:
                        print('Replace old version with new')

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
                # Check if sync file contains info about the file
                if f in data:
                    latest_data = data[f][0][1]
                    latest_file_data = get_mod_and_hash(rel_path(directory, f))
                    # If latest hash is different, update sync file
                    if not latest_data == latest_file_data[1]:
                        data[f].insert(0, latest_file_data)

                # File not recorded in sync, add new entry
                else:
                    f_history = make_entry_for_file(f, directory)
                    data[f] = f_history

            # Check for deleted files
            for key in data:
                latest_data = data[key][0][1]
                print(latest_data)
                if key not in files:
                    if not latest_data == "deleted":
                        data[key].insert(0, get_mod_deleted(rel_path(directory, f)))

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

def get_mod_deleted(filename):
    """Returns array with last mod time at first index and deleted at second
    index.
    """
    return [modification_timestamp(filename), "deleted"]

def modification_timestamp(filename):
    """Get the last modified time in the format specified in the assignment."""
    last_mod_time = os.path.getmtime(filename)
    return time.strftime("%Y-%m-%d %H:%M:%S +1200", time.gmtime(last_mod_time))

def string_to_time(string):
    """Returns time object for a given string."""
    return time.strptime(string, "%Y-%m-%d %H:%M:%S +1200")

def get_files_in_dir(directory):
    """Gets files, excluding dirs, inside a given directory as a list."""
    files = []
    for f in os.listdir(directory):
        if not f.startswith('.'):
            files.append(f)
    return files

#-----------------------------
# JSON file related functions
#-----------------------------
def make_entry_for_file(filename, directory):
    """Makes a 2D array for a list of mod and hashes for a file."""
    file_path = rel_path(directory, filename)
    print(file_path)
    file_history = []
    file_history.append(get_mod_and_hash(file_path))
    return file_history

def get_data_from_sync_file(filename):
    """Returns JSON data from file as object."""
    with open(filename, "r+") as sync_f:
        return json.load(sync_f)

#==============================================================================
# ENTRY POINT

do_sync(sys.argv[1], sys.argv[2])
