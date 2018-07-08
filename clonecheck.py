#!/usr/bin/python3

import os
import hashlib
from collections import defaultdict
import csv
import sys
BLOCK_SIZE = 65536
# RECTORIES = ['C:/Users/Mark/Dropbox', 'C:/Users/Mark/Photos']
FILE_TYPES = ['.jpg', 'jpeg', 'gif', 'png', 'avi', 'mov', 'mp4', 'mp3', 'mkv', 'ivx']

if len(sys.argv) < 2:
    print("Usage: clonecheck.py [DIRECTORY TO SCAN]")
    raise SystemExit

directory = sys.argv[1]

def get_files(directories):
    for base_dir in directories:
        for root, _, files in os.walk(base_dir):
            for filename in files:
                path = os.path.abspath(os.path.join(root, filename))
                if path[-4:] in (FILE_TYPES):
                    yield path
                # yield path    

def calculate_hashes(directories):
    hash_dict = defaultdict(list)
    for path in get_files(directories):
        hasher = hashlib.md5()
        try:
            with open(path, 'rb') as f:
                buf = f.read(BLOCK_SIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(BLOCK_SIZE)
        except FileNotFoundError as err:
            print(f"Skipping {path} {err}")
        hash_dict[hasher.hexdigest()].append(path)
    return hash_dict

def get_dupes(hash_dict):
    dupes = {}
    for k, v in hash_dict.items():
        if len(v) > 1:
            dupes[k] = v
    return dupes

def create_csv(dupes, fname='duplicates.csv'):
    with open(fname, 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=['hash', 'location'],
            delimiter=';', lineterminator='\n'
        )
        writer.writeheader()
        for k, v in dupes.items():
            writer.writerow({"hash": k, "location": v })
            
if __name__ == '__main__':
    hash_dict = calculate_hashes(directory)
    dupe_dict = get_dupes(hash_dict)
    create_csv(dupe_dict)
