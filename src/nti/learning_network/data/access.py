#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from zope.cachedescriptors.property import Lazy

from nti.analytics.assessments import get_assignment_views
from nti.analytics.assessments import get_self_assessment_views

from nti.analytics.boards import get_topic_views

from nti.analytics.resource_views import get_user_video_views
from nti.analytics.resource_views import get_user_resource_views

from nti.analytics.sessions import get_user_sessions

from nti.analytics.stats.utils import get_time_stats

from nti.learning_network.interfaces import IAccessStatsSource


def _get_time_lengths(records, do_include):
	result = None
	if records:
		result = [ 	x.Duration
					for x in records
					if do_include(x) and x.Duration is not None ]
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
