# -*- coding: utf-8 -*-
"""Recipe node"""
import subprocess
import logging
import glob
import sys
import os
import json
from pipes import quote as shell_quote


class Recipe(object):
    """zc.buildout recipe"""

    binary_format = 'https://nodejs.org/dist/v{v}/node-v{v}-{p}-{a}.tar.gz'
    source_format = 'https://nodejs.org/dist/v{v}/node-v{v}.tar.gz'

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self._use_relative_paths = self._determine_use_relative_paths()

    def get_node_directory(self, options):
        directory = self.options.get('node-directory')
        if not directory:
            directory = self.buildout['buildout'].get('node-directory')
        if not directory:
            directory = os.path.join(
                self.buildout['buildout']['parts-directory'],
                'buildout-node')
        if not os.path.isdir(directory):
            os.makedirs(directory)
        return directory

    def get_binary(self, options, name='node'):
        node_binary = options.get('binary')
        directory = self.get_node_directory(options)
        if not node_binary:
            for path in ((directory, 'bin', name),
                         (directory, 'node-*', 'bin', name)):
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
                uname = os.uname()
                if 'x86_64' in uname:
                    a = 'x64'
                elif 'arm64' in uname:
                    a = 'arm64'
                else:
                    a = 'x86'
                args = dict(
                    v=self.get_version(options),
                    a=a,
                )
                if sys.platform.startswith('linux'):
                    args['p'] = 'linux'
                elif sys.platform == 'darwin':
                    args['p'] = 'darwin'

            if 'p' in args:
                binary_url = options.get('binary-url', self.binary_format)
                options['url'] = url = binary_url.format(**args)
                logger.info('Using binary distribution at %s', url)

                from zc.buildout.download import Download
                from archive import extract

                # Use the buildout download infrastructure
                manager = Download(options=self.buildout['buildout'],
                                   offline=self.buildout['buildout'].get('offline') == 'true')

                # The buildout download utility expects us to know whether or
                # not we have a download cache, which causes fun errors.  This
                # is probably a bug, but this test should be safe regardless.
                if manager.download_cache:
                    filename = manager.download_cached(url)[0]
                else:
                    filename = manager.download(url)[0]

                destination = self.get_node_directory(options)

                # Finally, extract the archive.  The binary distribution urls
                # are defined in this file, so we can safely assume they're
                # gzipped tarballs.  This prevents an error when downloaded
                # into a temporary file.
                extract(filename, destination, ext=".tar.gz")

            else:
                if 'url' not in options:
                    options['url'] = url = self.source_format.format(**args)
                logger.info('Using source distribution at %s', options['url'])
                import zc.recipe.cmmi
                options['environment'] = (
                    'PYTHONPATH=tools:deps/v8/tools:../../deps/v8/tools'
                )

                node = zc.recipe.cmmi.Recipe(
                    self.buildout, name, options)
                node.install()

            node_binary = self.get_binary(options)

        node_bin = os.path.dirname(node_binary)

        npms = options.get('npms', '')
        if npms:
            npms = ' '.join([npm.strip() for npm in npms.split()
                             if npm.strip()])
            cmd_data = {'node_dir': shell_quote(node_dir),
                        'node_bin': shell_quote(node_bin),
                        'cache': os.path.expanduser('~/.npm'),
                        'npms': npms}
            cmd_prefix = (
                'export HOME=%(node_dir)s;'
                'export PATH=%(node_bin)s:"$PATH";'
                'echo "prefix=$HOME" > $HOME/.npmrc;'
                'echo "cache=%(cache)s" >> $HOME/.npmrc;'
                '%(node_bin)s/npm set color false;'
                '%(node_bin)s/npm set unicode false;') % cmd_data

            if self.buildout['buildout'].get('offline') == 'true':
                cmd = cmd_prefix + \
                    '%(node_bin)s/npm ls %(npms)s --global --json' % cmd_data
                import zc.buildout
                try:
                    output = subprocess.check_output(cmd, shell=True)
                    output_json = json.loads(output)
                    installed_npms = output_json.get('dependencies')
                    # if npm reports a discrepancy, error out
                    if not installed_npms or \
                            len(installed_npms) != len(npms.split()):
                        raise zc.buildout.UserError(
                            "Couldn't install %r npms in offline mode" % npms)
                    logger.debug('Using existing npm install for %r' % npms)
                except subprocess.CalledProcessError:
                    # npm fails if install has not yet happened
                    raise zc.buildout.UserError(
                        "Couldn't install %r npms in offline mode" % npms)

            else:
                cmd = cmd_prefix + \
                    '%(node_bin)s/npm install -g %(npms)s' % cmd_data
                p = subprocess.Popen(cmd, shell=True)
                p.wait()

        return self.install_scripts()

    def install_scripts(self):
        options = self.options
        node_binary = self.get_binary(options)
        parts = self.buildout['buildout']['parts-directory']
        node_dir = os.path.join(parts, self.name)
        node_bin = os.path.dirname(node_binary)
        scripts = options.get('scripts', '').split()
        scripts = [script.strip() for script in scripts
                   if script.strip()]

        if not scripts and os.path.isdir(os.path.join(node_dir, 'bin')):
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
        node_path = [self._get_path(pth) for pth in node_path]
        options['initialization'] = INITIALIZE % {
            'node_path': ', '.join(node_path),
            'node_dir_bin': self._get_path(os.path.join(node_dir, 'bin')),
            'node_bin': self._get_path(node_bin),
        }

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
        node_dir_bin = os.path.join(node_dir, 'bin')
        options['arguments'] = '%s, (%s, %s), sys.argv[0]' % (
            self._get_path(node_binary),
            self._get_path(node_dir_bin),
            self._get_path(node_bin),
        )
        options['scripts'] = '\n'.join(scripts)
        options['entry-points'] = '\n'.join([
            '%s=gp.recipe.node.script:main' % s for s in scripts
        ])
        from zc.recipe.egg import Scripts
        rscripts = Scripts(self.buildout, self.name, options)
        return rscripts.install()

    def update(self):
        return self.install_scripts()

    def _to_relative(self, absolute_path):
        """ convert an absolute path to a relative one """
        directory = self.buildout['buildout']['directory']
        if directory in absolute_path:
            path = absolute_path.replace(
                self.buildout['buildout']['directory'], '').lstrip(os.sep)
            return "join(base, '{1}')".format(self.name, path)
        else:
            return "'{0}'".format(absolute_path)

    def _get_path(self, absolute_path):
        if self._use_relative_paths:
            return self._to_relative(absolute_path)
        else:
            return "'{0}'".format(absolute_path)

    def _determine_use_relative_paths(self):
        # this mirrors behaviour in zc.recipe.egg
        return self.options.get(
            'relative-paths',
            self.buildout['buildout'].get('relative-paths', 'false')
            ) == 'true'

INITIALIZE = '''
import os
from glob import glob

NODE_PATH = [%(node_path)s]
NODE_PATH.extend(
   glob(os.path.join(NODE_PATH[0], "*", "node_modules"))
)
os.environ["NODE_PATH"] = os.pathsep.join(NODE_PATH)

os.environ["PATH"] = os.pathsep.join([
    %(node_bin)s,
    %(node_dir_bin)s,
    os.environ["PATH"],
])
'''
