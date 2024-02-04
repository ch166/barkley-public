""" Support Debugging Printing """

# -*- coding: utf-8 -*-


import datetime

DEBUG_MSGS = True


def dprint(args):
    """Passthrough call to print() if DEBUG_MSGS is enabled"""
    if DEBUG_MSGS:
        appname = "barkley"
        logtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(logtime, appname, "DEBUG:", args, flush=True)
