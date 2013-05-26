# -*- coding: utf-8 -*-
import os
import shutil
import tempfile
import subprocess
from unittest import TestCase

BUILDOUT = """
[buildout]
develop = %s

[node1]
recipe = gp.recipe.node
npms =
    less
scripts =
    lessc

[node2]
recipe = gp.recipe.node
url = http://nodejs.org/dist/v0.10.4/node-v0.10.4.tar.gz
npms =
    less
scripts =
    lessc

[node3]
recipe = gp.recipe.node
"""


class TestNode(TestCase):

    def setUp(self):
        self.pwd = os.path.abspath(os.getcwd())
        self.wd = tempfile.mkdtemp()
        os.environ['HOME'] = self.wd
        self.addCleanup(shutil.rmtree, self.wd)
        self.buildout = os.path.join(self.pwd, 'bin', 'buildout')
        os.chdir(self.wd)
        self.addCleanup(os.chdir, self.pwd)

    def callFTU(self, part):
        with open(os.path.join(self.wd, 'buildout.cfg'), 'w') as fd:
            fd.write(BUILDOUT % self.pwd)
        cmd = [self.buildout, 'buildout:parts=' + part]
        output = subprocess.check_output(cmd)
        return output

    def test_binaries(self):
        output = self.callFTU('node1')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'less'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

        output = subprocess.check_output(
            [os.path.join(self.wd, 'bin', 'lessc'), '-v'])
        self.assertTrue(output.startswith('lessc'))

    def test_compile(self):
        output = self.callFTU('node2')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'less'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

        output = subprocess.check_output(
            [os.path.join(self.wd, 'bin', 'node'), '-v'])
        self.assertTrue(output.startswith('v0.10.4'))
        output = subprocess.check_output(
            [os.path.join(self.wd, 'bin', 'lessc'), '-v'])
        self.assertTrue(output.startswith('lessc'))

    def test_no_scripts(self):
        output = self.callFTU('node3')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)
