#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.analytics.sessions import get_user_sessions
#from nti.analytics.boards import get_topic_views

from nti.learning_network.interfaces import IAccessStatsSource

from ._utils import get_time_stats

@interface.implementer( IAccessStatsSource )
class _AccessStatsSource( object ):

	def __init__(self, user):
		self.user = user

	def _get_time_lengths( self, records, do_include=lambda: True ):
		result = None
		if records:
			result = [ 	x.time_length
						for x in records
						if do_include( x ) and x.time_length is not None ]
		return result

	def get_platform_stats( self, timestamp=None ):
		user_sessions = get_user_sessions( self.user, timestamp=timestamp )

		def is_complete( record ):
			# Filtering out sessions without end times or time_lengths
			return record.end_time and record.time_length

		time_lengths = self._get_time_lengths( user_sessions,
											do_include=is_complete )

		stats = get_time_stats( time_lengths )
		return stats

	def get_forum_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for forums, optionally
		with a course or timestamp filter.
		"""

	def get_video_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for videos, optionally
		with a course or timestamp filter.
		"""

	def get_reading_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for readings, optionally
		with a course or timestamp filter.
		"""

	def get_assessment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for assessment views, optionally
		with a course or timestamp filter.
		"""

	def get_self_assessment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for self assessment views, optionally
		with a course or timestamp filter.
		"""

