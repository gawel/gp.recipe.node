# -*- coding: utf-8 -*-
import os
import sys
import shutil
import tempfile
import subprocess
import zc.buildout.configparser
from unittest import TestCase
from unittest import skipIf
from gp.recipe.node import Recipe
try:
    # python 2
    from StringIO import StringIO
except:
    # python 3
    from io import StringIO

TRAVIS = os.path.isdir('/home/travis')
PY3 = bool(sys.version_info[0] == 3)

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
url = http://nodejs.org/dist/v0.12.0/node-v0.12.0.tar.gz
npms =
    less
scripts =
    lessc

[node3]
recipe = gp.recipe.node

[node4]
recipe = gp.recipe.node
binary-url = https://nodejs.org/dist/v0.12.0/node-v0.12.0-{p}-{a}.tar.gz

[relativepaths]
recipe = gp.recipe.node
relative-paths = true
"""


class TestNode(TestCase):

    def setUp(self):
        self.pwd = os.path.abspath(os.getcwd())
        self.wd = tempfile.mkdtemp()
        os.environ['HOME'] = self.wd
        self.buildout = os.path.join(self.pwd, 'bin', 'buildout')
        if not os.path.isfile(self.buildout):
            self.buildout = 'buildout'
        os.chdir(self.wd)

    def tearDown(self):
        if hasattr(self, 'wd'):
            shutil.rmtree(self.wd)
        os.chdir(self.pwd)

    def callFTU(self, part, offline=False):
        with open(os.path.join(self.wd, 'buildout.cfg'), 'w') as fd:
            fd.write(BUILDOUT % self.pwd)
        cmd = [self.buildout, 'buildout:parts=' + part]
        if offline:
            cmd.append('-o')
        output = subprocess.check_output(cmd)
        output = output.decode('utf8')
        return output

    def test_binaries(self):
        output = self.callFTU('node1')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'less'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

        output = subprocess.check_output(
            [os.path.join(self.wd, 'bin', 'lessc'), '-v'])
        output = output.decode('utf8')
        self.assertTrue(output.startswith('lessc'))

    def test_binaries_offline(self):
        self.assertRaises(
            subprocess.CalledProcessError, self.callFTU, 'node1',
            offline=True)

    def test_binaries_offline_after_install(self):
        output = self.callFTU('node1')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'less'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

        output = self.callFTU('node1', offline=True)
        self.assertIn('Updating node1', output)

    @skipIf(TRAVIS, 'Skip compile on travis')
    @skipIf(PY3, 'Compile only work with a py2 installed')
    def test_compile(self):
        output = self.callFTU('node2')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'less'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

        output = subprocess.check_output(
            [os.path.join(self.wd, 'bin', 'node'), '-v'])
        assert 'v0.12.0' in output
        output = subprocess.check_output(
            [os.path.join(self.wd, 'bin', 'lessc'), '-v'])
        self.assertTrue(output.startswith('lessc'))

    def test_no_scripts(self):
        output = self.callFTU('node3')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

    def test_binary_url(self):
        output = self.callFTU('node4')
        self.assertIn(os.path.join(self.wd, 'bin', 'node'), output)
        self.assertIn(os.path.join(self.wd, 'bin', 'npm'), output)

    def test_relative_paths(self):
        self.callFTU('relativepaths')
        node_path = os.path.join(self.wd, 'bin', 'node')
        with open(node_path) as fd:
            content = fd.read()
            assert "NODE_PATH = [join(base, 'parts" in content


class TestNodeClass(TestCase):
    """ class to unit test the recipe directly """

    def setUp(self):
        self.buildout = zc.buildout.configparser.parse(
            StringIO(BUILDOUT),
            'buildout.cfg')
        self.name = 'test'
        self.options = {}
        self.recipe = Recipe(self.buildout,
                             self.name,
                             self.options)

    def test_to_relative(self):
        """ _to_relative should convert absolute buildout paths to relative """
        buildout_dir_path = 'foo'
        self.buildout['buildout']['directory'] = buildout_dir_path
        test_suffix = os.path.join(
            "parts", "node", "bin", "node"
        )
        test_absolute_path = os.path.join(
            buildout_dir_path, test_suffix
        )
        self.assertEquals(
            self.recipe._to_relative(test_absolute_path),
            "join(base, '{0}')".format(test_suffix)
        )

    def test_get_path(self):
        """
        _get_path should choose to change the path to relative
        or not based on the buildout configuration
        """
        buildout_dir_path = 'foo'
        self.buildout['buildout']['directory'] = buildout_dir_path
        absolute_path = os.path.join(
            buildout_dir_path, 'parts', 'node', 'bin', 'node'
        )
        self.recipe._use_relative_paths = True
        self.assertTrue(
            'join(base' in self.recipe._get_path(absolute_path)
        )
        self.recipe._use_relative_paths = False
        self.assertFalse(
            'join(base' in self.recipe._get_path(absolute_path)
        )

    def test_determine_use_relative_paths(self):
        """ relative paths should be honored """

        self.options['relative-paths'] = 'false'
        self.assertFalse(self.recipe._determine_use_relative_paths())
        del(self.options['relative-paths'])

        self.buildout['buildout']['relative-paths'] = 'true'
        self.assertTrue(self.recipe._determine_use_relative_paths())

        self.buildout['buildout']['relative-paths'] = 'false'
        self.assertFalse(self.recipe._determine_use_relative_paths())

        self.options['relative-paths'] = 'true'
        self.assertTrue(self.recipe._determine_use_relative_paths())
