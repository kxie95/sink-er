#!/usr/bin/env python

import sys
import os


def do_sync(arg_one, arg_two):
    """Check arguments and take appropriate action."""
    arg_one_is_dir = os.path.isdir(arg_one)
    arg_two_is_dir = os.path.isdir(arg_two)

    if not arg_one_is_dir and not arg_two_is_dir:
        print 'Both args not dir.'
    elif arg_one_is_dir and arg_two_is_dir:
        sync_dirs(arg_one, arg_two)  
    else:
        if arg_one_is_dir:
            print 'Arg1 is dir.'
            sync_dirs(arg_one, arg_two)
        else:
            print 'Arg2 is dir'
            sync_dirs(arg_two, arg_one)

def sync_dirs(from_dir, to_dir):
    """Syncs from one directory to another directory."""
    if not os.path.isdir(to_dir):
        os.makedirs(to_dir)
        print 'Made new dir: ' + to_dir  
    from_sync_file = from_dir + "/.sync"
    to_sync_file = from_dir + "/.sync"

    with open(from_dir + "/.sync", "a+") as f:
        f.write('hello')

do_sync(sys.argv[1], sys.argv[2])
