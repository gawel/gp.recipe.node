# -*- coding: utf-8 -*-
"""Recipe node"""
import subprocess
import logging
import glob
import sys
import os
from pipes import quote as shell_quote


class Recipe(object):
    """zc.buildout recipe"""

    binary_format = 'http://nodejs.org/dist/v{v}/node-v{v}-{p}-{a}.tar.gz'
    source_format = 'http://nodejs.org/dist/v{v}/node-v{v}.tar.gz'

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def get_binary(self, options, name='node'):
        node_binary = options.get('binary')
        parts = self.buildout['buildout']['parts-directory']
        if not node_binary:
            for path in ((parts, 'buildout-node', 'bin', name),
                         (parts, 'buildout-node', 'node-*', 'bin', name)):
                binaries = glob.glob(os.path.join(*path))
                if binaries:
                    node_binary = binaries[0]
        return node_binary

    def get_version(self, options):
        version = options.get('version')
        if version:
            return version
        import pkg_resources
        version = pkg_resources.get_distribution('gp.recipe.node').version
        version = list(version.split('.'))
        version = [i for i in version if i.isdigit()][:-1]  # allow .dev0
        return '.'.join(version)

    def install(self):
        """Installer"""
        logger = logging.getLogger(self.name)
        options = self.options
        parts = self.buildout['buildout']['parts-directory']

        name = 'buildout-node'
        node_dir = os.path.join(parts, self.name)
        if not os.path.isdir(node_dir):
            os.makedirs(node_dir)

        node_binary = self.get_binary(options)

        if node_binary is None:
            args = {}
            if 'url' not in options:
                args = dict(
                    v=self.get_version(options),
                    a='x86_64' in os.uname() and 'x64' or 'x86',
                )
                if sys.platform.startswith('linux'):
                    args['p'] = 'linux'
                elif sys.platform == 'darwin':
                    args['p'] = 'darwin'

            if 'p' in args:
                options['url'] = url = self.binary_format.format(**args)
                logger.info('Using binary distribution at %s', url)

                from zc.buildout.download import Download
                from archive import extract

                # Use the buildout download infrastructure
                manager = Download(options=self.buildout['buildout'])

                # The buildout download utility expects us to know whether or
                # not we have a download cache, which causes fun errors.  This
                # is probably a bug, but this test should be safe regardless.
                if manager.download_cache:
                    filename = manager.download_cached(url)[0]
                else:
                    filename = manager.download(url)[0]

                destination = os.path.join(
                    self.buildout['buildout']['parts-directory'],
                    name)

                # Finally, extract the archive.  The binary distribution urls
                # are defined in this file, so we can safely assume they're
                # gzipped tarballs.  This prevents an error when downloaded
                # into a temporary file.
                extract(filename, destination, ext=".tar.gz")

            else:
                if 'url' not in options:
                    options['url'] = url = self.source_format.format(**args)
                logger.info('Using source distribution at %s', options['url'])
                import hexagonit.recipe.cmmi
                options['environment'] = (
                    'PYTHONPATH=tools:deps/v8/tools:../../deps/v8/tools'
                )

                node = hexagonit.recipe.cmmi.Recipe(
                    self.buildout, name, options)
                node.install()

            node_binary = self.get_binary(options)

        node_bin = os.path.dirname(node_binary)

        scripts = options.get('scripts', '').split()
        scripts = [script.strip() for script in scripts
                   if script.strip()]

        npms = options.get('npms', '')
        if npms:
            npms = ' '.join([npm.strip() for npm in npms.split()
                             if npm.strip()])

            p = subprocess.Popen((
                'export HOME=%(node_dir)s;'
                'export PATH=%(node_bin)s:$PATH;'
                'echo "prefix=$HOME\n" > $HOME/.npmrc;'
                '%(node_bin)s/npm set color false;'
                '%(node_bin)s/npm set unicode false;'
                '%(node_bin)s/npm install -sg %(npms)s') % {
                    'node_dir': shell_quote(node_dir),
                    'node_bin': shell_quote(node_bin),
                    'npms': npms},
                shell=True)
            p.wait()

            if not scripts:
                scripts = os.listdir(os.path.join(node_dir, 'bin'))

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

        for script in ('node', 'npm'):
            if script not in scripts:
                scripts.append(script)

        node_path = options.get('node-path', '').split()
        node_path.insert(0, os.path.join(node_dir, 'lib', 'node_modules'))
        node_path = ':'.join(node_path)
        options['initialization'] = (
            'import os;\nos.environ["NODE_PATH"] = %r' % node_path
        )

        paths = [os.path.join(node_dir, 'bin'), node_bin]
        all_scripts = []
        for p in paths:
            if os.path.isdir(p):
                all_scripts.extend(os.listdir(p))

        typos = []
        for script in scripts:
            if script not in all_scripts:
                typos.append(script)
        if typos:
            import zc.buildout
            typos = ', '.join([repr(s) for s in typos])
            all_scripts = [repr(s) for s in all_scripts]
            all_scripts = ', '.join(sorted(all_scripts))
            raise zc.buildout.UserError((
                'Script(s) {0} not found in {1[0]};{1[1]}.\n'
                'You may have a typo in your buildout config.\n'
                'Available scripts are: {2}'
            ).format(typos, paths, all_scripts))

        options['eggs'] = 'gp.recipe.node'
        options['arguments'] = '%r, (%r, %r), sys.argv[0]' % (
            node_binary,
            os.path.join(node_dir, 'bin'),
            node_bin,
        )
        options['scripts'] = '\n'.join(scripts)
        options['entry-points'] = '\n'.join([
            '%s=gp.recipe.node.script:main' % s for s in scripts
        ])
        from zc.recipe.egg import Scripts
        rscripts = Scripts(self.buildout, self.name, options)
        return rscripts.install()

    def update(self):
        pass
