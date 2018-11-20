lugito
======

[![image](https://img.shields.io/pypi/v/lugito.svg)](https://pypi.python.org/pypi/lugito)

[![image](https://img.shields.io/travis/doc-E-brown/lugito.svg)](https://travis-ci.org/doc-E-brown/lugito)

[![Documentation Status](https://readthedocs.org/projects/lugito/badge/?version=latest)](https://lugito.readthedocs.io/en/latest/?badge=latest)

Python Boilerplate contains all the boilerplate you need to create a
Python package.

-   Free software: 3 Clause BSD license
-   Documentation: <https://lugito.readthedocs.io>.

Temp - Example .lugitorc
------------------------

```
[phabricator]
host = http://127.0.0.1:9091/api/
token = api-nojs2ip33hmp4zn6u6cf72w7d6yh

[phabricator.hooks]
irc = cqg42zdcuqysff632kc6rnsu4m3hjg6c
commithook = znkyfflbcia5gviqx5ybad7s6uyfywxi

[connector.irc]
host = irc.freenode.net
port  = 6697
username = someusername
password = somepassword
channel = #somechannel

[connector.launchpad]
application = lugito
staging = production
version = devel
supported_versions =
    Cosmic
    Bionic
    Xenial
    Trusty

[connector.launchpad.package_names]
rDEFAULTSETTINGS = lubuntu-default-settings
rART = lubuntu-artwork
rCALASETTINGS = calamares-settings-ubuntu
rQTERMINALPACKAGING = qterminal
rLXQTCONFIGPACKAGING = lxqt-config
rNMTRAYPACKAGING = nm-tray
```

Features
--------

-   TODO

Credits
-------

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
