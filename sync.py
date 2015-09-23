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

    # Update sync files for both folders
    update_sync_file(dir_one)
    update_sync_file(dir_two)

    #----- Check sync file contents -----#
    dir_one_data = get_data_from_sync_file(dir_one + "/.sync")
    dir_two_data = get_data_from_sync_file(dir_two + "/.sync")

    # If both sync files empty
    if dir_one_data is None and dir_two_data is None:
        return

    # If one sync file is empty, copy files and update sync file
    if dir_one_data is None:
        copy_and_update_sync(dir_two, dir_one)
    elif dir_two_data is None:
        copy_and_update_sync(dir_one, dir_two)

    # ------------------------------------#

    # Merge directories
    merge_dirs(dir_one, dir_two)

def merge_dirs(dir_one, dir_two):

    dir_one_data = get_data_from_sync_file(dir_one + "/.sync")
    dir_two_data = get_data_from_sync_file(dir_two + "/.sync")

    # Go through keys in dir_one
    for key in dir_one_data:

        # Matching key not found
        if not key in dir_two_data.keys():
            copy_file_and_update(key, dir_two, dir_one)

    # Go through keys in dir_two
    for key in dir_two_data:

        # Matching key not found
        if not key in dir_one_data.keys():
            copy_file_and_update(key, dir_two, dir_one)

    # Go through keys in dir_one
    for file_1 in dir_one_data:

        for file_2 in dir_two_data:

            if file_1 == file_2:
                # If both deleted separately, nothing needs to be done
                if dir_one_data[file_1][0][1] == "deleted" and dir_two_data[file_1][0][1] == "deleted":
                    continue

                # If dir one file is deleted
                elif dir_one_data[file_1][0][1] == "deleted":
                    if any(dir_one_data[file_1][0] == x for x in dir_two_data[file_1]):
                        copy_file_and_update(file_1, dir_two, dir_one)
                    else:
                        os.remove(dir_two + "/" + file_1)
                        update_sync_file(dir_two)
                    continue

                # If dir two file is deleted
                elif dir_two_data[file_1][0][1] == "deleted":
                    if any(dir_two_data[file_1][0] == x for x in dir_one_data[file_1]):
                        copy_file_and_update(file_1, dir_one, dir_two)
                    else:
                        os.remove(dir_one + "/" + file_1)
                        update_sync_file(dir_one)
                    continue
        
#-Compare digests--------------------------------------------------------------------------
                    # If digests different
    if not dir_one_data[file_1][0][1] == dir_two_data[file_1][0][1]:

        found_earlier = False

        # If digest of one is contained in earlier version
        if any(dir_one_data[file_1][0][1] in subl for subl in dir_two_data[file_1][1:]):
                # One has been superseded, copy two to one
                copy_file_and_update(file_1, dir_two, dir_one)
                found_earlier = True

        if any(dir_two_data[file_1][0][1] in subl for subl in dir_one_data[file_1][1:]):
            # Two has been superseded, copy one to two
            copy_file_and_update(file_1, dir_one, dir_two)
            found_earlier = True

        # Completely unique digest found
        if not found_earlier:
            if is_older(dir_one_data[file_1][0][0], dir_two_data[file_1][0][0]) == -1:
                copy_file_and_update(file_1, dir_two, dir_one)
            else:
                copy_file_and_update(file_1, dir_one, dir_two)

        # If modified time not the same
        if dir_one_data[file_1][0][0] == dir_two_data[file_1][0][0]:
            if is_older(dir_one_data[file_1][0][0], dir_two_data[file_1][0][0]) == -1:
                copy_file_and_update(file_1, dir_two, dir_one)
            else:
                copy_file_and_update(file_1, dir_one, dir_two)

        # No file_1 found in other directory
        else:
            copy_file_and_update(file_1, dir_one, dir_two)


def copy_file_and_update(file_name, src_folder, dest_folder):
    full_file_name = os.path.join(src_folder, file_name)
    shutil.copy2(full_file_name, dest_folder)
    update_sync_file(dest_folder)

def copy_and_update_sync(src_folder, dest_folder):
    src_files = os.listdir(src_folder)
    for file_name in src_files:
        full_file_name = os.path.join(src_folder, file_name)
        if os.path.isfile(full_file_name) and not file_name.startswith("."):
            shutil.copy2(full_file_name, dest_folder)
    update_sync_file(dest_folder)

def update_sync_file(directory):
    """Scans a given directory for files and updates its sync file."""

    # Get files in directory
    files = get_files_in_dir(directory)

    # Create sync file if it doesn't exist
    sync_file = directory + "/.sync"
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
                if key not in files:
                    if not latest_data == "deleted":
                        data[key].insert(0, get_mod_deleted())

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

    # print("****UPDATED*****" + directory)
    # print_file_contents(sync_file)

def rel_path(directory, filename):
    """Get relative path for a file."""
    rel_dir = os.path.relpath(directory)
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
    with open(filename, "rb") as f:
        file_contents = f.read()
        m = hashlib.sha256(file_contents)
        time_and_hash.append(m.hexdigest())

    return time_and_hash

def get_mod_deleted():
    """Returns array with last mod time at first index and deleted at second
    index.
    """
    return [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +1200"), "deleted"]

def modification_timestamp(filename):
    """Get the last modified time in the format specified in the assignment."""
    last_mod_time = os.path.getmtime(filename)
    return time.strftime("%Y-%m-%d %H:%M:%S +1200", time.gmtime(last_mod_time))

def string_to_time(string):
    """Returns time object for a given string."""
    return time.strptime(string, "%Y-%m-%d %H:%M:%S +1200")

def is_older(time_x, time_y):
    """Returns true if x is older than y."""
    if string_to_time(time_x) < string_to_time(time_y):
        return -1
    elif string_to_time(time_x) > string_to_time(time_y):
        return 1
    return 0

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
    file_history = []
    file_history.append(get_mod_and_hash(file_path))
    return file_history

def get_data_from_sync_file(filename):
    """Returns JSON data from file as object."""
    if not os.stat(filename).st_size == 0:
        with open(filename, "r+") as sync_f:
            return json.load(sync_f)
    return None

def write_to_json_file(data, filename):
    with open(filename, "r+") as sync_f:
        json.dump(data, sync_f, indent=4, separators=(',', ': '))

def print_file_contents(filename):
    with open(filename, 'r') as f:
        print(f.read())
#==============================================================================
# ENTRY POINT

do_sync(sys.argv[1], sys.argv[2])
