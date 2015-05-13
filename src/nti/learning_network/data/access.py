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
from nti.analytics.boards import get_topic_views

from nti.learning_network.interfaces import IAccessStatsSource

@interface.implementer( IAccessStatsSource )
class _AccessStatsSource( object ):

	def __init__(self, user):
		self.user = user

	def get_platform_stats( self, timestamp=None ):
		"""
		Return the learning network stats for context, optionally
		with a timestamp filter.
		"""

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

