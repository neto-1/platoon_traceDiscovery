#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Abstract Model Class
"""
from __future__ import print_function
from .database import Database


class Model(object):
    """
    Simple Abstract Model Class
    """
    def __init__(self, logging=True):
        """
        Init database connection
        :param logging: Enable/Disable logging
        """
        self.db = Database()
        self.logging = logging

    def _log(self, message):
        """
        Print a log message to the screen of logging is enabled
        :param message: Log message
        """
        if self._log:
            print("[LOG]: " + message)
