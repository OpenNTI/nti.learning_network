#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.analytics.assessments import get_assignments_for_user
from nti.analytics.assessments import get_self_assessments_for_user

from nti.analytics.boards import get_forum_comments_for_user

from nti.analytics.blogs import get_blogs
from nti.analytics.blogs import get_blog_comments

from nti.analytics.stats.model import NoteStats
from nti.analytics.stats.model import CommentStats
from nti.analytics.stats.model import AssignmentStats
from nti.analytics.stats.model import ThoughtCommentStats
from nti.analytics.stats.model import SelfAssessmentStats

from nti.analytics.mime_types import get_all_mime_types

from nti.analytics.resource_tags import get_notes
from nti.analytics.resource_tags import get_highlights
from nti.analytics.resource_tags import get_bookmarks

from nti.analytics.stats.utils import get_count_stats
from nti.analytics.stats.utils import build_post_stats

from nti.assessment.interfaces import IQTimedAssignment

from nti.common.property import readproperty

from nti.learning_network.interfaces import IProductionStatsSource

def _get_stats(records, do_include=lambda _: True):
	"""
	For records, return the stats, optionally filtering.
	"""
	if records:
		records = [x for x in records if do_include(x)]
	stats = get_count_stats(records)
	return stats

@interface.implementer(IProductionStatsSource)
class _AnalyticsProductionStatsSource(object):
	"""
	A production stats source that pulls data from analytics.
	"""
	__external_class_name__ = "ProductionStatsSource"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.productionstatssource'
	display_name = 'Production'

	def __init__(self, user, course=None, timestamp=None, max_timestamp=None):
		self.user = user
		self.course = course
		self.timestamp = timestamp
		self.max_timestamp = max_timestamp

	@property
	def AllMimeTypes(self):
		results = get_all_mime_types()
		return sorted( results ) if results else ()

	@readproperty
	def AssignmentStats(self):
		"""
		Return the learning network stats for assignments, optionally
		with a course or timestamp filter.
		"""
		assignments = get_assignments_for_user(self.user, course=self.course,
											   timestamp=self.timestamp,
											   max_timestamp=self.max_timestamp)
		count = unique_count = 0
		late_count = timed_count = timed_late_count = 0

		if assignments:
			id_set = set()
			for assignment_record in assignments:
				count += 1
				id_set.add(assignment_record.AssignmentId)
				if assignment_record.IsLate:
					late_count += 1

				assignment = getattr( assignment_record.Submission, 'Assignment', None )

				if assignment and IQTimedAssignment.providedBy(assignment):
					timed_count += 1
					if assignment_record.IsLate:
						timed_late_count += 1

			unique_count = len(id_set)

		stats = AssignmentStats(Count=count,
								UniqueCount=unique_count,
								AssignmentLateCount=late_count,
								TimedAssignmentCount=timed_count,
								TimedAssignmentLateCount=timed_late_count)
		return stats

	@readproperty
	def SelfAssessmentStats(self):
		"""
		Return the learning network stats for self-assessments, optionally
		with a course or timestamp filter.
		"""
		assessments = get_self_assessments_for_user(self.user, course=self.course,
													timestamp=self.timestamp,
											   		max_timestamp=self.max_timestamp)
		count = unique_count = 0

		if assessments:
			count = sum((1 for x in assessments))
			assessment_ids = {x.AssessmentId for x in assessments}
			unique_count = len(assessment_ids)

		stats = SelfAssessmentStats(Count=count, UniqueCount=unique_count)
		return stats

	@readproperty
	def CommentStats(self):
		"""
		Return the learning network stats for comments, optionally
		with a course or timestamp filter.
		"""
		comment_records = get_forum_comments_for_user(self.user, course=self.course,
													  timestamp=self.timestamp,
											   		  max_timestamp=self.max_timestamp)
		stats = build_post_stats(comment_records, CommentStats,
								'Comment', 'CommentLength',
								self.AllMimeTypes)
		return stats

	@readproperty
	def ThoughtStats(self):
		"""
		Return the learning network stats for thoughts, optionally
		with a timestamp filter.
		"""
		# TODO: Do we need to expand these stats beyond counts?
		blog_records = get_blogs(self.user, timestamp=self.timestamp,
								 max_timestamp=self.max_timestamp)
		return _get_stats(blog_records)

	@readproperty
	def ThoughtCommentStats(self):
		"""
		Return the learning network stats for thought comments, optionally
		with a timestamp filter.
		"""
		comment_records = get_blog_comments(self.user, timestamp=self.timestamp,
											max_timestamp=self.max_timestamp)
		stats = build_post_stats(comment_records, ThoughtCommentStats,
								'Comment', 'CommentLength',
								self.AllMimeTypes)
		return stats

	@readproperty
	def NoteStats(self):
		"""
		Return the learning network stats for notes, optionally
		with a course or timestamp filter.
		"""
		note_records = get_notes(self.user, course=self.course,
								 timestamp=self.timestamp,
								 max_timestamp=self.max_timestamp)
		stats = build_post_stats(note_records, NoteStats,
								'Note', 'NoteLength',
								self.AllMimeTypes)
		return stats

	@readproperty
	def HighlightStats(self):
		"""
		Return the learning network stats for highlights, optionally
		with a course or timestamp filter.
		"""
		highlight_records = get_highlights(self.user, course=self.course,
										   timestamp=self.timestamp,
										   max_timestamp=self.max_timestamp)
		return _get_stats(highlight_records)

	@readproperty
	def BookmarkStats(self):
		"""
		Return the learning network stats for bookmarks, optionally
		with a course or timestamp filter.
		"""
		blog_records = get_bookmarks(self.user, course=self.course,
									 timestamp=self.timestamp,
									 max_timestamp=self.max_timestamp)
		return _get_stats(blog_records)
