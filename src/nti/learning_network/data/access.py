#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.analytics.boards import get_topic_views
from nti.analytics.sessions import get_user_sessions
from nti.analytics.resource_views import get_user_video_events
from nti.analytics.resource_views import get_user_resource_views
from nti.analytics.assessments import get_assignment_views
from nti.analytics.assessments import get_self_assessment_views

from nti.learning_network.interfaces import IAccessStatsSource

from ._utils import get_time_stats

def _get_time_lengths( records, do_include ):
	result = None
	if records:
		result = [ 	x.time_length
					for x in records
					if do_include( x ) and x.time_length ]
	return result

def _get_stats( records, do_include=lambda: True ):
	"""
	For time length records, return the stats, optionally filtering.
	"""
	time_lengths = _get_time_lengths( records, do_include )
	stats = get_time_stats( time_lengths )
	return stats

@interface.implementer( IAccessStatsSource )
class _AnalyticsAccessStatsSource( object ):
	"""
	An access stats source that pulls data from analytics.
	"""

	def __init__(self, user):
		self.user = user

	def get_platform_stats( self, timestamp=None ):
		user_sessions = get_user_sessions( self.user, timestamp=timestamp )

		def is_complete( record ):
			# Filtering out sessions without end times or time_lengths
			return record.end_time and record.time_length

		return _get_stats( user_sessions, do_include=is_complete )

	def get_forum_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for forums, optionally
		with a course or timestamp filter.
		"""
		topic_views = get_topic_views( self.user, course=course,
									timestamp=timestamp )
		return _get_stats( topic_views )

	def get_video_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for videos, optionally
		with a course or timestamp filter.
		"""
		video_views = get_user_video_events( self.user, course=course,
											timestamp=timestamp )

		return _get_stats( video_views )

	def get_reading_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for readings, optionally
		with a course or timestamp filter.
		"""
		resource_views = get_user_resource_views( self.user, course=course,
												timestamp=timestamp )

		return _get_stats( resource_views )

	def get_assignment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for assignment views, optionally
		with a course or timestamp filter.
		"""
		assignment_views = get_assignment_views( self.user, course=course,
												timestamp=timestamp )

		return _get_stats( assignment_views )

	def get_self_assessment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for self assessment views, optionally
		with a course or timestamp filter.
		"""
		self_assess_views = get_self_assessment_views( self.user, course=course,
													timestamp=timestamp )

		return _get_stats( self_assess_views )

