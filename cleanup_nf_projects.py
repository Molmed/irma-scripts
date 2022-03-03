#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script for cleaning up old analysis nextflow projects

The script will list folders (with full path) that will be deleted and calculate how much data will be removed.
It will wait for input from user before removing anything.

Usage:
cd /path/to/analysis/project
python /path/to/script/folder/cleanup_nf_projects.py

"""


import os
import math
from datetime import datetime
import shutil

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

# The last four elements are needed to support cleanup of sarek 2.3 data generated via the  ngi_pipeline,
# when we no longer has to support that, we can remove those folders from the list. / MÅ 20201104
cleanup_directory_names = ["work", "results", "Annotation", "Preprocessing", "VariantCalling", "Reports"]

directory_list = []

# Look for directories to clean
for dirpath, dirnames, filenames in os.walk("."):
    for dirname in dirnames:
        if dirname in cleanup_directory_names and dirname != ".":
            if os.path.abspath(dirpath) not in directory_list:
                full_path = os.path.abspath(os.path.join(dirpath, dirname))
                directory_list.append(full_path)

now = datetime.now()
clean_up_log = "cleanup_{}.log".format(str(now).replace(" ", "_").replace(":","-"))

# Find files to delete, and check how much disk will be cleared
files_to_clean_up = []
total_size = 0
for directory in directory_list:
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            files_to_clean_up.append(full_path)
            if not os.path.islink(full_path):
                total_size += os.stat(full_path).st_size
human_readable_size = convert_size(total_size)

# Get from user if we should delete stuff or not. If yes, write the clean up log and delete the dirs.
print("The following directories will be removed:")
for d in directory_list:
    print(d)

while True:
    yes_no = input("Do you want to delete {} of data? [y/N]\n".format(human_readable_size)) or "N"
    if yes_no == "y":
        print("I will ghost these suckers, writing log to: {}".format(clean_up_log))

        with open(clean_up_log, "w") as clean_up_file:
            for f in files_to_clean_up:
                clean_up_file.write(f + "\n")

        for f in directory_list:
            if os.path.isdir(f):
                shutil.rmtree(f)

        break
    elif yes_no == "N":
        clean_up_list = clean_up_log.replace("log", "list")
        with open(clean_up_list, "w") as clean_up_list_file:
            for f in files_to_clean_up:
                clean_up_list_file.write(f + "\n")
        print("Safety first! The files you did not remove have been written to {}".format(clean_up_list))
        break
    else:
        print("Did not recognize: {}.".format(yes_no))

