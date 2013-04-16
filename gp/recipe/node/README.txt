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
    url to a node.js archive

version
    node.js version. Ignored if url is set. Default to recipe version.  Mean
    that using ``recipe=gp.recipe.node==0.10.3.X`` will install ``node 0.10.3``

npms
    a list of package to install with npm. You can specify a package version by
    using ``npmname@version``

scripts
    a list of scripts

node-path
    a list of extra directory to add to ``NODE_PATH``


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


