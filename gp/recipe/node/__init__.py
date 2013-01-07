# -*- coding: utf-8 -*-
"""Recipe node"""
import subprocess
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
        parts = self.buildout['buildout']['parts-directory']
        name = options['url'].split('/')[-1].replace('.tar.gz', '')
        node_dir = os.path.join(parts, self.name)
        if not os.path.isdir(node_dir):
            os.makedirs(node_dir)
        node_binary = options.get('binary',
                                  os.path.join(parts, name, 'bin', 'node'))
        node_bin = os.path.dirname(node_binary)

        if not os.path.isfile(node_binary):
            from zc.recipe.cmmi import Recipe as Cmmi
            options['environment'] = 'PYTHONPATH=tools:deps/v8/tools'
            node = Cmmi(self.buildout, name, options)
            node.install()

        options['on_install'] = 'true'
        options['on_update'] = 'true'

        if not os.path.isfile(os.path.join(node_bin, 'npm')):
            p = subprocess.Popen((
                    'curl -sk https://npmjs.org/install.sh > install.sh&&'
                    'PATH=%s:$PATH '
                    'clean=yes sh install.sh&&rm install.sh'
                              ) % (node_bin,), shell=True)
            p.wait()

        scripts = [script.strip() for script in options['scripts'].split() \
                                                            if script.strip()]

        npms = options.get('npms', '')
        if npms:
            npms = ' '.join([npm.strip() for npm in npms.split() \
                                                            if npm.strip()])
            p = subprocess.Popen(('export HOME=%(node_dir)s;'
                               'export PATH=%(node_bin)s:$PATH;'
                               'echo "prefix=$HOME" > $HOME/.npmrc;'
                               '%(node_bin)s/npm install -g %(npms)s'
                              ) % locals(), shell=True)
            p.wait()

            for script in scripts:
                if script in ['node']:
                    continue
                filename = os.path.join(node_bin, script)
                if os.path.isfile(filename):
                    fd = open(filename)
                    data = fd.read()
                    fd.close()
                    fd = open(filename, 'w')
                    fd.seek(0)
                    data = data.split('\n')
                    data[0] = '#!%s' % node_binary
                    fd.write('\n'.join(data))
                    fd.close()

        if 'node' not in scripts:
            scripts.append('node')

        node_path = options.get('node-path', '').split()
        node_path.insert(0, os.path.join(node_dir, 'lib', 'node_modules'))
        node_path = ':'.join(node_path)
        options['initialization'] = \
                        'import os;\nos.environ["NODE_PATH"] = %r' % node_path

        options['eggs'] = 'gp.recipe.node'
        options['arguments'] = '%r, (%r, %r), sys.argv[0]' % (
                                node_binary,
                                os.path.join(node_dir, 'bin'),
                                node_bin,
                             )
        options['entry-points'] = '\n'.join([
            '%s=gp.recipe.node.script:main' % s for s in scripts
            ])
        from zc.recipe.egg import Scripts
        rscripts = Scripts(self.buildout, self.name, options)
        return rscripts.install()

    def update(self):
        pass
