# -*- coding: utf-8 -*-
"""Recipe node"""
from zc.recipe.cmmi import Recipe as Cmmi
from collective.recipe.cmd import Cmd
from zc.recipe.egg import Scripts
from glob import glob
import os

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        if 'url' not in options:
            options['url'] = 'http://nodejs.org/dist/node-v0.4.12.tar.gz'

    def install(self):
        """Installer"""
        options = self.options
        node_dir = os.path.join(self.buildout['buildout']['parts-directory'], self.name)
        node_bin = os.path.join(node_dir, 'bin')
        if not os.path.isdir(node_dir):
            options['environment'] = 'PYTHONPATH=tools:deps/v8/tools'
            node = Cmmi(self.buildout, self.name, options)
            node.install()

        options['on_install'] = 'true'
        options['on_update'] = 'true'

        cmd = Cmd(self.buildout, self.name, options)
        if not os.path.isdir(os.path.join(node_dir, 'lib', 'node_modules', 'npm')):
            options['cmds'] = ('export PATH=%s:$PATH;'
                               'curl http://npmjs.org/install.sh|clean=no sh'
                              ) % node_bin
            cmd.install()

        scripts = [script.strip() for script in options['scripts'].split() if script.strip()]

        npms = options.get('npms', '')
        if npms:
            npms = [npm.strip() for npm in npms.split() if npm.strip()]
            options['cmds'] = ('export PATH=%s:$PATH;'
                               'npm install -g %s'
                              ) % (node_bin, ' '.join(npms))
            cmd.install()

            bin_dir = os.path.join(self.buildout['buildout']['bin-directory'])

            node = os.path.join(node_bin, 'node')
            for script in scripts:
                if script in ['node']:
                    continue
                filename = os.path.join(node_bin, script)
                fd = open(filename)
                data = fd.read()
                fd.close()
                fd = open(filename, 'w')
                fd.seek(0)
                data = data.split('\n')
                data[0] = '#!%s' % node
                fd.write('\n'.join(data))
                fd.close()

        if 'node' not in scripts:
            scripts.append('node')
        rscripts = Scripts(self.buildout, self.name, options)
        options['eggs'] = 'gp.recipe.node'
        options['arguments'] = '%r, sys.argv[0]' % (node_bin,)
        options['initialization'] = 'import os; os.environ["NODE_PATH"] = %r' % os.path.join(node_dir, 'lib', 'node_modules')
        options['entry-points'] = '\n'.join([
            '%s=gp.recipe.node.script:main' % s for s in scripts
            ])
        return rscripts.install()

        #link = Link(self.buildout, self.name, options)
        #options['symlink'] = '\n'.join(scripts)
        #options['symlink_base'] = node_bin
        #options['symlink_target'] = bin_dir
        #return link.install()

    update = install
