SaltStack service
=================

SaltStack service settings
--------------------------

SaltStack service settings have two additional quotas:

- exchange_storage - total disk space for Exchange installation.
- sharepoint_storage - total disk space for SharePoint installation.
- exchange_tenant_count - count of all created exchange tenants.

SaltStack services list
-----------------------

To get a list of services, run GET against **/api/saltstack/** as authenticated user.


Create a SaltStack service
--------------------------

To create a new SaltStack service, issue a POST with service details to **/api/saltstack/** as a customer owner.

Request parameters:

 - name - service name,
 - customer - URL of service customer,
 - settings - URL of SaltStack settings, if not defined - new settings will be created from server parameters,
 - dummy - is service dummy,

The following rules for generation of the service settings are used:

 - backend_url - URL for SaltStack master API (required, e.g.: http://salt-master.example.com:8080);
 - password - Secret key;

Example of a request:

.. code-block:: http

    POST /api/saltstack/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "My SaltStack",
        "customer": "http://example.com/api/customers/2aadad6a4b764661add14dfdda26b373/",
        "backend_url": "http://salt-master.example.com:8080",
        "password": "secretkey"
    }


Link service to a project
-------------------------
In order to be able to provision SaltStack resources, it must first be linked to a project. To do that,
POST a connection between project and a service to **/api/saltstack-service-project-link/** as staff user or customer
owner.
For example:

.. code-block:: http

    POST /api/saltstack-service-project-link/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "project": "http://example.com/api/projects/e5f973af2eb14d2d8c38d62bcbaccb33/",
        "service": "http://example.com/api/saltstack/b0e8a4cbd47c4f9ca01642b7ec033db4/"
    }

To remove a link, issue DELETE to url of the corresponding connection as staff user or customer owner.


Project-service connection list
-------------------------------
To get a list of connections between a project and an SaltStack service, run GET against
**/api/saltstack-service-project-link/** as authenticated user. Note that a user can only see connections of a project
where a user has a role.


MS Exchange
===========

.. include:: exchange.rst

MS Sharepoint
=============

.. include:: sharepoint.rst
