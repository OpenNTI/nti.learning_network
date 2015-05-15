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
from hamcrest import assert_that

from datetime import datetime

from zope.interface import directlyProvides

from nti.analytics.read_models import AnalyticsAssignment

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

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from ..production import _AnalyticsProductionStatsSource

from nti.learning_network.tests import LearningNetworkTestCase

course = CourseInstance()
_question_id = '1968'
_question_set_id = '2'
_assignment_id = 'b'
_assignment_ntiid = 'tag:nextthought:bleh'
_response = 'bleh'
test_user_ds_id = 9999

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
	result_creator = Principal( username=str( test_user_ds_id ) )
	directlyProvides( result_creator, IUser )
	result_creator.__dict__['_ds_intid'] = test_user_ds_id
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

class TestProduction( LearningNetworkTestCase ):

	def setUp(self):
		self.user = None
		self.stat_source = _AnalyticsProductionStatsSource( self.user )

	@WithMockDSTrans
	def _get_user(self):
		return User.create_user( username='new_user1', dataserver=self.ds )

	@fudge.patch( 'nti.learning_network.data.production.get_assignments_for_user' )
	def test_assessment_stats( self, mock_get_assignments ):
		# Empty
		mock_get_assignments.is_callable().returns( None )
		stats = self.stat_source.get_assignment_stats()
		assert_that( stats, none() )

		mock_get_assignments.is_callable().returns( () )
		stats = self.stat_source.get_assignment_stats()
		assert_that( stats, none() )

		user = self._get_user()
		# Single
		assignment_id = 'assignment1'
		submission, _ = _get_history_item()
		assignment = _get_assignment( assignment_id, user, submission )
		assignments = ( assignment, )
		mock_get_assignments.is_callable().returns( assignments )

		stats = self.stat_source.get_assignment_stats()
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

		stats = self.stat_source.get_assignment_stats()
		assert_that( stats.Count, is_( 2 ))
		assert_that( stats.UniqueCount, is_( 2 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Double, late
		assignment3 = _get_assignment( assignment_id, user, submission, is_late=True )
		assignments = ( assignment, assignment2, assignment3 )
		mock_get_assignments.is_callable().returns( assignments )

		stats = self.stat_source.get_assignment_stats()
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

		stats = self.stat_source.get_assignment_stats()
		assert_that( stats.Count, is_( 4 ))
		assert_that( stats.UniqueCount, is_( 3 ))
		assert_that( stats.AssignmentLateCount, is_( 2 ))
		assert_that( stats.TimedAssignmentCount, is_( 1 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 1 ))
