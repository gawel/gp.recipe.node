# -*- coding: utf-8 -*-
import os
import sys


def main(binary, dirnames, filename):
    script_name = os.path.basename(filename)
    path = []
    if script_name == 'node':
        args = [binary] + sys.argv[1:]
        path.append(os.path.dirname(binary))
    else:
        script = None
        for dirname in dirnames:
            filename = os.path.join(dirname, script_name)
            if os.path.isfile(filename):
                script = [binary, filename]
                path.append(os.path.dirname(filename))
                break
        if script is None:
            all_scripts = []
            for p in dirnames:
                all_scripts.extend(os.listdir(p))
            all_scripts = [repr(s) for s in all_scripts]
            all_scripts = ', '.join(sorted(all_scripts))
            print((
                'Error: Script(s) {0} not found in {1[0]};{1[1]}.\n'
                'You may have a typo in your buildout config.\n'
                'Available scripts are: {2}'
            ).format(repr(script_name), dirnames, all_scripts))
            sys.exit(1)
        args = script + sys.argv[1:]
        with open(filename) as fd:
            shebang = fd.readline()
            if shebang.startswith('#!') and 'node' not in shebang:
                args = [filename] + sys.argv[1:]
    os.environ['PATH'] = os.pathsep.join(path + [os.environ['PATH']])
    os.execve(args[0], args, os.environ)
