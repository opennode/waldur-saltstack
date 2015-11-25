SaltStack service
=================

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

 - backend_url - URL for slat master API (required, e.g.: http://salt-master.example.com:8080);
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
To get a list of connections between a project and an oracle service, run GET against
**/api/saltstack-service-project-link/** as authenticated user. Note that a user can only see connections of a project
where a user has a role.


MS Exchange
===========

Create a tenant
---------------
Tenant is a SaltStack resource which represents MS Exchange Domain.
A new tenant can be created by users with project administrator role, customer owner role or with
staff privilege (is_staff=True). To create a tenant, client must issue POST request to **/api/exchange-tenants/** with
parameters:

 - name - Tenant name;
 - description - Description (optional);
 - link to the service-project-link object;
 - domain - Domain name;
 - max_users - Maximum number of users;
 - mailbox_size - Average mailboxes size (Gb);


 Example of a valid request:

.. code-block:: http

    POST /api/exchange-tenants/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "TNT",
        "service_project_link": "http://example.com/api/saltstack-service-project-link/1/",
        "tenant": "test.com",
        "max_users": "500",
        "mailbox_size": "3"
    }


Tenant display
--------------

To get tenant data - issue GET request against **/api/exchange-tenants/<tenant_uuid>/**.

Example rendering of the tenant object:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-tenants/7693d9308e0641baa95720d0046e5696/",
            "uuid": "7693d9308e0641baa95720d0046e5696",
            "name": "TNT",
            "description": "",
            "start_time": null,
            "service": "http://example.com/api/saltstack/655b79490b63442d9264d76ab9478f62/",
            "service_name": "My SaltStack",
            "service_uuid": "655b79490b63442d9264d76ab9478f62",
            "project": "http://example.com/api/projects/0e86f04bb1fd48e181742d0598db69d5/",
            "project_name": "My Project",
            "project_uuid": "0e86f04bb1fd48e181742d0598db69d5",
            "customer": "http://example.com/api/customers/3b0fc2c0f0ed4f40b26126dc9cbd8f9f/",
            "customer_name": "Me",
            "customer_native_name": "",
            "customer_abbreviation": "",
            "project_groups": [],
            "resource_type": "SaltStack.Tenant",
            "state": "Online",
            "created": "2015-10-20T10:35:19.146Z"
        }
    ]


Delete tenant
-------------

To delete tenant - issue DELETE request against **/api/exchange-tenants/<tenant_uuid>/**.


Create tenant user
------------------

To create new tenant user - issue POST request against **/api/exchange-tenants/<tenant_uuid>/users/**.

Request parameters:

 - username - new user username;
 - last_name - new user last name;
 - first_name - new user first name;
 - mailbox_size - mailbox size (Mb);

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/users/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "username": "joe",
        "first_name": "Joe",
        "last_name": "Doe",
        "mailbox_size": "5"
    }


List tenant users
-----------------

To get a list of all tenant users - issue GET request against **/api/exchange-tenants/<tenant_uuid>/users/**.
Only users with view access to tenant can view tenant users.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-tenants/24156c367e3a41eea81e374073fa1060/users/e88471c7-fcf5-4e12-8163-2a8ad9c87f4b/",
            "id": "e88471c7-fcf5-4e12-8163-2a8ad9c87f4b",
            "email": "joe@test.com",
            "first_name": "Joe",
            "last_name": "Doe",
            "password": "+!V?5T$9!61@"
        }
    ]


Delete tenant user
------------------

To delete tenant user - issue DELETE request against **/api/exchange-tenants/<tenant_uuid>/users/<user_id>/**.


Create tenant contact
---------------------

To create new tenant contact - issue POST request against **/api/exchange-tenants/<tenant_uuid>/contacts/**.

Request parameters:

 - email - new contact email;
 - last_name - new contact last name;
 - first_name - new contact first name;

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/contacts/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Lebowski"
    }


List tenant contacts
--------------------

To get a list of all tenant contacts - issue GET request against **/api/exchange-tenants/<tenant_uuid>/contacts/**.
Only users with view access to tenant can view tenant contacts.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-tenants/24156c367e3a41eea81e374073fa1060/contacts/5b6d80ea-bb3e-4321-8722-fe8ab17ec649/",
            "id": "5b6d80ea-bb3e-4321-8722-fe8ab17ec649",
            "email": "alice@example.com",
            "name": "Joe Doe"
        }
    ]


Delete tenant contact
---------------------

To delete tenant contact - issue DELETE request against **/api/exchange-tenants/<tenant_uuid>/contacts/<contact_id>/**.


Create tenant distribution group
--------------------------------

To create new tenant distribution group - issue POST request against **/api/exchange-tenants/<tenant_uuid>/distgroups/**.

Request parameters:

 - name - distribution group name;
 - alias - username;
 - email - manager email;

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/distgroups/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "My Group",
        "alias": "my_grp",
        "email": "joe@test.com"
    }


List tenant distribution groups
-------------------------------

To get a list of all tenant distribution groups - issue GET request against
**/api/exchange-tenants/<tenant_uuid>/distgroups/**.
Only users with view access to tenant can view tenant distribution groups.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-tenants/24156c367e3a41eea81e374073fa1060/distgroups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/",
            "id": "99b7febb-4efb-4a2e-b183-6a0624e2e2b0",
            "email": "my_grp@test.com",
            "name": "My Group"
        }
    ]


Delete tenant distribution group
--------------------------------

To delete tenant distribution group - issue DELETE request against
**/api/exchange-tenants/<tenant_uuid>/distgroups/<distgroup_id>/**.


List distribution group members
-------------------------------

To get a list of all distribution group members - issue GET request against
**/api/exchange-tenants/<tenant_uuid>/distgroups/<distgroup_id>/**.
Only users with view access to tenant can view tenant distribution group members.

Response example:

.. code-block:: javascript

    [
        {
            "id": "99b7febb-4efb-4a2e-b183-6a0624e2e2b0",
            "email": "joe@test.com",
            "name": "Joe Doe"
        }
    ]


Add member to distribution group
--------------------------------

To add new member to distribution group - issue POST request against
**/api/exchange-tenants/<tenant_uuid>/distgroups/<distgroup_id>/add_member/**.

Request parameters:

 - user_id - new member ID

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/distgroups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/add_member/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "user_id": "e941ccc0-75cd-46ab-9c03-a4cda0b62b99"
    }


Delete member from distribution group
-------------------------------------

To remove member from distribution group - issue POST request against
**/api/exchange-tenants/<tenant_uuid>/distgroups/<distgroup_id>/del_member/**.

Request parameters:

 - user_id - member ID

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/distgroups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/del_member/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "user_id": "e941ccc0-75cd-46ab-9c03-a4cda0b62b99"
    }



MS Sharepoint
=============

Create a site
-------------
Site is a SaltStack resource which represents MS Sharepoint site.
A new site can be created by users with project administrator role, customer owner role or with
staff privilege (is_staff=True). To create a site, client must issue POST request to **/api/sharepoint-sites/** with
parameters:

 - name - Site name;
 - description - Description (optional);
 - link to the service-project-link object;
 - domain - Domain name;
 - storage_size - Storage size (one of: small, medium, large);


 Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-sites/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "my-site",
        "service_project_link": "http://example.com/api/saltstack-service-project-link/1/",
        "domain": "test.com",
        "storage_size": "small"
    }


Site display
------------

To get site data - issue GET request against **/api/sharepoint-sites/<site_uuid>/**.

Example rendering of the site object:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/sharepoint-sites/7693d9308e0641baa95720d0046e5696/",
            "uuid": "7693d9308e0641baa95720d0046e5696",
            "name": "my-site",
            "description": "",
            "start_time": null,
            "service": "http://example.com/api/saltstack/655b79490b63442d9264d76ab9478f62/",
            "service_name": "My SaltStack",
            "service_uuid": "655b79490b63442d9264d76ab9478f62",
            "project": "http://example.com/api/projects/0e86f04bb1fd48e181742d0598db69d5/",
            "project_name": "My Project",
            "project_uuid": "0e86f04bb1fd48e181742d0598db69d5",
            "customer": "http://example.com/api/customers/3b0fc2c0f0ed4f40b26126dc9cbd8f9f/",
            "customer_name": "Me",
            "customer_native_name": "",
            "customer_abbreviation": "",
            "project_groups": [],
            "resource_type": "SaltStack.Site",
            "state": "Online",
            "created": "2015-10-20T10:35:19.146Z",
        }
    ]


Delete site
-----------

To delete site - issue DELETE request against **/api/sharepoint-sites/<site_uuid>/**.
