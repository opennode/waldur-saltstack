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
