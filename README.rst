=====
pynxm
=====
.. image:: https://img.shields.io/pypi/v/pynxm.svg?style=flat-square&label=PyPI
    :target: https://pypi.org/project/pynxm/
.. image:: https://img.shields.io/pypi/pyversions/pynxm.svg?style=flat-square&label=Python%20Versions
    :target: https://pypi.org/project/pynxm/
.. image:: https://img.shields.io/travis/GandaG/pynxm/master.svg?style=flat-square&label=Linux%20Build
    :target: https://travis-ci.org/GandaG/pynxm
.. image:: https://img.shields.io/appveyor/ci/GandaG/pynxm/master.svg?style=flat-square&label=Windows%20Build
    :target: https://ci.appveyor.com/project/GandaG/pynxm/branch/master

*A python wrapper for the Nexus API.*

Features:

- Retrieve information regarding colour-specific themes for games;
- Access resources specific to a user:
    - Get user details;
    - Get user's endorsements;
    - Get, add and delete user's tracked mods.
- Retrieve game information;
- Access mod information:
    - Get latest added mods;
    - Get latest updated mods;
    - Get all updated mods in a specific period of time;
    - Get trending mods;
    - Search for a specific mod;
    - Get mod details;
    - Get mod's changelogs;
    - Endorse or abstain from endorsing a mod.
- Access a mod's files:
    - List a mod's files;
    - Get a mod's file details;
    - Generate a download link for a mod's file.

Installation
------------

To install *pynxm*, use pip::

    pip install pynxm

Users will also need an api key to login with, generate one for your account
`here <https://www.nexusmods.com/users/myaccount?tab=api%20access>`_.

Application developers that wish to use Nexus' Single Sign-On (SSO) will need an
application slug and a connection token, please contact a Nexus Community Manager
for more information.

Quick Examples
--------------

Connect to Nexus::

    >>> api_key = "my-api-key"
    >>> nxm = pynxm.Nexus(api_key)

Track a new mod::

    >>> game = "fallout3"
    >>> mod_id = "00000"
    >>> nxm.user_tracked_add(game, mod_id)

Endorse a mod::

    >>> game = "newvegas"
    >>> mod_id = "99999"
    >>> nxm.mod_endorse(game, mod_id)

Documentation
-------------

For more information check out *pynxm*'s API documentation at `pynxm.rtfd.io <https://pynxm.rtfd.io>`_

You can supplement *pynxm*'s API docs with the
`Nexus API documentation <https://app.swaggerhub.com/apis-docs/NexusMods/nexus-mods_public_api_params_in_form_data/1.0#/>`_.

Issues
------

Please use the `GitHub issue tracker <https://github.com/GandaG/pynxm/issues>`_ to submit bugs or request features.

Development
-----------

Setup a virtualenv, install `flit` and run::

    flit install -s

This will install an editable version of *pynxm* and all dev packages.

To run the checks and tests::

    tox

And to publish::

    flit publish
