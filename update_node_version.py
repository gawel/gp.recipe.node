#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import re


def main():
    page = urllib.urlopen('http://nodejs.org/download/').read()
    version = re.search('v([0-9\.]+)', page).groups()[0]

    updated = ''
    with open('setup.py') as fd:
        for line in fd:
            if line.startswith('version ='):
                if version not in line:
                    line = "version = '%s.1.dev0'\n" % version
            updated += line

    with open('setup.py', 'w') as fd:
        fd.write(updated)

if __name__ == '__main__':
    main()
