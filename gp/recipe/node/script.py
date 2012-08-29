# -*- coding: utf-8 -*-
import os
import sys


def main(binary, dirnames, filename):
    script_name = os.path.basename(filename)
    if script_name == 'node':
        script = [binary]
    else:
        for dirname in dirnames:
            filename = os.path.join(dirname, script_name)
            if os.path.isfile(filename):
                script = [binary, filename]
    args = script + sys.argv[1:]
    os.execv(args[0], args[1:])
