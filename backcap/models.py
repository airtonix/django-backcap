# -*- coding: utf-8 -*-

# Backcap, a support module for community-driven django websites
# Copyright (C) 2010, Guillaume Libersat <guillaume@spreadband.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.dispatch import receiver
from django.db.models import ForeignKey, CharField, TextField, DateTimeField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.comments.signals import comment_was_posted

from voting.models import Vote
import notification.models as notification

from .utils import subscribe_user
from .signals import feedback_updated
from .conf import settings


class Feedback(models.Model):
    class Meta:
        ordering = ('-modified_on', 'kind')

    KIND_CHOICES = (('Q', _('Question')),
                    ('P', _('Problem')),
                    ('I', _('Idea')),
                    )

    STATUS_CHOICES = (('N', _('New (unreviewed)')),
                      ('V', _('Valid')),
                      ('M', _('Need more information')),
                      ('W', _('Won\'t Fix')),
                      ('I', _('Invalid')),
                      ('A', _('Assigned')),
                      ('D', _('Duplicate')),
                      ('R', _('Re-opened')),
                      ('C', _('Closed')),
                      )

    # Timestamps
    created_on = DateTimeField(auto_now_add=True)
    modified_on = DateTimeField(auto_now=True)

    # Who and what
    user = ForeignKey(User, related_name='feedbacks')
    referer = TextField(verbose_name=_('Referer'),
                        blank=True,
                        null=True)

    # Contents
    kind = CharField(verbose_name=_('Kind'),
                     max_length=1, choices=KIND_CHOICES)
    title = CharField(verbose_name=_('Title'),
                      max_length=255)
    text = TextField(verbose_name=_('Text'),
                     help_text=_("Description of the feedback"),
                     blank=True)

    # State
    status = CharField(verbose_name=_('Status'),
                       max_length=1,
                       choices=STATUS_CHOICES, default='N')

    assigned_to = ForeignKey(User,
                             verbose_name=_('Assigned to'),
                             limit_choices_to={'is_staff': True},
                             related_name='assigned_feedbacks',
                             null=True,
                             blank=True)

    duplicate_of = ForeignKey('self',
                              verbose_name=_('Duplicate of'),
                              related_name='duplicates',
                              null=True,
                              blank=True)

    votes = generic.GenericRelation(Vote,
                                    object_id_field="object_id",
                                    content_type_field="content_type")

    followers = models.ManyToManyField(User, related_name='followed_feedbacks')

    def __unicode__(self):
        return '%s - %s' % (self.kind, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('feedback-detail', (), {'feedback_id': self.id})


@receiver(feedback_updated)
def on_feedback_updated(sender, *args, **kwargs):
    notification.send(sender.followers.all(), 'feedback_updated', {'feedback': sender})


@receiver(comment_was_posted)
def on_comment_posted(sender, comment, request, *args, **kwargs):
    # Send the 'feedback_updated' signal
    feedback_ctype = ContentType.objects.get_for_model(Feedback)
    if comment.content_type == feedback_ctype:
        feedback_updated.send(sender=comment.content_object)

    # Subscribe the commenting user to this feedback
    if not request.user.is_anonymous():
        subscribe_user(request.user, comment.content_object)
