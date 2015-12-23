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
        "domain": "test.io"
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

 - link to exchange tenant object;
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

 - link to exchange tenant object;
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



Endpoints to be implemented in future release
---------------------------------------------



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
            "name": "My Group",
            "members": [
                {
                    "id": "99b7febb-4efb-4a2e-b183-6a0624e2e2b0",
                    "email": "zak@somewhere.com",
                    "name": "Zak Son"
                }
            ],
        }
    ]


Delete tenant distribution group
--------------------------------

To delete tenant distribution group - issue DELETE request against
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/**.


Add member to distribution group
--------------------------------

To add new member to distribution group - issue POST request against
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/members/**.

Request parameters:

 - id - new member ID

Example of a request:

.. code-block:: http

    POST /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/groups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/members/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "id": "e941ccc0-75cd-46ab-9c03-a4cda0b62b99"
    }


Delete member from distribution group
-------------------------------------

To remove member from distribution group - issue DELETE request against
**/api/exchange-tenants/<tenant_uuid>/groups/<group_id>/members/**.

Request parameters:

 - id - member ID

Example of a request:

.. code-block:: http

    DELETE /api/exchange-tenants/24156c367e3a41eea81e374073fa1060/groups/99b7febb-4efb-4a2e-b183-6a0624e2e2b0/members/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "id": "e941ccc0-75cd-46ab-9c03-a4cda0b62b99"
    }
