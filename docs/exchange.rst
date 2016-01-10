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
        "mailbox_size": "3"
    }


Change tenant domain name
-------------------------

To update tenant domain - issue PUT request against **/api/exchange-tenants/<tenant_uuid>/**.

Example of a valid request:

.. code-block:: http

    PUT /api/exchange-tenants/7693d9308e0641baa95720d0046e5696/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "domain": "test.io",
        "description": "my domain"
    }


Delete tenant
-------------

To delete tenant - issue DELETE request against **/api/exchange-tenants/<tenant_uuid>/**.


List users
----------

To get a list of all users - issue GET request against **/api/exchange-users/**.
Only users with view access to tenant can view tenant users.

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
            "mailbox_size": 5
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
    }


Update user
-----------

To update user data - issue PUT or PATCH request against **/api/exchange-users/<user_uuid>/**.


Delete user
-----------

To delete user - issue DELETE request against **/api/exchange-users/<user_uuid>/**.


List contacts
-------------

To get a list of all contacts - issue GET request against **/api/exchange-contacts/**.
Only users with view access to tenant can view tenant contacts.

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
- ?tenant_domain=XXX
- ?username=XXX

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-groups/c39cc7f57fab499786609298019cf844/",
            "uuid": "c39cc7f57fab499786609298019cf844",
            "tenant": "http://example.com/api/exchange-tenants/7f1d21d48b9c46228c2991c02a070121/",
            "tenant_uuid": "7f1d21d48b9c46228c2991c02a070121",
            "tenant_domain": "test.io",
            "manager": "http://example.com/api/exchange-users/faf0ed086efd42c08e477797364a78f3/",
            "manager_uuid": "faf0ed086efd42c08e477797364a78f3",
            "manager_name": "Big Joe",
            "name": "My Group",
            "username": "grp"
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
        "username": "grp"
    }


Update distribution group
-------------------------

To update distribution group data - issue PUT or PATCH request against **/api/exchange-groups/<group_uuid>/**.


Delete distribution group
-------------------------

To delete distribution group - issue DELETE request against **/api/exchange-groups/<group_uuid>/**.


List group members
------------------

To get a list of all distribution group memberss - issue GET request against **/api/exchange-groups/<group_uuid>/members**.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/",
            "uuid": "db82a52368ba4957ac2cdb6a37d22dee",
            "tenant": "http://example.com/api/exchange-tenants/9baf2ec31a624ab78e348758b668f36d/",
            "tenant_uuid": "9baf2ec31a624ab78e348758b668f36d",
            "tenant_domain": "test.com",
            "name": "Alice",
            "first_name": "Alice",
            "last_name": "L",
            "username": "alice",
            "password": "eD0YQpc076cR",
            "mailbox_size": 3
        }
    ]


Add member to group
-------------------

To add new member to distribution group - issue POST request against **/api/exchange-groups/<group_uuid>/members/**.

Request parameters:

 - user - link to exchange user object;

Example of a request:

.. code-block:: http

    POST /api/exchange-groups/c39cc7f57fab499786609298019cf844/members/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "user": "http://example.com/api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/"
    }


Delete member from group
------------------------

To remove member from distribution group - issue DELETE request against **/api/exchange-groups/<group_uuid>/members/**.

Request parameters:

 - user - link to exchange user object;

Example of a request:

.. code-block:: http

    DELETE /api/exchange-groups/c39cc7f57fab499786609298019cf844/members/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "user": "http://example.com/api/exchange-users/db82a52368ba4957ac2cdb6a37d22dee/"
    }
