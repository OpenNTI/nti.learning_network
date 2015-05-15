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
	A container for holding the count of events.
	"""

	Count = Number( title="Count", required=True )

class ITimeStats( IStats ):
	"""
	A container for holding various time stats.
	"""
	AggregateTime = Number( title="The total amount of time spent.", required=True )
	StandardDeviationDuration = Float( title="Standard deviation duration", required=True )
	AverageDuration = Float( title="Average duration", required=True )

class IUniqueStatsMixin( IStats ):
	"""
	Establishes uniqueness counts.
	"""
	UniqueCount = Number( title="Unique self assessment count", required=True )

class ISelfAssessmentStats( IUniqueStatsMixin ):
	"""
	A container for holding self-assessment stats.
	"""

class IAssignmentStats( IUniqueStatsMixin ):
	"""
	A container for holding assignment stats.
	"""
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
	A source of learning network access stats.
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

	def get_assignment_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for assignment views, optionally
		with a course or timestamp filter.
		"""

	def get_self_assessment_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for self assessment views, optionally
		with a course or timestamp filter.
		"""

class IProductionStatsSource( interface.Interface ):
	"""
	A source of learning network production stats.
	"""

	def get_assignment_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for the assignments, optionally
		with a timestamp filter.
		"""

	def get_self_assessment_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for self-assessments, optionally
		with a course or timestamp filter.
		"""

	def get_comment_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for comments, optionally
		with a course or timestamp filter.
		"""

	def get_thought_stats( timestamp=None ):
		"""
		Return the learning network stats for thoughts, optionally
		with a timestamp filter.
		"""

	def get_note_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for notes, optionally
		with a course or timestamp filter.
		"""

	def get_highlight_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for highlights, optionally
		with a course or timestamp filter.
		"""

	def get_bookmark_stats( course=None, timestamp=None ):
		"""
		Return the learning network stats for bookmarks, optionally
		with a course or timestamp filter.
		"""
