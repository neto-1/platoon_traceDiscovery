#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Database Wrapper Class
"""
from __future__ import print_function
import psycopg2
import yaml
import io

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class Database(object):
    """
    Simple Database Wrapper for psycopg2
    """
    def __init__(self):
        """
        Init database connection
        """
        # load config
        with io.open("./config.yaml", 'r', encoding="utf-8") as ymlfile:
            cfg = yaml.load(ymlfile)
            pgname = (cfg["pgname"])
            pgpass = (cfg["pgpass"])
            pgdbname = (cfg["pgdbname"])
            pghost = (cfg["pghost"])

        # try to establish database connection
        try:
            self.conn = psycopg2.connect(
                "dbname={} user={} host={} port=5432 password={}".format(pgdbname, pgname, pghost, pgpass)
            )
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            print("Could not connect to database")
            raise

    def __exit__(self, *args):
        """ Close database connection """
        self.cursor.close()
        self.conn.close()
