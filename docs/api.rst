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
        "name": "My SaltStack"
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


Create a domain
---------------
Domain is a SaltStack resource which represents MS Exchange domain.
A new domain can be created by users with project administrator role, customer owner role or with
staff privilege (is_staff=True). To create a domain, client must issue POST request to **/api/saltstack-domains/** with
parameters:

 - name - Bucket name;
 - description - Description (optional);
 - link to the service-project-link object;
 - domain - Domain name;
 - bucket_size - Bucket size (one of: small, medium, large);
 - mailbox_size - Average mailboxes size (Gb);


 Example of a valid request:

.. code-block:: http

    POST /api/saltstack-domains/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "my-domain",
        "service_project_link": "http://example.com/api/saltstack-service-project-link/1/",
        "domain": "test.com",
        "bucket_size": "small",
        "mailbox_size": "10"
    }


Domain display
--------------

To get domain data - issue GET request against **/api/saltstack-domains/<domain_uuid>/**.

Example rendering of the domain object:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/saltstack-domains/7693d9308e0641baa95720d0046e5696/",
            "uuid": "7693d9308e0641baa95720d0046e5696",
            "name": "my-domain",
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
            "resource_type": "SaltStack.Domain",
            "state": "Online",
            "created": "2015-10-20T10:35:19.146Z"
        }
    ]


Delete domain
-------------

To delete domain - issue DELETE request against **/api/saltstack-domains/<domain_uuid>/**.


List domain mailboxes
---------------------

To get list of all registered on domain mailboxes - issue GET request against **/api/saltstack-domains/<domain_uuid>/users/**.
Only users with view access to domain can view domain users.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/saltstack-domains/24156c367e3a41eea81e374073fa1060/users/a67a5b55-bb5f-1259-60a2-562e3c88fb34/",
            "id": "a67a5b55-bb5f-1259-60a2-562e3c88fb34",
            "email": "joe@test.com",
            "first_name": "Joe",
            "last_name": "Doe",
            "mailbox_size": "50"
        }
    ]


Create new domain mailbox
-------------------------

To create new domain mailbox - issue POST request against **/api/saltstack-domains/<domain_uuid>/users/**.

Request parameters:

 - email - new user email;
 - last_name - new user last name;
 - first_name - new user first name;
 - mailbox_size - mailbox size (Mb);


Example of a request:


.. code-block:: http

    POST /api/saltstack/24156c367e3a41eea81e374073fa1060/users/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "email": "alice@example.com"
        "last_name": "Alice",
        "last_name": "Lebowski",
        "mailbox_size": "20"
    }


Delete domain mailbox
---------------------

To delete domain mailbox - issue DELETE request against **/api/saltstack-domains/<domain_uuid>/users/<user_id>/**.


Create a site
-------------
Site is a SaltStack resource which represents MS Sharepoint site.
A new site can be created by users with project administrator role, customer owner role or with
staff privilege (is_staff=True). To create a site, client must issue POST request to **/api/saltstack-sites/** with
parameters:

 - name - Site name;
 - description - Description (optional);
 - link to the service-project-link object;
 - domain - Domain name;
 - storage_size - Storage size (one of: small, medium, large);


 Example of a valid request:

.. code-block:: http

    POST /api/saltstack-sites/ HTTP/1.1
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

To get site data - issue GET request against **/api/saltstack-sites/<site_uuid>/**.

Example rendering of the site object:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/saltstack-sites/7693d9308e0641baa95720d0046e5696/",
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

To delete site - issue DELETE request against **/api/saltstack-sites/<site_uuid>/**.
