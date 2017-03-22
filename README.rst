iprir
=====

Retrieve, store and query information about Regional Internet Registries

|Build_Status| |codecov| |PyPI_Version| |Python_Version|

.. |Build_Status| image:: https://travis-ci.org/account-login/iprir.svg?branch=master
    :target: https://travis-ci.org/account-login/iprir
.. |codecov| image:: https://codecov.io/gh/account-login/iprir/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/account-login/iprir
.. |PyPI_Version| image:: https://badge.fury.io/py/iprir.svg
    :target: https://badge.fury.io/py/iprir
.. |Python_Version| image:: https://img.shields.io/pypi/pyversions/iprir.svg
    :target: https://badge.fury.io/py/iprir

Installation
------------

.. code-block:: bash

    pip install iprir


Usage
-----

Query by ip:

.. code-block:: python

    >>> import iprir
    >>> from ipaddress import IPv4Address, IPv6Address
    >>> iprir.by_ip(IPv4Address('8.8.8.8'))
    RIRRecord(country='US', type='ipv4', start='8.0.0.0', value='16777216', status='allocated')

Attributes of :code:`RIRRecord`:

.. code-block:: python

    >>> record = iprir.by_ip(IPv4Address('8.8.8.8'))
    >>> record.ipv4
    IPv4Address('8.0.0.0')
    >>> record.ipv4_network
    IPv4Network('8.0.0.0/8')
    >>> record.length
    16777216
    >>> record.as_int
    134217728

Use IpSet:

.. code-block:: python

    >>> us = iprir.by_country('ipv4', 'US')
    >>> IPv4Address('8.8.4.4') in us
    True
    >>> IPv4Address('1.2.3.4') in us
    False
    >>> from iprir.ipset import IpSet
    >>> db = iprir.get_db()
    >>> us_and_ca_v6 = IpSet(db.by_country('ipv6', 'US') + db.by_country('ipv6', 'CA'))
    >>> IPv6Address('2001:4860:4860::8888') in us_and_ca_v6
    True

Update database:

.. code-block:: bash

    # update text db and sqlite db
    python3 -m iprir.updater

    # show more choices
    python3 -m iprir.updater -h
