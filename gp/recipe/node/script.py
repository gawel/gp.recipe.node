# -*- coding: utf-8 -*-
import os
import sys
import subprocess

def main(binary, dirnames, filename):
    script_name = os.path.basename(filename)
    if script_name == 'node':
        script = [binary]
    else:
        for dirname in dirnames:
            filename = os.path.join(dirname, script_name)
            if os.path.isfile(filename):
                script = [binary, filename]
    subprocess.Popen(script+sys.argv[1:],
                     stdout=sys.stdout,
                     stderr=sys.stderr).wait()

