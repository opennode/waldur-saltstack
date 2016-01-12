List templates
--------------

Templates synced automatically from backend after service settings creation or on daily basis.
To get a list of templates - issue GET request against **/api/sharepoint-templates/**.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/sharepoint-templates/04e2a211df964967ad2e57796056bdb9/",
            "uuid": "04e2a211df964967ad2e57796056bdb9",
            "name": "Team Site",
            "code": "STS#0"
        },
        {
            "url": "http://example.com/api/sharepoint-templates/6fce60a7f8094b7f8579024b41835d6f/",
            "uuid": "6fce60a7f8094b7f8579024b41835d6f",
            "name": "Blog",
            "code": "BLOG#0"
        }

    ]


Create a tenant
---------------
Tenant is a SaltStack resource which represents MS Sharepoint Domain.
A new tenant can be created by users with project administrator role, customer owner role or with
staff privilege (is_staff=True). To create a tenant, client must issue POST request to **/api/sharepoint-tenants/** with
parameters:

 - name - Tenant name;
 - link to the service-project-link object;
 - link to template object;
 - domain - Domain name;
 - site_name - Site name;
 - description - Site description;
 - storage_size - Site storage size (GB);
 - users_count - Number of users;


 Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-tenants/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "TST",
        "service_project_link": "http://example.com/api/saltstack-service-project-link/2/",
        "template": "http://example.com/api/sharepoint-templates/6fce60a7f8094b7f8579024b41835d6f/",
        "domain": "blog.com",
        "site_name": "Blog",
        "description": "My blog",
        "storage_size": 2.5,
        "users_count": 10
    }


Tenant display
--------------

To get tenant data - issue GET request against **/api/sharepoint-tenants/<tenant_uuid>/**.

Example rendering of the tenant object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/sharepoint-tenants/8194584bc21449ccbe60509ec34b03e2/",
        "uuid": "8194584bc21449ccbe60509ec34b03e2",
        "name": "TST",
        "description": "My blog",
        "start_time": null,
        "service": "http://example.com/api/saltstack/90f701dd4b804d39bafd8509b70f1594/",
        "service_name": "My SaltStack",
        "service_uuid": "90f701dd4b804d39bafd8509b70f1594",
        "project": "http://example.com/api/projects/3c8e7478f131493aafdd5c450caaf925/",
        "project_name": "My Project",
        "project_uuid": "3c8e7478f131493aafdd5c450caaf925",
        "customer": "http://example.com/api/customers/1040561ca9e046d2b74268600c7e1105/",
        "customer_name": "Me",
        "customer_native_name": "Joe Doe",
        "customer_abbreviation": "JD",
        "project_groups": [
            {
                "url": "http://example.com/api/project-groups/e5cf9b2efc664c82a2dfe9450c7f6b63/",
                "name": "Basic",
                "uuid": "e5cf9b2efc664c82a2dfe9450c7f6b63"
            }
        ],
        "tags": [],
        "error_message": "",
        "resource_type": "SaltStack.SharepointTenant",
        "state": "Offline",
        "created": "2015-12-14T16:49:12.597Z",
        "backend_id": "f5469eea-4c5c-45b7-97f6-50e80c83916e",
        "domain": "blog.com",
        "site_name": "Blog",
        "site_url": "http://blog.com/my",
        "admin_url": "http://blog.com/admin",
        "admin_login": "tenantadmin@blog.com",
        "admin_password": "k?6y#3$+0=@a",
        "management_ip": "10.7.7.0"
    }


Update tenant quotas
--------------------

To update tenant quotas - issue POST request against **/api/sharepoint-tenants/<tenant_uuid>/set_quotas/**.

Example of a valid request:

.. code-block:: http

    PUT /api/sharepoint-tenants/8194584bc21449ccbe60509ec34b03e2/set_quotas/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "storage_size": 5,
        "users_count": 20
    }


Delete tenant
-------------

To delete tenant - issue DELETE request against **/api/sharepoint-tenants/<tenant_uuid>/**.


Create user
-----------

To create new sharepoint user - issue POST request against **/api/sharepoint-users/**.

 - name - Display name;
 - email;
 - username;
 - last_name;
 - first_name;
 - link to tenant object;

 Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-users/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "tenant": "http://example.com/api/sharepoint-tenants/8194584bc21449ccbe60509ec34b03e2/",
        "name": "Joe",
        "email": "joe@email.com",
        "first_name": "Joe",
        "last_name": "Doe",
        "username": "joe.doe"
    }


User display
------------

To get user data - issue GET request against **/api/sharepoint-users/<user_uuid>/**.

Example rendering of the user object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/sharepoint-users/d1d5a5e24fe940c9aea9640e176684de/",
        "uuid": "d1d5a5e24fe940c9aea9640e176684de",
        "tenant": "http://example.com/api/sharepoint-tenants/8194584bc21449ccbe60509ec34b03e2/",
        "tenant_uuid": "8194584bc21449ccbe60509ec34b03e2",
        "tenant_domain": "blog.com",
        "name": "Joe",
        "email": "joe@email.com",
        "first_name": "Joe",
        "last_name": "Doe",
        "username": "joe.doe",
        "password": "l1LJ7UK2YZt0"
    }


Update user
-----------

To update user data - issue PUT or PATCH request against **/api/sharepoint-users/<user_uuid>/**.


Delete user
-----------

To delete user - issue DELETE request against **/api/sharepoint-users/<user_uuid>/**.


Endpoints to be implemented in future release
---------------------------------------------


Create site
-----------

To create new sharepoint site - issue POST request against **/api/sharepoint-sites/**.

 - name - Site name;
 - site_url - Site URL;
 - description - Site description;
 - max_quota - Maximum site quota (GB);
 - warn_quota - Warning quota (GB);
 - link to template object;
 - link to user object;

 Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-sites/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "template": "http://example.com/api/sharepoint-templates/04e2a211df964967ad2e57796056bdb9/",
        "user": "http://example.com/api/sharepoint-users/d1d5a5e24fe940c9aea9640e176684de/",
        "site_url": "/test",
        "name": "Test",
        "description": "Test portal",
        "max_quota": 5,
        "warn_quota": 3
    }


Site display
------------

To get site data - issue GET request against **/api/sharepoint-sites/<site_uuid>/**.

Example rendering of the site object:

.. code-block:: javascript

    {
        "url": "http://akara.me/api/sharepoint-sites/0c0d58331274477585a4ef16e0e67efa/",
        "uuid": "0c0d58331274477585a4ef16e0e67efa",
        "user": "http://akara.me/api/sharepoint-users/d1d5a5e24fe940c9aea9640e176684de/",
        "site_url": "http://blog.come/sites/test",
        "name": "Test",
        "description": "Test portal"
    }


Delete site
-----------

To delete site - issue DELETE request against **/api/sharepoint-sites/<site_uuid>/**.
