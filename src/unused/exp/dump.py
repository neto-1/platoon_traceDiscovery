#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple dump script to dump PostgreSQL Database
"""
from __future__ import print_function
from urllib.parse import quote
import os
import time
import subprocess
import gzip
import shutil
import yaml

def dump():
    """
    Dump a postgre sql database into a file and compress it
    """
    # Read Config file
    with open("config.yaml", 'r') as ymlfile:
        config = yaml.load(ymlfile)

        if "pgdump" not in config:
            print(
                "Please specify the full path to the pg_dump executable in the yaml file. Example:",
                "\npgdump: \"C:/Program Files/PostgreSQL/10/bin/pg_dump.exe\""
            )
            return 0

    # Get Dir and File path
    directory = os.path.dirname(os.path.realpath(__file__)) + '/dumps'
    filename = 'dump.{}-{}.sql'.format(config['pgdbname'], int(time.time()))
    outfile = '{}/{}'.format(directory, filename)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write Info
    print("============= Dumping Database ============= ")
    print("Start:", time.strftime('%x %X'))
    print("Database:", config['pgdbname'])
    print("Directory:", directory)
    print("File:", filename)

    # Dump Data
    print("\nDumping database into sql file via pg_dump ...")
    pgdump = subprocess.Popen([
        config['pgdump'],
        "--dbname=postgresql://{}:{}@{}:{}/{}".format(
            quote(config['pgname']),
            quote(config['pgpass']),
            config['pghost'],
            config['pgport'],
            config['pgdbname'],
        ),
        "--format=p",
        "--file={}".format(outfile),
        "--column-inserts"
    ], executable=config['pgdump'])

    # Compress file
    pgdump.communicate()
    print("Compressing file ...")
    with open(outfile, 'rb') as f_in, gzip.open(outfile + '.gz', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

    # Remove uncompressed file
    print("Cleanup ...")
    os.remove(outfile)

    print("\nFinished dumping database!")

if __name__ == '__main__':
    dump()
