List templates
--------------

Templates synced automatically from backend after service settings creation or on daily basis.
To get a list of templates - issue GET request against **/api/sharepoint-templates/**.

Filtering is possible by:

- ?name
- ?domain

Ordering is possible by: name, domain.

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
Tenant is a SaltStack resource which represents MS SharePoint tenant with domain. A tenant can have multiple
site collections and users.

A new tenant can be created by users with project administrator role, customer owner role or with
staff privilege (is_staff=True). To create a tenant, client must issue POST request to **/api/sharepoint-tenants/** with
parameters:

 - name - tenant name;
 - link to the service-project-link object;
 - domain - domain name;
 - description - tenant description;
 - storage - tenant storage size (MB);
 - user_count - number of users;


 Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-tenants/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "test tenant",
        "service_project_link": "http://example.com/api/saltstack-service-project-link/2/",
        "domain": "myspace.example.com",
        "description": "My space",
        "storage": 2048,
        "user_count": 10
    }


Tenant lifecycle
----------------

SharePoint tenant creation leads to setup of the basic pre-requisites for managing domain. However, for proper
operation tenant needs to be initialized with a main, private and admin site collections. To do that, a user must
first be created that can be assigned as a manager for those site collections.

Before tenant is initialized, it is not possible to add additional site collections. To initialize a SharePoint tenant
the following steps must be done:

 1. Create at least one user that will have administrative privileges on the main site collection.
 2. Request initialisation of the tenant by issuing POST request to **/api/sharepoint-tenants/<tenant_uuid>/initialize/**
    with the payload defining:

    - name - name of the main site collection;
    - description - description of the main site collection;
    - template - link to a site collection template;
    - storage - size of a quota for the main site collection (in MBs);
    - user - link to a user, who will be granted administrative privileges.


    For example, the payload could look like:

    .. code-block:: javascript

        {
            "template": "http://example.com/api/sharepoint-templates/6fce60a7f8094b7f8579024b41835d6f/",
            "user": "http://akara.me/api/sharepoint-users/d1d5a5e24fe940c9aea9640e176684de/",
            "storage": 100
        }

To track the status of the tenant use its **initialization_status** field. Possible values are:

 - Not initialized
 - Initializing
 - Initialized
 - Initialization failed

Tenant display
--------------

To get tenant data - issue GET request against **/api/sharepoint-tenants/<tenant_uuid>/**.

- access_url - Main site collection URL
- admin_url - ???
- management_ip - IP of the main site collection. Make sure it resolves to the domain. (Optional)

Example rendering of the tenant object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/sharepoint-tenants/178adb40c1a24a8ab95e4dbc1a0bc213/",
        "uuid": "178adb40c1a24a8ab95e4dbc1a0bc213",
        "name": "test-sharepoint-deployment",
        "description": "",
        "start_time": null,
        "service": "http://example.com/api/saltstack/e21602aa438d4a1aa03cf5d43d101a63/",
        "service_name": "MS Services",
        "service_uuid": "e21602aa438d4a1aa03cf5d43d101a63",
        "project": "http://example.com/api/projects/5490794d01f84f1d832137149442f664/",
        "project_name": "SharePoint project",
        "project_uuid": "5490794d01f84f1d832137149442f664",
        "customer": "http://example.com/api/customers/236f25fedf794e2da511b2d2763746ae/",
        "customer_name": "SharePoint customer",
        "customer_native_name": "",
        "customer_abbreviation": "",
        "project_groups": [],
        "tags": [],
        "error_message": "",
        "resource_type": "SaltStack.SharepointTenant",
        "state": "Provisioning Scheduled",
        "created": "2016-01-25T14:11:55.567Z",
        "backend_id": "",
        "access_url": null,
        "domain": "test-sharepoint-deployment.com",
        "quotas": [
            {
                "url": "http://example.com/api/quotas/459e26dc90384c7296bf530af5b25858/",
                "uuid": "459e26dc90384c7296bf530af5b25858",
                "name": "user_count",
                "limit": 10.0,
                "usage": 0.0,
                "scope": "http://example.com/api/sharepoint-tenants/178adb40c1a24a8ab95e4dbc1a0bc213/"
            },
            {
                "url": "http://example.com/api/quotas/f5f78821bee8463397f4cc63a648d84d/",
                "uuid": "f5f78821bee8463397f4cc63a648d84d",
                "name": "storage",
                "limit": 200.0,
                "usage": 0.0,
                "scope": "http://example.com/api/sharepoint-tenants/178adb40c1a24a8ab95e4dbc1a0bc213/"
            }
        ],
        "initialization_status": "Not initialized",
        "admin_url": null,
        "management_ip": "10.1.10.1"
    }


Update tenant
-------------

Only tenant name and description could be updated.

For tenant update - execute PUT request to **/api/sharepoint-tenants/<tenant_uuid>/** with parameters:

 - name - tenant new name;
 - description - tenant new description;


 Example of a valid request:

.. code-block:: http

    PUT /api/sharepoint-tenants/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "tenant new name",
        "description": "tenant new description"
    }


Delete tenant
-------------

To delete tenant - issue DELETE request against **/api/sharepoint-tenants/<tenant_uuid>/**.


List users
----------

To get list of users - issue GET request against **/api/sharepoint-users/**

Filtering is possible by:

- ?name
- ?username
- ?email
- ?first_name
- ?last_name
- ?tenant_uuid
- ?tenant=<tenant URL>

Ordering is possible by: name, username, email, first_name, last_name.

Example:

.. code-block:: javascript

    [
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
    ]


Create user
-----------

To create new SharePoint user - issue POST request against **/api/sharepoint-users/**.

 - name - Display name;
 - email;
 - username;
 - last_name;
 - first_name;
 - link to a tenant;

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


Reset user password
-------------------

To reset user password - issue POST request against **/api/sharepoint-users/<user_uuid>/password/**.

Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-users/db82a52368ba4957ac2cdb6a37d22dee/password/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

Example of a valid response:

.. code-block:: javascript

    {
        "password": "eD0YQpc076cR"
    }

Delete user
-----------

To delete user - issue DELETE request against **/api/sharepoint-users/<user_uuid>/**.


Create site collection
----------------------

To create a new SharePoint site collection, issue POST request against **/api/sharepoint-site-collections/**.

 - name - site collection name;
 - site_url - site collection URL suffix;
 - description - site collection description;
 - storage - maximum storage quota size (MB);
 - link to a site collection template;
 - link to a user object - user will be configured as admin of site collection;

 Example of a valid request:

.. code-block:: http

    POST /api/sharepoint-site-collections/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "template": "http://example.com/api/sharepoint-templates/04e2a211df964967ad2e57796056bdb9/",
        "user": "http://example.com/api/sharepoint-users/d1d5a5e24fe940c9aea9640e176684de/",
        "site_url": "test",
        "name": "Test",
        "description": "Test portal",
        "storage": 100,
    }



Site collection display
-----------------------

To get site collection info, issue GET request against **/api/sharepoint-site-collections/<site_collection_uuid>/**.

Example rendering of the site object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/sharepoint-site-collections/2ec3edc4b46b4b04bef17f48667ce04f/",
        "uuid": "2ec3edc4b46b4b04bef17f48667ce04f",
        "user": "http://example.com/api/sharepoint-users/db39a1e2a4794c31b1c6dd656df8d7e5/",
        "quotas": [
            {
                "url": "http://example.com/api/quotas/587b4b252a7a4ea88b0d5217ef95cd7e/",
                "uuid": "587b4b252a7a4ea88b0d5217ef95cd7e",
                "name": "storage",
                "limit": 100.0,
                "usage": 0.0,
                "scope": "http://example.com/api/sharepoint-site-collections/2ec3edc4b46b4b04bef17f48667ce04f/"
            }
        ],
        "access_url": "http://pavel-test-sharepoint-606.com/sites/test-site-collection",
        "site_url": "test-site-collection",
        "name": "test-site-collection",
        "description": "test-site-collection"
    },


Delete site
-----------

To delete a site collection, issue DELETE request against **/api/sharepoint-site-collections/<site_collection_uuid>/**.
