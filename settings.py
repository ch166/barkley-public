#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  9 16:52:41 2019

@author: chris
"""

import configparser


def init():
    """Initialize and load configuration"""
    global configfile
    configfile = configparser.ConfigParser()
    configfile.read("config.ini")


def get(section, key):
    """Read Setting"""
    return configfile.get(section, key)


def get_string(section, key):
    """Read Setting"""
    return configfile.get(section, key)


def get_bool(section, key):
    """Read Setting"""
    return configfile.getboolean(section, key)


def get_integer(section, key):
    """Read Setting"""
    return configfile.getint(section, key)
