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
 - mailbox_size - Average mailboxes size (GB);


 Example of a valid request:

.. code-block:: http

    POST /api/exchange-tenants/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "TST",
        "service_project_link": "http://example.com/api/saltstack-service-project-link/1/",
        "domain": "test.com",
        "max_users": "500",
        "mailbox_size": "3"
    }


Tenant display
--------------

To get tenant data - issue GET request against **/api/exchange-tenants/<tenant_uuid>/**.

Example rendering of the tenant object:

.. code-block:: javascript

    {
        "url": "http://example.com/api/exchange-tenants/7693d9308e0641baa95720d0046e5696/",
        "uuid": "7693d9308e0641baa95720d0046e5696",
        "name": "TST",
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
        "error_message": "",
        "resource_type": "SaltStack.ExchangeTenant",
        "state": "Online",
        "created": "2015-10-20T10:35:19.146Z",
        "domain": "test.com",
        "max_users": "500",
        "mailbox_size": "3",
        "owa_url": "https://owa.example.com",
        "ecp_url": "https://ecp.example.com"
    }


Update tenant details
---------------------

To update details of a MS Exchange tenant, issue PUT request against **/api/exchange-tenants/<tenant_uuid>/**.

Example of a valid request:

.. code-block:: http

    POST /api/exchange-tenants/7693d9308e0641baa95720d0046e5696/domain/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "name": "test.io",
        "description": "My new domain"
    }


Change tenant domain name
-------------------------

To update tenant domain - issue PUT request against **/api/exchange-tenants/<tenant_uuid>/domain/**.

Example of a valid request:

.. code-block:: http

    PUT /api/exchange-tenants/7693d9308e0641baa95720d0046e5696/domain/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "domain": "test.io"
    }


Delete tenant
-------------

To delete tenant - issue DELETE request against **/api/exchange-tenants/<tenant_uuid>/**.


List users
----------

To get a list of all users - issue GET request against **/api/exchange-users/**.
Only users with view access to tenant can view tenant users.

Filtering and ordering is possible by:

- ?name=XXX
- ?email=XXX
- ?username=XXX
- ?first_name=XXX
- ?last_name=XXX
- ?mailbox_size=XXX
- ?tenant_uuid=XXX

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-users/8d3f1e878b2345a7a65f28d426e85137/",
            "uuid": "8d3f1e878b2345a7a65f28d426e85137",
            "tenant": "http://example.com/api/exchange-tenants/9baf2ec31a624ab78e348758b668f36d/",
            "tenant_uuid": "9baf2ec31a624ab78e348758b668f36d",
            "tenant_domain": "test.com",
            "name": "Joe D",
            "first_name": "Joe",
            "last_name": "Doe",
            "username": "joe.doe",
            "password": "?lU_YmOi_vO=",
            "mailbox_size": 5,
            "email": "joe.doe@test.com"
        }
    ]


Create user
-----------

To create new user - issue POST request against **/api/exchange-users/**.

Request parameters:

 - tenant - link to exchange tenant object;
 - name - user name;
 - username - user username;
 - last_name - user last name;
 - first_name - user first name;
 - mailbox_size - mailbox size (Mb);
 - manager - user manager (optional);
 - office - user office name (optional);
 - phone - user phone (optional);
 - department - user department (optional);
 - company - user company name (optional);
 - title - user title (optional);
 - notify - whether to SMS temp password to user (optional);

Example of a request:

.. code-block:: http

    POST /api/exchange-users/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "tenant": "http://example.com/api/exchange-tenants/7693d9308e0641baa95720d0046e5696/",
        "name": "Joe D",
        "username": "joe.d",
        "first_name": "Joe",
        "last_name": "Doe",
        "mailbox_size": "5"
        "office": "office",
        "phone": "21323211,
        "department": "test department",
        "company": "test company",
        "title": "Joe",
        "notify": true,
        "manager": "http://example.com/api/exchange-users/b5b164ffbc434bbaaad15d4ae8f6a979/"
    }


Update user
-----------

To update user data - issue PUT or PATCH request against **/api/exchange-users/<user_uuid>/**.


Reset user password
-------------------

To reset user password - issue POST request against **/api/exchange-users/<user_uuid>/password/**.

Example of a valid request:

.. code-block:: http

    POST /api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/password/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "password": "eD0YQpc076cR",
        "notify": true
    }


Delete user
-----------

To delete user - issue DELETE request against **/api/exchange-users/<user_uuid>/**.


List contacts
-------------

To get a list of all contacts - issue GET request against **/api/exchange-contacts/**.
Only users with view access to tenant can view tenant contacts.

Filtering is possible by:

- ?name=XXX
- ?email=XXX
- ?first_name=XXX
- ?last_name=XXX
- ?tenant_uuid=XXX

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-contacts/b6086d0ff2ec4357bc5f34ec22e82b84/",
            "uuid": "b6086d0ff2ec4357bc5f34ec22e82b84",
            "tenant": "http://example.com/api/exchange-tenants/7f1d21d48b9c46228c2991c02a070121/",
            "tenant_uuid": "7f1d21d48b9c46228c2991c02a070121",
            "tenant_domain": "test.io",
            "name": "Joe",
            "email": "joe@me.com",
            "first_name": "Joe",
            "last_name": "Doe"
        }
    ]


Create contact
--------------

To create new contact - issue POST request against **/api/exchange-contacts/**.

Request parameters:

 - tenant - link to exchange tenant object;
 - name - contact name;
 - email - contact email;
 - last_name - contact last name;
 - first_name - contact first name;

Example of a request:

.. code-block:: http

    POST /api/exchange-contacts/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "tenant": "http://example.com/api/exchange-tenants/7693d9308e0641baa95720d0046e5696/",
        "name": "Joe",
        "email": "joe@example.com",
        "first_name": "Joe",
        "last_name": "Doe"
    }


Update contact
--------------

To update contact data - issue PUT or PATCH request against **/api/exchange-contacts/<contact_uuid>/**.


Delete contact
--------------

To delete contact - issue DELETE request against **/api/exchange-contacts/<contact_uuid>/**.


List distribution groups
------------------------

To get a list of all distribution groups - issue GET request against **/api/exchange-groups/**.
Only users with view access to tenant can view tenant distribution groups.

Filtering is possible by:

- ?name=XXX
- ?username=XXX
- ?tenant_domain=XXX
- ?tenant_uuid=XXX

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-groups/c39cc7f57fab499786609298019cf844/",
            "uuid": "c39cc7f57fab499786609298019cf844",
            "tenant": "http://example.com/api/exchange-tenants/7f1d21d48b9c46228c2991c02a070121/",
            "tenant_uuid": "7f1d21d48b9c46228c2991c02a070121",
            "tenant_domain": "test.com",
            "manager": "http://example.com/api/exchange-users/faf0ed086efd42c08e477797364a78f3/",
            "manager_uuid": "faf0ed086efd42c08e477797364a78f3",
            "manager_name": "Big Joe",
            "name": "My Group",
            "username": "grp",
            "email": "grp@test.com",
            "members": [
                "http://example.com/api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/",
                "http://example.com/api/exchange-users/faf0ed086efd42c08e477797364a78f3/"
            ]
        }
    ]


Create distribution group
-------------------------

To create distribution group - issue POST request against **/api/exchange-groups/**.

Request parameters:

 - tenant - link to exchange tenant object;
 - manager - link to exchange user object;
 - name - distribution group name;
 - username - group username;
 - members - a list of group members' links;

Example of a request:

.. code-block:: http

    POST /api/exchange-groups/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "tenant": "http://example.com/api/exchange-tenants/7f1d21d48b9c46228c2991c02a070121/",
        "manager": "http://example.com/api/exchange-users/faf0ed086efd42c08e477797364a78f3/",
        "name": "My Group",
        "username": "grp",
        "members": [
            "http://example.com/api/exchange-users/ee6ca4b2929c46cb85bedb276a937ac2/"
        ]
    }


Update distribution group
-------------------------

To update distribution group data - issue PUT or PATCH request against **/api/exchange-groups/<group_uuid>/**.


Delete distribution group
-------------------------

To delete distribution group - issue DELETE request against **/api/exchange-groups/<group_uuid>/**.


Change group members
--------------------

To change distribution group members - issue PUT or PATCH request against **/api/exchange-groups/<group_uuid>/**.

Request parameters:

 - members - a list of links to exchange user objects, that should be in group;

Example of a requests:

1. Add 2 users to group:

.. code-block:: http

    PATCH /api/exchange-groups/c39cc7f57fab499786609298019cf844/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "members": [
            "http://example.com/api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/",
            "http://example.com/api/exchange-users/faf0ed086efd42c08e477797364a78f3/"
        ]
    }

2. Add another one user:

.. code-block:: http

    PATCH /api/exchange-groups/c39cc7f57fab499786609298019cf844/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "members": [
            "http://example.com/api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/",
            "http://example.com/api/exchange-users/faf0ed086efd42c08e477797364a78f3/",
            "http://example.com/api/exchange-users/9baf2ec31a624ab78e348758b668f36d/"
        ]
    }

3. Remove all users:

.. code-block:: http

    PATCH /api/exchange-groups/c39cc7f57fab499786609298019cf844/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "members": []
    }


List group members
------------------

To get a list of all distribution group members - issue GET request against **/api/exchange-groups/<group_uuid>/members/**.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-users/77a5451549854258820ae211b473ce9b/",
            "uuid": "77a5451549854258820ae211b473ce9b",
            "tenant": "http://example.com/api/exchange-tenants/9760d685cbad4fa4b3255d6ffd917393/",
            "tenant_uuid": "9760d685cbad4fa4b3255d6ffd917393",
            "tenant_domain": "test.com",
            "name": "Ivan P",
            "first_name": "Ivan",
            "last_name": "Petrov",
            "username": "ivan.p",
            "password": "Y16j$Keub@G",
            "mailbox_size": 2,
            "office": "",
            "phone": "",
            "department": "",
            "company": "",
            "title": "",
            "manager": null,
            "email": "ivan.p@test.com"
        },
        {
            "url": "http://example.com/api/exchange-users/ee6ca4b2929c46cb85bedb276a937ac2/",
            "uuid": "ee6ca4b2929c46cb85bedb276a937ac2",
            "tenant": "http://example.com/api/exchange-tenants/9760d685cbad4fa4b3255d6ffd917393/",
            "tenant_uuid": "9760d685cbad4fa4b3255d6ffd917393",
            "tenant_domain": "test.com",
            "name": "Zoe",
            "first_name": "Zoe",
            "last_name": "Chloe",
            "username": "zoe",
            "password": "pBo07@WZ-te",
            "mailbox_size": 2,
            "office": "",
            "phone": "",
            "department": "",
            "company": "",
            "title": "",
            "manager": null,
            "email": "zoe@test.com"
        }
    ]
