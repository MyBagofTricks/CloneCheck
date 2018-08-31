#!/usr/bin/python3
#  Scans a folder recursively for select files, calculates their md5 and exports path 
#  of dupes to a csv

import os
import hashlib
import csv
from argparse import ArgumentParser
from collections import defaultdict

BLOCK_SIZE = 65536
FILE_TYPES = {
        'media': [
            'jpg', 'jpeg', 'gif', 'png', 'avi', 'mov', 'mp4', 'mp3', 'mkv', 'ivx',
            'txt', 'docx', 'doc', 'rtf', 'xls', 'xlsx', 'sql'
            ],
        'programs': ['exe', 'msi', 'dll', 'ps1', '.sh', 'perl', '.php', '.js', '.py', 'bat'],
        }

def parse_args():
   parser = ArgumentParser(
           description="Search a folder duplicate files based on their md5 and outputs to a csv")
   parser.add_argument(
           "path", help="Full path to scan. Use quotes if directory has spaces")
   parser.add_argument(
           "-t", "--type", help="options are 'media'(default) or 'programs'", default="media")
   args = parser.parse_args()
   return args.path, args.type

def get_files(path, ftype):
    for root, _, files in os.walk(path):
        for filename in files:
            file_path = os.path.abspath(os.path.join(root, filename))
            if (file_path[-4:] in ftype) or (file_path[-3:] in ftype):
                yield file_path

def calculate_hashes(path, ftype):
    hash_dict = defaultdict(list)
    for file_path in get_files(path, ftype):
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                buf = f.read(BLOCK_SIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = f.read(BLOCK_SIZE)
        except FileNotFoundError as err:
            print(f"Skipping {file_path} {err}")
        hash_dict[hasher.hexdigest()].append(file_path)
    return hash_dict

def get_dupes(hash_dict):
    dupes = {}
    for k, v in hash_dict.items():
        if len(v) > 1:
            dupes[k] = v
    return dupes

def create_csv(dupes, fname='output.csv'):
    with open(fname, 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=['hash', 'location'],
            delimiter=';', lineterminator='\n'
        )
        writer.writeheader()
        for k, v in dupes.items():
            writer.writerow({"hash": k, "location": v })
            

if __name__ == '__main__':
    path, ftype = parse_args()
    hash_dict = calculate_hashes(path, FILE_TYPES[ftype])
    dupe_dict = get_dupes(hash_dict)
    create_csv(dupe_dict)
