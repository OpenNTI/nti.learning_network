#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from itertools import chain

from zope import interface

from nti.analytics.boards import get_forum_comments

from nti.analytics.resource_tags import get_notes

from nti.learning_network.interfaces import IConnectionsSource

from nti.learning_network.model import Connection

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IConnectionsSource)
class _AnalyticsConnections(object):
    """
    A connections source that pulls data from analytics.
    """

    def __init__(self, context):
        self.course = context

    def _get_connection_objs(self, replies):
        results = []
        for reply in replies or ():
            if reply.IsReply and reply.RepliedToUser:
                target = reply.RepliedToUser.username
                source = reply.user.username
                if source != target:
                    timestamp = reply.timestamp
                    new_connection = Connection(Source=source,
                                                Target=target,
                                                Timestamp=timestamp)
                    results.append(new_connection)
        return results

    def _get_notes(self, timestamp=None):
        notes = get_notes(course=self.course,
                          timestamp=timestamp, replies_only=True)
        results = self._get_connection_objs(notes)
        return results

    def _get_forum_comments(self, timestamp=None):
        comments = get_forum_comments(
            course=self.course, timestamp=timestamp, replies_only=True)
        results = self._get_connection_objs(comments)
        return results

    def get_connections(self, timestamp=None):
        notes = self._get_notes(timestamp)
        comments = self._get_forum_comments(timestamp)
        return chain(notes, comments)
