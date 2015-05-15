#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.assessment.interfaces import IQTimedAssignment

from nti.analytics.assessments import get_assignments_for_user
from nti.analytics.assessments import get_self_assessments_for_user

from nti.analytics.blogs import get_blogs

from nti.analytics.resource_tags import get_notes
from nti.analytics.resource_tags import get_highlights
from nti.analytics.resource_tags import get_bookmarks

from nti.learning_network.interfaces import IProductionStatsSource

from nti.learning_network.model import AssignmentStats
from nti.learning_network.model import SelfAssessmentStats

from ._utils import get_count_stats

def _get_stats( records, do_include=lambda: True ):
	"""
	For records, return the stats, optionally filtering.
	"""
	records = [x for x in records if do_include( x )]
	stats = get_count_stats( records )
	return stats

@interface.implementer( IProductionStatsSource )
class _AnalyticsProductionStatsSource( object ):
	"""
	A production stats source that pulls data from analytics.
	"""

	def __init__(self, user):
		self.user = user

	def get_assignment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for the assignments, optionally
		with a timestamp filter.
		"""
		assignments = get_assignments_for_user( self.user, course=course,
											timestamp=timestamp )
		stats = None

		if assignments:
			count = timed_count = late_count = timed_late_count = 0
			id_set = set()
			for assignment_record in assignments:
				count += 1
				id_set.add( assignment_record.AssignmentId )
				if assignment_record.IsLate:
					late_count += 1

				assignment = assignment_record.Submission.Assignment

				if IQTimedAssignment.providedBy( assignment ):
					timed_count += 1
					if assignment_record.IsLate:
						timed_late_count += 1

			unique_count = len( id_set )

			stats = AssignmentStats( Count=count,
									UniqueCount=unique_count,
									AssignmentLateCount=late_count,
									TimedAssignmentCount=timed_count,
									TimedAssignmentLateCount=timed_late_count )
		return stats

	def get_self_assessment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for self-assessments, optionally
		with a course or timestamp filter.
		"""
		assessments = get_self_assessments_for_user( self.user, course=course,
													timestamp=timestamp )
		stats = None

		if assessments:
			count = sum( (1 for x in assessments) )
			assessment_ids = {x.AssignmentId for x in assessments}
			unique_count = len( assessment_ids )

			stats = SelfAssessmentStats( Count=count, UniqueCount=unique_count )
		return stats

	def get_comment_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for comments, optionally
		with a course or timestamp filter.
		"""

	def get_thought_stats( self, timestamp=None ):
		"""
		Return the learning network stats for thoughts, optionally
		with a timestamp filter.
		"""
		blog_records = get_blogs( self.user, timestamp=timestamp )
		return _get_stats( blog_records )

	def get_note_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for notes, optionally
		with a course or timestamp filter.
		"""
		note_records = get_notes( self.user, course=course,
								timestamp=timestamp )
		return _get_stats( note_records )

	def get_highlight_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for highlights, optionally
		with a course or timestamp filter.
		"""
		highlight_records = get_highlights( self.user, course=course,
										timestamp=timestamp )
		return _get_stats( highlight_records )

	def get_bookmark_stats( self, course=None, timestamp=None ):
		"""
		Return the learning network stats for bookmarks, optionally
		with a course or timestamp filter.
		"""
		blog_records = get_bookmarks( self.user, course=course,
									timestamp=timestamp )
		return _get_stats( blog_records )
