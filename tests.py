import os
import shutil
import subprocess
import tempfile
from io import StringIO
from unittest import TestCase

import zc.buildout.configparser

from gp.recipe.node import Recipe


BUILDOUT = """
[buildout]
develop = %s

[node1]
recipe = gp.recipe.node
npms =
    less
scripts =
    lessc

[node3]
recipe = gp.recipe.node

[node4]
recipe = gp.recipe.node
binary-url = https://nodejs.org/dist/v24.0.1/node-v24.0.1-{p}-{a}.tar.gz

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
        self.assertEqual(
            self.recipe._to_relative(test_absolute_path),
            f"join(base, '{test_suffix}')"
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
        self.assertIn(
            'join(base',
            self.recipe._get_path(absolute_path)
        )
        self.recipe._use_relative_paths = False
        self.assertNotIn(
            'join(base',
            self.recipe._get_path(absolute_path)
        )

    def test_determine_use_relative_paths(self):
        """ relative paths should be honored """

        self.options['relative-paths'] = 'false'
        self.assertFalse(self.recipe._determine_use_relative_paths())
        del self.options['relative-paths']

        self.buildout['buildout']['relative-paths'] = 'true'
        self.assertTrue(self.recipe._determine_use_relative_paths())

        self.buildout['buildout']['relative-paths'] = 'false'
        self.assertFalse(self.recipe._determine_use_relative_paths())

        self.options['relative-paths'] = 'true'
        self.assertTrue(self.recipe._determine_use_relative_paths())
