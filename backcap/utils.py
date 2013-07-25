import notification.models as notification


def subscribe_user(user, feedback):
    """
    Subscribe a user to any change of a given feedback
    """
    feedback.followers.add(user)


def unsubscribe_user(user, feedback):
    """
    Unsubscribe a user to any change of a given feedback
    """
    feedback.followers.remove(user)


def get_class(fqn):
    """
    Takes a fully qualified name and returns the resulting object

        KlassThing = get_class('some_app.some_module.SomeUsefulKlassThing')

    """
    try:
        parts = fqn.split('.')
        module = ".".join(parts[:-1])
        klass = __import__(module)
        for component in parts[1:]:
            klass = getattr(klass, component)
        return klass
    except ImportError as error:
        raise error()
