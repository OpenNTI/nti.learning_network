#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.schema.field import Number
from nti.schema.field import Float

class IStats( interface.Interface ):
	"""
	A container for holding various stats.
	"""

	StandardDeviation = Float( title="Standard deviation", required=True )
	Average = Float( title="Average", required=True )
	Count = Number( title="Count", required=True )

class ITimeStats( IStats ):
	"""
	A container for holding various time stats.
	"""

	AggregateTime = Number( title="The total amount of time spent.", required=True )

class IAggregateAssessmentStats( interface.Interface ):
	"""
	A container for holding assessment aggregate stats.
	"""

	SelfAssessmentCount = Number( title="Self assessment count", required=True )
	UniqueSelfAssessmentCount = Number( title="Unique self assessment count", required=True )

	AssignmentCount = Number( title="Assignment count", required=True )
	UniqueAssignmentCount = Number( title="Unique assignment count", required=True )
	AssignmentLateCount = Number( title="Unique self assessment count", required=True )
	TimedAssignmentCount = Number( title="Unique assignment count", required=True )
	TimedAssignmentLateCount = Number( title="Late assignment timed count", required=True )

class ILearningNetworkScoreProvider( interface.Interface ):
	"""
	For a given context, typically a user, able to answer
	various learning network related questions.
	"""

	def get_score( course=None, timestamp=None ):
		"""
		Return the learning network score for context, optionally
		with a course or timestamp filter.
		"""

class IAccessScoreProvider( ILearningNetworkScoreProvider ):
	"""
	Provides learning network scores for access.
	"""

class IAccessStatsSource( interface.Interface ):
	"""
	Provides learning network stats for access.
	"""
	def get_platform_stats( timestamp=None ):
		"""
		Return the learning network stats for the platform, optionally
		with a timestamp filter.
		"""

	def get_forum_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for forums, optionally
		with a course or timestamp filter.
		"""

	def get_video_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for videos, optionally
		with a course or timestamp filter.
		"""

	def get_reading_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for readings, optionally
		with a course or timestamp filter.
		"""

	def get_assignment_views( course=None, timestamp=None ):
		"""
		Return the learning network stats for assignment views, optionally
		with a course or timestamp filter.
		"""

	def get_self_assessment_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for self assessment views, optionally
		with a course or timestamp filter.
		"""
