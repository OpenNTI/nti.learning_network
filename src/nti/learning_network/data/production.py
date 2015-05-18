#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
from brownie.itools import count
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.assessment.interfaces import IQTimedAssignment

from nti.analytics.assessments import get_assignments_for_user
from nti.analytics.assessments import get_self_assessments_for_user

from nti.analytics.boards import get_forum_comments_for_user

from nti.analytics.blogs import get_blogs

from nti.analytics.resource_tags import get_notes
from nti.analytics.resource_tags import get_highlights
from nti.analytics.resource_tags import get_bookmarks

from nti.common.property import readproperty

from nti.dataserver.core.interfaces import ICanvas

from nti.learning_network.interfaces import IProductionStatsSource

from nti.learning_network.model import NoteStats
from nti.learning_network.model import CommentStats
from nti.learning_network.model import AssignmentStats
from nti.learning_network.model import SelfAssessmentStats

from ._utils import get_std_dev
from ._utils import get_count_stats

def _get_stats( records, do_include=lambda: True ):
	"""
	For records, return the stats, optionally filtering.
	"""
	records = [x for x in records if do_include( x )]
	stats = get_count_stats( records )
	return stats

def _has_whiteboard( obj ):
	body = obj.body
	if body:
		for body_part in body:
			if ICanvas.providedBy( body_part ):
				return True
	return False

def _get_post_stats( records, clazz, obj_field, length_field ):
	post_stats = None

	if records:
		count = reply_count = top_level_count = 0
		distinct_like_count = distinct_fave_count = 0
		total_likes = total_faves = total_length = 0
		recursive_child_count = contains_board_count = 0
		lengths = []

		for post in records:
			count += 1
			if post.IsReply:
				reply_count += 1
			else:
				top_level_count += 1

			if post.LikeCount:
				distinct_like_count += 1
				total_likes += post.LikeCount

			if post.FavoriteCount:
				distinct_fave_count += 1
				total_faves += post.FavoriteCount

			post_length = getattr( post, length_field, None )

			if post_length is not None:
				lengths.append( post_length )
				total_length += post_length

			obj = getattr( post, obj_field, None )

			if obj is not None:
				# Waking up object, expensive if we're
				# waking up every child?
				recursive_child_count += obj.referents

				if _has_whiteboard( obj ):
					contains_board_count += 1

		average_length = total_length / count
		std_dev_length = get_std_dev( lengths, total_length )

		post_stats = clazz( Count=count,
							ReplyCount=reply_count,
							TopLevelCount=top_level_count,
							DistinctPostsLiked=distinct_like_count,
							DistinctPostsFavorited=distinct_fave_count,
							TotalLikes=total_likes,
							TotalFavorites=total_faves,
							RecursiveChildrenCount=recursive_child_count,
							StandardDeviationLength=std_dev_length,
							AverageLength=average_length,
							ContainsWhiteboardCount=contains_board_count )

	return post_stats

@interface.implementer( IProductionStatsSource )
class _AnalyticsProductionStatsSource( object ):
	"""
	A production stats source that pulls data from analytics.
	"""

	def __init__(self, user, course=None, timestamp=None):
		self.user = user
		self.course = course
		self.timestamp = timestamp

	@readproperty
	def assignment_stats( self ):
		"""
		Return the learning network stats for assignments, optionally
		with a course or timestamp filter.
		"""
		assignments = get_assignments_for_user( self.user, course=self.course,
												timestamp=self.timestamp )
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

	@readproperty
	def self_assessment_stats( self ):
		"""
		Return the learning network stats for self-assessments, optionally
		with a course or timestamp filter.
		"""
		assessments = get_self_assessments_for_user( self.user, course=self.course,
													timestamp=self.timestamp )
		stats = None

		if assessments:
			count = sum( (1 for x in assessments) )
			assessment_ids = {x.AssessmentId for x in assessments}
			unique_count = len( assessment_ids )

			stats = SelfAssessmentStats( Count=count, UniqueCount=unique_count )
		return stats

	@readproperty
	def comment_stats( self ):
		"""
		Return the learning network stats for comments, optionally
		with a course or timestamp filter.
		"""
		comment_records = get_forum_comments_for_user( self.user, course=self.course,
													timestamp=self.timestamp )
		stats = _get_post_stats( comment_records, CommentStats,
								'Comment', 'CommentLength' )
		return stats

	@readproperty
	def thought_stats( self ):
		"""
		Return the learning network stats for thoughts, optionally
		with a timestamp filter.
		"""
		blog_records = get_blogs( self.user, timestamp=self.timestamp )
		# FIXME posts also?
		# Thought comments?
		return _get_stats( blog_records )

	@readproperty
	def note_stats( self ):
		"""
		Return the learning network stats for notes, optionally
		with a course or timestamp filter.
		"""
		note_records = get_notes( self.user, course=self.course,
									timestamp=self.timestamp )
		stats = _get_post_stats( note_records, NoteStats, 'Note', 'NoteLength' )
		return stats

	@readproperty
	def highlight_stats( self ):
		"""
		Return the learning network stats for highlights, optionally
		with a course or timestamp filter.
		"""
		highlight_records = get_highlights( self.user, course=self.course,
										timestamp=self.timestamp )
		return _get_stats( highlight_records )

	@readproperty
	def bookmark_stats( self ):
		"""
		Return the learning network stats for bookmarks, optionally
		with a course or timestamp filter.
		"""
		blog_records = get_bookmarks( self.user, course=self.course,
										timestamp=self.timestamp )
		return _get_stats( blog_records )
