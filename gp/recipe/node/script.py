# -*- coding: utf-8 -*-
import os
import sys
import subprocess

def main(bin_dir, filename):
    node = os.path.join(bin_dir, 'node')
    script = [os.path.join(bin_dir, os.path.basename(filename))]
    if node not in script:
        script.insert(0, node)
    subprocess.Popen(script+sys.argv[1:], stdout=sys.stdout, stderr=sys.stderr).wait()

