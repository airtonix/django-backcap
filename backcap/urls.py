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

from django.conf.urls.defaults import patterns, url
from django.views.generic.base import RedirectView

from . import views
from .conf import settings


urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='list')),
    url(r'^new/$', views.feedback_new, name='feedback-new'),
    url(r'^list/$', views.FeedbackListView.as_view(), name='feedback-list'),
    url(r'^list/(?P<qtype>\w+)/$', views.FeedbackListView.as_view(), name='feedback-list'),
    url(r'^search/$', views.feedback_search, name='feedback-search'),
    url(r'^(?P<feedback_id>\d+)/$', views.FeedbackDetailView.as_view(), name='feedback-detail'),
    url(r'^(?P<feedback_id>\d+)/update/$', views.FeedbackUpdateView.as_view(), name='feedback-update'),
    url(r'^(?P<feedback_id>\d+)/close/$', views.feedback_close, name='feedback-close'),
    url(r'^(?P<feedback_id>\d+)/ping/$', views.feedback_ping_observers, name='feedback-ping-observers'),

    # Following
    url(r'^(?P<feedback_id>\d+)/follow/$', views.feedback_follow, name='feedback-follow'),
    url(r'^(?P<feedback_id>\d+)/unfollow/$', views.feedback_unfollow, name='feedback-unfollow'),

    url(r'^feedback-tab/$', views.feedback_tab, name='feedback-tab'),

    # Votes
    url(r'^(?P<feedback_id>\d+)/(?P<direction>up|down|clear)vote/$', views.feedback_vote, name='feedback-vote'),

)
