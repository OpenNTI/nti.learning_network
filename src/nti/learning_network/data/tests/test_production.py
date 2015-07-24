#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time
import fudge
import weakref

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import assert_that

from datetime import datetime

from zope import component

from zope.interface import directlyProvides

from nti.analytics.read_models import AnalyticsBlog
from nti.analytics.read_models import AnalyticsBlogComment
from nti.analytics.read_models import AnalyticsAssignment
from nti.analytics.read_models import AnalyticsAssessment

from nti.app.assessment.history import UsersCourseAssignmentHistory

from nti.assessment.assignment import QAssignmentSubmissionPendingAssessment

from nti.assessment.assessed import QAssessedQuestionSet
from nti.assessment.assessed import QAssessedQuestion
from nti.assessment.assessed import QAssessedPart
from nti.assessment.assignment import QAssignment
from nti.assessment.assignment import QTimedAssignment
from nti.assessment.submission import AssignmentSubmission
from nti.assessment.submission import QuestionSetSubmission
from nti.assessment.submission import QuestionSubmission

from nti.contenttypes.courses.courses import CourseInstance

from nti.dataserver.users import User
from nti.dataserver.interfaces import IUser
from nti.dataserver.users.users import Principal

from nti.dataserver.contenttypes.forums.forum import PersonalBlog
from nti.dataserver.contenttypes.forums.topic import PersonalBlogEntry
from nti.dataserver.contenttypes.forums.post import PersonalBlogEntryPost
from nti.dataserver.contenttypes.forums.post import PersonalBlogComment

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.learning_network.interfaces import IProductionStatsSource

from ..production import _AnalyticsProductionStatsSource

from nti.learning_network.tests import LearningNetworkTestCase

course = CourseInstance()
_question_id = '1968'
_question_set_id = '2'
_assignment_id = 'b'
_response = 'bleh'

def _get_assessed_question_set():
	assessed_parts = []
	assessed = []
	assessed_parts.append( QAssessedPart(submittedResponse=_response, assessedValue=1.0))
	assessed.append( QAssessedQuestion(questionId=_question_id, parts=assessed_parts) )

	return QAssessedQuestionSet(questionSetId=_question_set_id, questions=assessed)

def _get_history_item( assignment_type=QAssignment ):
	question_set = _get_assessed_question_set()
	history = UsersCourseAssignmentHistory()
	qs_submission = QuestionSetSubmission(
						questionSetId=_question_set_id,
						questions=(QuestionSubmission(questionId=_question_id, parts=(_response,)),))
	submission = AssignmentSubmission(assignmentId=_assignment_id, parts=(qs_submission,))
	pending = QAssignmentSubmissionPendingAssessment( assignmentId=_assignment_id,
													   parts=(question_set,) )
	result = history.recordSubmission( submission, pending )

	# Need a weak ref for owner.
	result_creator = Principal( username=str( 'mrshowwithbobanddavid' ) )
	directlyProvides( result_creator, IUser )
	history.owner = weakref.ref( result_creator )

	result.createdTime = time.time()
	result.Assignment = assignment_type( parts=() )
	return result, result_creator

def _get_assignment( assignment_id, user, submission, is_late=False ):
	result = AnalyticsAssignment( Submission=submission,
									user=user,
									timestamp=datetime.utcnow(),
									RootContext=course,
									Duration=30,
									AssignmentId=assignment_id,
									GradeNum=None,
									Grade=None,
									Grader=None,
									IsLate=is_late,
									Details=None )
	return result

def _get_assessment( assignment_id, user, submission ):
	result = AnalyticsAssessment( Submission=submission,
									user=user,
									timestamp=datetime.utcnow(),
									RootContext=course,
									Duration=30,
									AssessmentId=assignment_id )
	return result

def _get_blog( blog, user ):
	result = AnalyticsBlog( Blog=blog,
							user=user,
							timestamp=datetime.utcnow(),
							BlogLength=30 )
	return result

def _get_blog_comment( comment, user, like_count=0, fave_count=0, is_reply=False ):
	result = AnalyticsBlogComment( Comment=comment,
									user=user,
									timestamp=datetime.utcnow(),
									CommentLength=30,
									LikeCount=like_count,
									FavoriteCount=fave_count,
									IsReply=is_reply )
	return result

