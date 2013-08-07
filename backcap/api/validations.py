from tastypie import validation

from ..forms import FeedbackNewForm


class FeedbackFormValidation(validation.FormValidation):
    def __init__(self, *args, **kwargs):
        super(FeedbackFormValidation, self).__init__(form_class=FeedbackNewForm)