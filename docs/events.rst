Events
++++++

SaltStack application emits several events messages documented below.

Generic
=======

Several models in SaltStack application are considered to be properties of the particular remotely managed application.

Each event message contains in the context a **property_type** parameter specifying exact model. Currently existing are:

- exchange.user
- exchange.group
- exchange.contact
- exchange.conferenceroom
- sharepoint.user
- sharepoint.sitecollection
- sharepoint.template

.. glossary::

    **saltstack_property_creation_succeeded**
        A service property creation has succeeded.

    **saltstack_property_update_succeeded**
        A service property update has succeeded.

    **saltstack_property_deletion_succeeded**
        A service property deletion has succeeded.

------------

.. glossary::

    **exchange_user_password_reset**
        Exchange user password has been reset.

------------

.. glossary::

    **sharepoint_user_password_reset**
        SharePoint user password has been reset.

    **sharepoint_site_collection_quota_update**
        SharePoint site collection quota has been updated.
