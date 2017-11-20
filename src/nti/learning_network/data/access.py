#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.cachedescriptors.property import Lazy

from nti.analytics.assessments import get_assignment_views
from nti.analytics.assessments import get_self_assessment_views

from nti.analytics.boards import get_topic_views

from nti.analytics.resource_views import get_user_video_views
from nti.analytics.resource_views import get_user_resource_views

from nti.analytics.sessions import get_user_sessions

from nti.analytics.stats.utils import get_time_stats
from nti.analytics.stats.utils import get_count_stats

from nti.analytics.user_file_views import get_user_file_views

from nti.learning_network.interfaces import IAccessStatsSource
from nti.learning_network.interfaces import IResourceAccessStatsSource

from nti.ntiids.ntiids import find_object_with_ntiid

from nti.ntiids.oids import to_external_ntiid_oid

logger = __import__('logging').getLogger(__name__)


def _get_time_lengths(records, do_include):
    result = None
    if records:
        result = [x.Duration
                  for x in records
                  if do_include(x) and x.Duration is not None]
    return result


def _get_stats(records, do_include=lambda _: True):
    """
    For time length records, return the stats, optionally filtering.
    """
    time_lengths = _get_time_lengths(records, do_include)
    stats = get_time_stats(time_lengths)
    return stats


@interface.implementer(IAccessStatsSource)
class _AnalyticsAccessStatsSource(object):
    """
    An access stats source that pulls data from analytics.
    """
    __external_class_name__ = "AccessStatsSource"
    mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.accessstatssource'

    display_name = 'Access'

    def __init__(self, user, course=None, timestamp=None, max_timestamp=None):
        self.user = user
        self.course = course
        self.timestamp = timestamp
        self.max_timestamp = max_timestamp

    @Lazy
    def PlatformStats(self):
        user_sessions = get_user_sessions(self.user, timestamp=self.timestamp,
                                          max_timestamp=self.max_timestamp)

        def is_complete(record):
            # Filtering out sessions without end times or time_lengths
            return record.SessionEndTime

        return _get_stats(user_sessions, do_include=is_complete)

    @Lazy
    def ForumStats(self):
        """
        Return the learning network stats for forums, optionally
        with a course or timestamp filter.
        """
        topic_views = get_topic_views(self.user, course=self.course,
                                      timestamp=self.timestamp,
                                      max_timestamp=self.max_timestamp)
        return _get_stats(topic_views)

    @Lazy
    def VideoStats(self):
        """
        Return the learning network stats for videos, optionally
        with a course or timestamp filter.
        """
        video_views = get_user_video_views(self.user, course=self.course,
                                           timestamp=self.timestamp,
                                           max_timestamp=self.max_timestamp)

        return _get_stats(video_views)

    @Lazy
    def ReadingStats(self):
        """
        Return the learning network stats for readings, optionally
        with a course or timestamp filter.
        """
        resource_views = get_user_resource_views(self.user, course=self.course,
                                                 timestamp=self.timestamp,
                                                 max_timestamp=self.max_timestamp)

        return _get_stats(resource_views)

    @Lazy
    def AssignmentStats(self):
        """
        Return the learning network stats for assignment views, optionally
        with a course or timestamp filter.
        """
        assignment_views = get_assignment_views(self.user, course=self.course,
                                                timestamp=self.timestamp,
                                                max_timestamp=self.max_timestamp)

        return _get_stats(assignment_views)

    @Lazy
    def SelfAssessmentStats(self):
        """
        Return the learning network stats for self assessment views, optionally
        with a course or timestamp filter.
        """
        self_assess_views = get_self_assessment_views(self.user, course=self.course,
                                                      timestamp=self.timestamp,
                                                      max_timestamp=self.max_timestamp)

        return _get_stats(self_assess_views)


@interface.implementer(IResourceAccessStatsSource)
class _AnalyticsResourceAccessStatsSource(object):

    __external_class_name__ = "ResourceAccessStatsSource"
    mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.resourceaccessstatssource'
    display_name = 'ResourceAccess'

    def __init__(self, user, course=None, timestamp=None, max_timestamp=None):
        self.user = user
        self.course = course
        self.timestamp = timestamp
        self.max_timestamp = max_timestamp

    def _get_resource_title(self, resource_record):
        result = resource_record.Title
        if result is None:
            resource = find_object_with_ntiid(resource_record.ResourceId)
            result = getattr(resource, 'title', '') \
                  or getattr(resource, 'label', '')
        return result

    def get_all_resource_names(self):
        result = set()
        resource_views = get_user_resource_views(course=self.course,
                                                 timestamp=self.timestamp,
                                                 max_timestamp=self.max_timestamp)
        for resource_view in resource_views:
            title = self._get_resource_title(resource_view)
            result.add('Reading_%s' % title)

        video_views = get_user_video_views(course=self.course,
                                           timestamp=self.timestamp,
                                           max_timestamp=self.max_timestamp)
        for video_view in video_views:
            title = self._get_resource_title(video_view)
            result.add('Video_%s' % title)

        topic_views = get_topic_views(course=self.course,
                                      timestamp=self.timestamp,
                                      max_timestamp=self.max_timestamp)
        for topic_view in topic_views:
            if topic_view.Topic is None:
                continue
            result.add('Topic_%s' % topic_view.Topic.title)

        file_views = get_user_file_views(course=self.course,
                                         timestamp=self.timestamp,
                                         max_timestamp=self.max_timestamp)
        for file_view in file_views:
            if file_view.FileObject is None:
                continue
            result.add('FileUploadView_%s' % file_view.FileObject.filename)
        return result

    def get_resource_stats(self):
        result = {}
        resource_views = get_user_resource_views(self.user,
                                                 course=self.course,
                                                 timestamp=self.timestamp,
                                                 max_timestamp=self.max_timestamp)
        record_map = {}
        for resource_view in resource_views:
            ntiid = resource_view.ResourceId
            if ntiid not in record_map:
                title = self._get_resource_title(resource_view)
                # Tuple (title, records)
                record_map[ntiid] = ('Reading_%s' % title, [])
            record_map[ntiid][1].append(resource_view)

        video_views = get_user_video_views(self.user,
                                           course=self.course,
                                           timestamp=self.timestamp,
                                           max_timestamp=self.max_timestamp)
        for video_view in video_views:
            ntiid = video_view.ResourceId
            if ntiid not in record_map:
                title = self._get_resource_title(video_view)
                # Tuple (title, records)
                record_map[ntiid] = ('Video_%s' % title, [])
            record_map[ntiid][1].append(video_view)

        topic_views = get_topic_views(self.user,
                                      course=self.course,
                                      timestamp=self.timestamp,
                                      max_timestamp=self.max_timestamp)
        for topic_view in topic_views:
            if topic_view.Topic is None:
                continue
            ntiid = to_external_ntiid_oid(topic_view.Topic)
            if ntiid not in record_map:
                # Tuple (title, records)
                record_map[ntiid] = ('Topic_%s' % topic_view.Topic.title, [])
            record_map[ntiid][1].append(topic_view)

        # XXX: no course here...
        file_views = get_user_file_views(self.user,
                                         timestamp=self.timestamp,
                                         max_timestamp=self.max_timestamp)
        for file_view in file_views:
            if file_view.FileObject is None:
                continue
            ntiid = file_view.file_ds_id
            if ntiid not in record_map:
                # Tuple (title, records)
                record_map[ntiid] = ('FileUploadView_%s' %
                                     file_view.FileObject.filename, [])
            record_map[ntiid][1].append(file_view)

        for title, records in record_map.values():
            result[title] = get_count_stats(records)
        return result
