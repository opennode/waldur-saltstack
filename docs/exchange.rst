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

    [
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
            "resource_type": "SaltStack.Tenant",
            "state": "Online",
            "created": "2015-10-20T10:35:19.146Z",
            "domain": "test.com",
            "max_users": "500",
            "mailbox_size": "3"
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

To create new tenant distribution group - issue POST request against **/api/exchange-tenants/<tenant_uuid>/groups/**.

Request parameters:

 - name - distribution group name;
 - alias - username;
 - email - manager email;

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/groups/ HTTP/1.1
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
**/api/exchange-tenants/<tenant_uuid>/groups/**.
Only users with view access to tenant can view tenant distribution groups.

Response example:

.. code-block:: javascript

    [
        {
            "url": "http://example.com/api/exchange-tenants/24156c367e3a41eea81e374073fa1060/groups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/",
            "id": "99b7febb-4efb-4a2e-b183-6a0624e2e2b0",
            "email": "my_grp@test.com",
            "name": "My Group"
        }
    ]


Delete tenant distribution group
--------------------------------

To delete tenant distribution group - issue DELETE request against
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/**.


List distribution group members
-------------------------------

To get a list of all distribution group members - issue GET request against
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/**.
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
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/add_member/**.

Request parameters:

 - user_id - new member ID

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/groups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/add_member/ HTTP/1.1
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
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/del_member/**.

Request parameters:

 - user_id - member ID

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/groups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/del_member/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "user_id": "e941ccc0-75cd-46ab-9c03-a4cda0b62b99"
    }
