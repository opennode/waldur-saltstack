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
 - storage - tenant storage size (MB), should not be less than 1024;
 - site_name - main site collection name;
 - site_description - main site collection description;
 - template - main site collection template;
 - notify - True if SMS with admin user should be send on its creation.
 - phone - phone number, required if "notify" is True;


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
        "site_name": "Main site",
        "site_description": "Awesome main site",
        "template": "http://example.com/api/sharepoint-templates/04e2a211df964967ad2e57796056bdb9/"
    }


Tenant display
--------------

To get tenant data - issue GET request against **/api/sharepoint-tenants/<tenant_uuid>/**.

- admin - user that was automatically created on tenant initialization as admin.
- main_site_collection, admin_site_collection - site collection that were created during tenant initialization.
- management_ip - IP of the main site collection. Make sure it resolves to the domain. (Optional)

Filtering is possible by:

- ?customer
- ?customer_uuid
- ?customer_name
- ?customer_native_name
- ?customer_abbreviation
- ?project
- ?project_uuid
- ?project_name
- ?project_group
- ?project_group_uuid
- ?project_group_name
- ?service_uuid
- ?service_name
- ?name
- ?description
- ?state
- ?uuid
- ?domain

Example rendering of the tenant object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/sharepoint-tenants/35f3ee225c8343f582adb5fe387f8e94/",
        "uuid": "35f3ee225c8343f582adb5fe387f8e94",
        "name": "test-tenant",
        "description": "test-tenant",
        "start_time": "2016-02-17T06:24:12.350Z",
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
        "state": "Online",
        "created": "2016-02-17T06:21:24.873Z",
        "backend_id": "NC_2AC92770A6",
        "access_url": "http://test-tenant.com",
        "domain": "test-tenant.com",
        "quotas": [
            {
                "url": "http://example.com/api/quotas/707471368b8e415e8caf58cea3c3057a/",
                "uuid": "707471368b8e415e8caf58cea3c3057a",
                "name": "user_count",
                "limit": -1.0,
                "usage": 1.0
            },
            {
                "url": "http://example.com/api/quotas/66401ba4737d43cc96c4f85da88ea19b/",
                "uuid": "66401ba4737d43cc96c4f85da88ea19b",
                "name": "storage",
                "limit": 1025.0,
                "usage": 0.0
            }
        ],
        "management_ip": "Unknown",
        "admin": {
            "url": "http://example.com/api/sharepoint-users/9a0394f7fe064fb4bdc15c89a2462ae9/",
            "uuid": "9a0394f7fe064fb4bdc15c89a2462ae9",
            "tenant": "http://example.com/api/sharepoint-tenants/35f3ee225c8343f582adb5fe387f8e94/",
            "tenant_uuid": "35f3ee225c8343f582adb5fe387f8e94",
            "tenant_domain": "test-tenant.com",
            "name": "Admin",
            "email": "admin@test-tenant.com",
            "first_name": "Admin",
            "last_name": "Admin",
            "username": "admin",
            "password": "b-6#urx@8149"
        },
        "admin_site_collection": {
            "url": "http://example.com/api/sharepoint-site-collections/271ae2431188428b9ce8e66122385938/",
            "uuid": "271ae2431188428b9ce8e66122385938",
            "template": "http://example.com/api/sharepoint-templates/34a623ba82fb4662b95452da1d74e167/",
            "template_code": "TENANTADMIN#0",
            "template_name": "Tenant Admin Site",
            "user": "http://example.com/api/sharepoint-users/9a0394f7fe064fb4bdc15c89a2462ae9/",
            "name": "Admin",
            "description": "Admin site collection",
            "quotas": [
                {
                    "url": "http://example.com/api/quotas/087780fb1860433db3cdb78e8095dc3f/",
                    "uuid": "087780fb1860433db3cdb78e8095dc3f",
                    "name": "storage",
                    "limit": 50.0,
                    "usage": 0.0
                }
            ],
            "site_url": "",
            "access_url": "http://test-tenant.com/admin"
        },
        "main_site_collection": {
            "url": "http://example.com/api/sharepoint-site-collections/f1ae7366c9b14bfb8e2ff5f0cfbe9a99/",
            "uuid": "f1ae7366c9b14bfb8e2ff5f0cfbe9a99",
            "template": "http://example.com/api/sharepoint-templates/452482cd1d024b5fbb6a09b38b0280af/",
            "template_code": "STS#0",
            "template_name": "Team Site",
            "user": "http://example.com/api/sharepoint-users/9a0394f7fe064fb4bdc15c89a2462ae9/",
            "name": "test-tenant-main-sc",
            "description": "test-tenant-main-sc-description",
            "quotas": [
                {
                    "url": "http://example.com/api/quotas/7c7e0f4ac38240b99a01e02ef03175e0/",
                    "uuid": "7c7e0f4ac38240b99a01e02ef03175e0",
                    "name": "storage",
                    "limit": 500.0,
                    "usage": 0.0
                }
            ],
            "site_url": "",
            "access_url": "http://test-tenant.com"
        }
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


Change tenant quotas
--------------------

To update tenant quotas - issue POST request against **/api/sharepoint-tenants/<tenant_uuid>/change_quotas/** with
parameters storage, (user_count quota is not editable).

Example of valid request:

.. code-block:: http

    POST /api/exchange-tenants/7693d9308e0641baa95720d0046e5696/change_quotas/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "storage": 2048
    }


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
Not initialized personal site collection will be automatically created on user creation.

 - name - Display name;
 - email;
 - username;
 - last_name;
 - first_name;
 - link to a tenant;
 - notify - True if user has to be notified with SMS on creation.
 - phone (required if "notify" is True);

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
        "username": "joe.doe",
        "notify": True,
        "phone": "123456789"
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
        "password": "l1LJ7UK2YZt0",
        "personal_site_collection": {
            "url": "http://127.0.0.1:8000/api/sharepoint-site-collections/7f6d8bdfe23549c597c9797bb995b8a3/",
            "uuid": "7f6d8bdfe23549c597c9797bb995b8a3",
            "template": null,
            "template_code": null,
            "template_name": null,
            "user": "http://127.0.0.1:8000/api/sharepoint-users/5f093dfd31f64e6eaaf5724cd02c61f1/",
            "name": "Personal",
            "description": "Personal site collection",
            "quotas": [
                {
                    "url": "http://127.0.0.1:8000/api/quotas/c7649c8b3091412090b5f475f69d68a3/",
                    "uuid": "c7649c8b3091412090b5f475f69d68a3",
                    "name": "storage",
                    "limit": 5.0,
                    "usage": 0.0
                }
            ],
            "site_url": "",
            "access_url": "http://pavel-test-sharepoint-706.com/my/personal/42dfa946621ba8b26b7c"
        }
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
        "storage": 100
    }


List site collections
---------------------

To get site collection list, issue GET request against **/api/sharepoint-site-collections/**.

The following filtering options are present (**?field_name=...**):

- name
- description
- access_url
- user_uuid
- template_uuid
- template_code
- template_name
- template_uuid
- tenant_uuid
- type - can be list. Choices: main, admin, personal, regular.


Site collection display
-----------------------

To get site collection info, issue GET request against **/api/sharepoint-site-collections/<site_collection_uuid>/**.

Example rendering of the site object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/sharepoint-site-collections/f38896cb1b7c472f9a7ccb865206dadd/",
        "uuid": "f38896cb1b7c472f9a7ccb865206dadd",
        "template": "http://example.com/api/sharepoint-templates/37f4d32bc4c94a40bfaac7eb02b493e6/",
        "template_code": "STS#0",
        "template_name": "Team Site",
        "user": "http://example.com/api/sharepoint-users/26b5e4e14b1e48ff82d1e7b663282a1d/",
        "name": "Personal",
        "description": "Personal site collection",
        "quotas": [
            {
                "url": "http://example.com/api/quotas/c726408671794852aa3791eb0467a309/",
                "uuid": "c726408671794852aa3791eb0467a309",
                "name": "storage",
                "limit": 1000.0,
                "usage": 0.0,
                "scope": "http://example.com/api/sharepoint-site-collections/f38896cb1b7c472f9a7ccb865206dadd/"
            }
        ],
        "site_url": "",
        "access_url": "http://ilja-test-780.com/",
        "deletable": false,
        "type": "regular"
     }


Delete site collection
----------------------

To delete a site collection, issue DELETE request against **/api/sharepoint-site-collections/<site_collection_uuid>/**.
Is is impossible to delete tenant initial site collections (main, personal and admin).


Change storage quota
--------------------

To change storage quota - issue POST or PUT request against
**/api/sharepoint-site-collections/<site_collection_uuid>/change_quotas/** with "storage" as parameter.

Endpoint will return error with status 409 if personal site collection was not initialized.

Example of valid request:

.. code-block:: http

    POST /api/sharepoint-site-collections/b05674b1063f42178267cc2f9ada2ace/change_quotas/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "storage": 200,
    }