class TestProduction( LearningNetworkTestCase ):

	def setUp(self):
		self.user = None
		self.stat_source = _AnalyticsProductionStatsSource( self.user )

	@WithMockDSTrans
	def _get_user(self):
		return User.create_user( username='new_user1' )

	@fudge.patch( 'nti.learning_network.data.production.get_assignments_for_user' )
	def test_assignment_stats( self, mock_get_assignments ):
		user = self._get_user()

		# Empty
		mock_get_assignments.is_callable().returns( None )
		stats = self.stat_source.AssignmentStats
		assert_that( stats.Count, is_( 0 ))
		assert_that( stats.UniqueCount, is_( 0 ) )

		mock_get_assignments.is_callable().returns( () )
		stats = self.stat_source.AssignmentStats
		assert_that( stats.Count, is_( 0 ))
		assert_that( stats.UniqueCount, is_( 0 ) )

		# Single
		assignment_id = 'assignment1'
		submission, _ = _get_history_item()
		assignment = _get_assignment( assignment_id, user, submission )
		assignments = ( assignment, )
		mock_get_assignments.is_callable().returns( assignments )

		stats = self.stat_source.AssignmentStats
		assert_that( stats.Count, is_( 1 ))
		assert_that( stats.UniqueCount, is_( 1 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Second
		assignment_id2 = 'assignment2'
		assignment2 = _get_assignment( assignment_id2, user, submission )
		assignments = ( assignment, assignment2 )
		mock_get_assignments.is_callable().returns( assignments )

		stats = self.stat_source.AssignmentStats
		assert_that( stats.Count, is_( 2 ))
		assert_that( stats.UniqueCount, is_( 2 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Dupe, late
		assignment3 = _get_assignment( assignment_id, user, submission, is_late=True )
		assignments = ( assignment, assignment2, assignment3 )
		mock_get_assignments.is_callable().returns( assignments )

		stats = self.stat_source.AssignmentStats
		assert_that( stats.Count, is_( 3 ))
		assert_that( stats.UniqueCount, is_( 2 ))
		assert_that( stats.AssignmentLateCount, is_( 1 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Timed, late
		assignment_id3 = 'assignment3'
		submission, _ = _get_history_item( QTimedAssignment )
		assignment4 = _get_assignment( assignment_id3, user, submission, is_late=True )
		assignments = ( assignment, assignment2, assignment3, assignment4 )
		mock_get_assignments.is_callable().returns( assignments )

		stats = self.stat_source.AssignmentStats
		assert_that( stats.Count, is_( 4 ))
		assert_that( stats.UniqueCount, is_( 3 ))
		assert_that( stats.AssignmentLateCount, is_( 2 ))
		assert_that( stats.TimedAssignmentCount, is_( 1 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 1 ))

	@fudge.patch( 'nti.learning_network.data.production.get_self_assessments_for_user' )
	def test_assessment_stats( self, mock_get_assessments ):
		user = self._get_user()

		# Empty
		mock_get_assessments.is_callable().returns( None )
		stats = self.stat_source.SelfAssessmentStats
		assert_that( stats.Count, is_( 0 ))
		assert_that( stats.UniqueCount, is_( 0 ) )

		mock_get_assessments.is_callable().returns( () )
		stats = self.stat_source.SelfAssessmentStats
		assert_that( stats.Count, is_( 0 ))
		assert_that( stats.UniqueCount, is_( 0 ) )

		# Single
		assignment_id = 'assignment1'
		submission = _get_assessed_question_set()
		assignment = _get_assessment( assignment_id, user, submission )
		assignments = ( assignment, )
		mock_get_assessments.is_callable().returns( assignments )

		stats = self.stat_source.SelfAssessmentStats
		assert_that( stats.Count, is_( 1 ))
		assert_that( stats.UniqueCount, is_( 1 ))

		# Second
		assignment_id2 = 'assignment2'
		assignment2 = _get_assessment( assignment_id2, user, submission )
		assignments = ( assignment, assignment2 )
		mock_get_assessments.is_callable().returns( assignments )

		stats = self.stat_source.SelfAssessmentStats
		assert_that( stats.Count, is_( 2 ))
		assert_that( stats.UniqueCount, is_( 2 ))

		# Dupe
		assignment3 = _get_assessment( assignment_id, user, submission )
		assignments = ( assignment, assignment2, assignment3 )
		mock_get_assessments.is_callable().returns( assignments )

		stats = self.stat_source.SelfAssessmentStats
		assert_that( stats.Count, is_( 3 ))
		assert_that( stats.UniqueCount, is_( 2 ))

	@fudge.patch( 'nti.learning_network.data.production.get_blogs',
				 'nti.learning_network.data.production.get_blog_comments')
	def test_blog_stats( self, mock_get_blogs, mock_get_blog_comments ):
		user = self._get_user()
		# Empty
		mock_get_blogs.is_callable().returns( None )
		mock_get_blog_comments.is_callable().returns( None )
		assert_that( self.stat_source.ThoughtStats.Count, is_( 0 ) )
		assert_that( self.stat_source.ThoughtCommentStats.Count, is_( 0 ) )
		assert_that( self.stat_source.ThoughtCommentStats.ReplyCount, is_( 0 ) )

		mock_get_blogs.is_callable().returns( () )
		mock_get_blog_comments.is_callable().returns( () )
		assert_that( self.stat_source.ThoughtStats.Count, is_( 0 ) )
		assert_that( self.stat_source.ThoughtCommentStats.Count, is_( 0 ) )
		assert_that( self.stat_source.ThoughtCommentStats.ReplyCount, is_( 0 ) )

		# Blog, comment with one reply, and that reply
		blog_container = PersonalBlog()
		blog = PersonalBlogEntry()
		blog.headline = PersonalBlogEntryPost()
		blog.__parent__ = blog_container
		blog.creator = user
		comment1 = PersonalBlogComment()
		comment1.creator = user
		comment1.__parent__ = blog

		comment2 = PersonalBlogComment()
		comment2.creator = user
		comment2.__parent__ = blog

		blog_record = _get_blog( blog, user )
		blog_comment_record1 = _get_blog_comment( comment1, user )
		like_count = 10
		fave_count = 5
		blog_comment_record2 = _get_blog_comment( comment2, user, is_reply=True,
												like_count=10, fave_count=5 )

		mock_get_blogs.is_callable().returns( (blog_record,) )
		stats = self.stat_source.ThoughtStats
		assert_that( stats.Count, is_( 1 ) )

		# One comment
		mock_get_blog_comments.is_callable().returns( (blog_comment_record1,) )
		stats = self.stat_source.ThoughtCommentStats
		assert_that( stats.Count, is_( 1 ) )
		assert_that( stats.ReplyCount, is_( 0 ) )
		assert_that( stats.TopLevelCount, is_( 1 ) )
		assert_that( stats.DistinctPostsLiked, is_( 0 ) )
		assert_that( stats.DistinctPostsFavorited, is_( 0 ) )
		assert_that( stats.TotalLikes, is_( 0 ) )
		assert_that( stats.RecursiveChildrenCount, is_( 0 ) )
		assert_that( stats.StandardDeviationLength, is_( 0 ) )
		assert_that( stats.AverageLength, is_( 30 ) )
		assert_that( stats.ContainsWhiteboardCount, is_( 0 ) )

		# Two comments
		mock_get_blog_comments.is_callable().returns(
								(blog_comment_record1, blog_comment_record2) )
		stats = self.stat_source.ThoughtCommentStats
		assert_that( stats.Count, is_( 2 ) )
		assert_that( stats.ReplyCount, is_( 1 ) )
		assert_that( stats.TopLevelCount, is_( 1 ) )
		assert_that( stats.DistinctPostsLiked, is_( 1 ) )
		assert_that( stats.DistinctPostsFavorited, is_( 1 ) )
		assert_that( stats.TotalLikes, is_( like_count ) )
		assert_that( stats.TotalFavorites, is_( fave_count ) )
		assert_that( stats.RecursiveChildrenCount, is_( 0 ) ) # Need to test this
		assert_that( stats.StandardDeviationLength, is_( 0 ) )
		assert_that( stats.AverageLength, is_( 30 ) )
		assert_that( stats.ContainsWhiteboardCount, is_( 0 ) )

	@fudge.patch( 'nti.learning_network.data.production.get_highlights' )
	def test_highlight_stats( self, mock_get_highlights ):
		# Empty
		mock_get_highlights.is_callable().returns( None )
		assert_that( self.stat_source.HighlightStats.Count, is_( 0 ) )

		mock_get_highlights.is_callable().returns( () )
		assert_that( self.stat_source.HighlightStats.Count, is_( 0 ) )

		# We simply get counts....
		highlights = [object()]
		mock_get_highlights.is_callable().returns( highlights )
		assert_that( self.stat_source.HighlightStats.Count, is_( len( highlights ) ) )

		highlights = [object(), object(), object()]
		mock_get_highlights.is_callable().returns( highlights )
		assert_that( self.stat_source.HighlightStats.Count, is_( len( highlights ) ) )

	@fudge.patch( 'nti.learning_network.data.production.get_bookmarks' )
	def test_bookmark_stats( self, mock_get_bookmarks ):
		# Empty
		mock_get_bookmarks.is_callable().returns( None )
		assert_that( self.stat_source.BookmarkStats.Count, is_( 0 ) )

		mock_get_bookmarks.is_callable().returns( () )
		assert_that( self.stat_source.BookmarkStats.Count, is_( 0 ) )

		# We simply get counts....
		bookmarks = [object()]
		mock_get_bookmarks.is_callable().returns( bookmarks )
		assert_that( self.stat_source.BookmarkStats.Count, is_( len( bookmarks ) ) )

		bookmarks = [object(), object(), object()]
		mock_get_bookmarks.is_callable().returns( bookmarks )
		assert_that( self.stat_source.BookmarkStats.Count, is_( len( bookmarks ) ) )

	# FIXME Note, comment stats

class TestAdapters( LearningNetworkTestCase ):

	def test_adapting(self):
		user = User( username='blehxxxxxxxx' )
		now = datetime.utcnow()

		stats_source = component.queryMultiAdapter( ( user, course, now ), IProductionStatsSource )
		assert_that( stats_source, not_none() )

		stats_source = component.queryMultiAdapter( ( user, course ), IProductionStatsSource )
		assert_that( stats_source, not_none() )

		stats_source = IProductionStatsSource( user )
		assert_that( stats_source, not_none() )
