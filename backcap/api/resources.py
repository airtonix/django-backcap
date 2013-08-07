import logging

from tastypie import resources

from .. import models
from .. import settings
from .. import utils


logger = logging.getLogger(__name__)
AuthenticationClass = utils.get_class(settings.BACKCAP_API_AUTHENTICATION_CLASS)
AuthorizationClass = utils.get_class(settings.BACKCAP_API_AUTHORIZATION_CLASS)


class FeedbackResource(resources.ModelResource):

    class Meta:
        # simple guardian permission codes leaning
        # on default model permission codes for now.
        authorization = AuthorizationClass()
        authentication = AuthenticationClass()
        queryset = models.Feedback.objects.all()
        resource_name = 'feedback'
        always_return_data = True
        filtering = {'kind': resources.ALL,
                     'title': resources.ALL,
                     'text': resources.ALL
                     }

    def pick(self, collection, item):
        """ simple pick or nothing """
        for choice in collection:
            if choice[0] == item:
                return choice[1]
        return ""

    def dehydrate_kind(self, bundle):
        """ When retrieving a Feedback item, convert the `kind`
            into the human readable version.
        """
        return self.pick(bundle.obj.KIND_CHOICES, bundle.obj.kind)

    def dehydrate_status(self, bundle):
        """ When retrieving a Feedback item, convert the `status`
            into the human readable version.
        """
        return self.pick(bundle.obj.STATUS_CHOICES, bundle.obj.status)

    def obj_create(self, bundle, **kwargs):
        """ When new feedback instance is created, ensure that the creating user
            is assigned to `user` and the initial `follower`
        """
        return super(FeedbackResource, self).obj_create(bundle,
                                                        user=bundle.request.user,
                                                        follower=bundle.request.user)

#
# entry point for django-piehunter 
EnabledResources = (FeedbackResource, )
