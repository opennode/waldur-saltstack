from nodeconductor.logging.log import EventLogger, event_logger
from nodeconductor_saltstack.sharepoint.models import User, SiteCollection


class SharepointUserEventLogger(EventLogger):
    affected_user = User

    class Meta:
        event_types = (
            'sharepoint_user_password_reset',
        )


class SharepointSiteCollectionEventLogger(EventLogger):
    site_collection = SiteCollection

    class Meta:
        event_types = (
            'sharepoint_site_collection_quota_update',
        )


event_logger.register('sharepoint_user', SharepointUserEventLogger)
event_logger.register('sharepoint_site_collection', SharepointSiteCollectionEventLogger)
