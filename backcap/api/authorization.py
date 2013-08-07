import logging

from tastypie.authorization import DjangoAuthorization, Authorization
from tastypie.exceptions import Unauthorized


logger = logging.getLogger(__name__)


class BaseAuthorization(DjangoAuthorization):

    """
        Authorization class for User objects.
    """

    def generic_base_check(self, object_list, bundle):
        """
            Returns False if either:
                a) if the `object_list.model` doesn't have a `_meta` attribute
                b) the `bundle.request` object doesn have a `user` attribute
        """
        klass = self.base_checks(bundle.request, object_list.model)
        if klass is False:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

    def generic_item_check(self, object_list, bundle):
        if not self.generic_base_check(object_list, bundle):
            raise Unauthorized("You are not allowed to access that resource.")

        return True

    def generic_list_check(self, object_list, bundle):
        if not self.generic_base_check(object_list, bundle):
            raise Unauthorized("You are not allowed to access that resource.")

        return object_list

    # List Checks
    def create_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle)

    def read_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle)

    def update_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle)

    def delete_list(self, object_list, bundle):
        return self.generic_list_check(object_list, bundle)

    # Item Checks
    def create_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle)

    def read_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return self.generic_item_check(object_list, bundle)


class GuestWritableAuthorization(BaseAuthorization):
    """
        Use case scenario: contact form
    """
    empty_object_list = []

    def create_detail(self, object_list, bundle):
        # allow creation
        return True


class UserObjectOnlyAuthorization(BaseAuthorization):

    def generic_item_check(self, object_list, bundle):
        super(UserObjectOnlyAuthorization, self).generic_item_check(object_list, bundle)
        if not bundle.request.user == bundle.obj:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

    def generic_list_check(self, object_list, bundle):
        super(UserObjectOnlyAuthorization, self).generic_list_check(object_list, bundle)
        return object_list.filter(pk=bundle.request.user.id)


class UserRelatedObjectsOnlyAuthorization(BaseAuthorization):

    def __init__(self, *args, **kwargs):
        self.user_field = kwargs.pop('user_field', 'user')
        super(UserRelatedObjectsOnlyAuthorization, self).__init__(*args, **kwargs)

    def generic_item_check(self, object_list, bundle):
        super(UserRelatedObjectsOnlyAuthorization, self).generic_item_check(object_list, bundle)
        user = bundle.request.user

        if not user.is_authenticated():
            raise Unauthorized("You are not allowed to access that resource.")
        if not getattr(bundle.obj, self.user_field) == user:
            raise Unauthorized("You are not allowed to access that resource.")
        return True

    def generic_list_check(self, object_list, bundle):
        super(UserRelatedObjectsOnlyAuthorization, self).generic_list_check(object_list, bundle)
        user = bundle.request.user
        user.is_authenticated()
        return object_list.filter(**{self.user_field: user.id})


class GuestWritableUserObjectsReadOnlyAuthorization(GuestWritableAuthorization, UserRelatedObjectsOnlyAuthorization):
    """ Long class name is long."""
    pass
