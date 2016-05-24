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

    **exchange_tenant_quota_update**
        Exchange tenant quota has been updated.

    **exchange_tenant_domain_change**
        Exchange tenant domain has been changed.

    **exchange_group_member_add**
        Member has been added to distribution group.

    **exchange_group_member_remove**
        Member has been removed from distribution group.

    **exchange_group_delivery_member_add**
        Delivery member has been added to distribution group.

    **exchange_group_delivery_member_remove**
        Delivery member has been removed from distribution group.

    **exchange_user_send_on_behalf_member_add**
        Send On Behalf member was added to exchange user.

    **exchange_user_send_on_behalf_member_remove**
        Send On Behalf member was removed from exchange user.

    **exchange_user_send_as_member_add**
        Send As member was added to exchange user.

    **exchange_user_send_as_member_remove**
        Send As member was removed from exchange user.

------------

.. glossary::

    **sharepoint_user_password_reset**
        SharePoint user password has been reset.

    **sharepoint_site_collection_quota_update**
        SharePoint site collection quota has been updated.

    **sharepoint_tenant_quota_update**
        SharePoint tenant quota has been updated.
