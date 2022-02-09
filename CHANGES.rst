16.13.2.1 (2022-02-09)
======================

- update to 16.13.2

- claim support for Python 3.6, 3.7, 3.8, 3.9, 3.10

- Load 'arm64' version of node.js on M1/arm apple machines and others.


13.3.0.1 (2019-12-12)
=====================

- update to 13.x


6.2.2.1 (2016-06-28)
====================

- Add support for offline mode in Buildout (`-o`)

- Quote $PATH variable in order to fix problem when $PATH contains space
  characters.


0.12.7.1 (2015-09-01)
=====================

- allow to specify URL for binary node.js distribution (binary-url)


0.12.3.3 (2015-05-22)
=====================

- allow to run non-node scripts (casperjs)

- extend PATH to buildout related paths

- extend NODE_PATH to module dependencies (allow to install .)


0.12.3.2 (2015-05-21)
=====================

- Bugfix when using ``node-directory`` combined with ``relative-path``


0.12.3.1 (2015-05-21)
=====================

- Allow to install node outside parts/ by specifying ``node-directory`` options

- Switch to 0.12.3.1

0.12.0.1 (2015-03-12)
=====================

- Switch to 0.12.0


0.10.28.0 (2014-06-03)
======================

- Switch to 0.10.28

- relative-paths should be honored


0.10.26.0 (2014-02-28)
======================

- Switch to 0.10.26


0.10.24.0 (2013-12-26)
======================

- Switch to 0.10.24


0.10.22.1 (2013-11-23)
======================

- Switch to 0.10.22

- scripts option is no longer required


0.10.21.1 (2013-11-08)
======================

- Switch to 0.10.21

- Allow dev version

- PEP8


0.10.20.1 (2013-10-14)
======================

- Switch to 0.10.20

- py3 compat


0.10.18.2 (2013-09-13)
======================

- Fixes a failure installing npms when the buildout path contains spaces

0.10.18.1
=========

- Update node version

- Allow to use download cache

0.10.8.1
========

- Allow to install only node/npm

0.10.5.1
========

- Now use binary distribution on linux and osx by default. Mean that the recipe
  no longer require gcc and the installation is way much faster.

- Raise an error if a script does not exist

- Use package version to get the node.js version to install

0.3
===

- Change npm install script location
  [Ross Pfahler]

0.1
===

- Created recipe with ZopeSkel
  [Gael Pasgrimaud]
