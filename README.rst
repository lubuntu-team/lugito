======
lugito
======

.. _Lubuntu Project: https://lubuntu.me/

lugito is a Python package that provides a webserver for connecting updates from Phabricator to communication tools such as irc and other services such as launchpad.  Lugito was developed within `Lubuntu Project`_ for use as an irc bot.

Installation
-------------

lugito can be installed via Pyp


* Free software: 3 Clause BSD license


* Note the params in the phabricator.hooks are the webhook endpoints defined within Herald in Phabricator and the values are the corresponding HMAC values

Temp - Example .lugitorc
-------------------------

.. code::

   [phabricator]
   host = http://127.0.0.1:9091/api/
   token = api-nojs2ip33hmp4zn6u6cf72w7d6yh

   [phabricator.hooks]
   irc = cqg42zdcuqysff632kc6rnsu4m3hjg6c
   commithook = znkyfflbcia5gviqx5ybad7s6uyfywxi

   [phabricator.package_names]
   rDEFAULTSETTINGS = lubuntu-default-settings
   rART = lubuntu-artwork
   rCALASETTINGS = calamares-settings-ubuntu
   rQTERMINALPACKAGING = qterminal
   rLXQTCONFIGPACKAGING = lxqt-config
   rNMTRAYPACKAGING = nm-tray

   [jenkins]
   site = https://ci.lubuntu.me
   template_url = ssh://git@phab.lubuntu.me:2222/source/PACKAGE.git

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



Features
--------

* TODO

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
