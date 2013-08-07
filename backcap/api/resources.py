import logging

from django.contrib.auth.models import User

from tastypie import resources
from tastypie import fields
from tastypie.throttle import BaseThrottle

from .. import models
from .. import utils
from ..conf import settings


logger = logging.getLogger(__name__)
AuthenticationClass = utils.get_class(settings.BACKCAP_API_AUTHENTICATION_CLASS)
AuthorizationClass = utils.get_class(settings.BACKCAP_API_AUTHORIZATION_CLASS)
ValidationClass = utils.get_class(settings.BACKCAP_API_VALIDATION_CLASS)


class UserResource(resources.ModelResource):
    class Meta:
        queryset = User.objects.all()


class FeedbackResource(resources.ModelResource):
    user = fields.ForeignKey(to=UserResource, blank=True, null=True, attribute='user')
    kind = fields.CharField(blank=True, null=True, attribute='user')

    class Meta:
        authorization = AuthorizationClass()
        authentication = AuthenticationClass()
        # validation = ValidationClass()
        queryset = models.Feedback.objects.all()
        throttle = BaseThrottle(throttle_at=settings.BACKCAP_API_THROTTLE_RATE)
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
        user = bundle.request.user
        email = bundle.data.get("email", None)
        created = False

        if not user.is_authenticated() and email:
            user, created = User.objects.get_or_create(username=email, email=email)

        return super(FeedbackResource, self).obj_create(bundle, user=user)

#
# entry point for django-piehunter
EnabledResources = (FeedbackResource, )
