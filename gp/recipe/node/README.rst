Supported options
=================

The recipe supports the following options:

.. Note to recipe author!
   ----------------------
   For each option the recipe uses you should include a description
   about the purpose of the option, the format and semantics of the
   values it accepts, whether it is mandatory or optional and what the
   default value is if it is omitted.

url
    url to a node.js source archive

binary-url
    url to a node.js binary archive. You can use placeholders ``{v}`` (the
    desired node version), ``{p}`` (platform name), and ``{a}`` (CPU
    architecture).  Defaults to
    ``https://nodejs.org/dist/v{v}/node-v{v}-{p}-{a}.tar.gz``.  Ignored if
    url is set, or if the platform is not recognized.

version
    node.js version. Ignored if url is set, or if binary-url is set that
    doesn't use the ``{v}`` placeholder. Default to recipe version.  Mean
    that using ``recipe=gp.recipe.node==0.10.22.X`` will install ``node
    0.10.22``

npms
    a list of package to install with npm. You can specify a package version by
    using ``npmname@version``

scripts
    a list of scripts (optional)

node-path
    a list of extra directory to add to ``NODE_PATH``

relative-paths
    will generate paths relative to the root buildout directory.
    this is also honored if 'relative-paths' is in the main
    buildout section


Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = test1
    ...
    ... [test1]
    ... recipe = gp.recipe.node
    ... npms = coffee-script less
    ... scripts = coffee lessc
    ... """)

Running the buildout gives us::

    >>> print 'start', system(buildout)
    start...
    Installing test1.
    ...
    Generated script '.../bin/lessc'.
