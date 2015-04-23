#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import time
import weakref

from datetime import datetime
from datetime import timedelta

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import assert_that

from zope.interface import directlyProvides

from nti.analytics.recorded.interfaces import AnalyticsAssessmentRecordedEvent

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

from . import NTIAnalyticsTestCase

from ..assessments import _analytics_assignment
from ..assessments import _analytics_assessment
from ..assessments import get_aggregate_assessment_stats

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

def _get_history_item():
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
	result.Assignment = QAssignment()
	return result, result_creator

class TestAssessments( NTIAnalyticsTestCase ):


	def setUp(self):
		self.assignment, _ = _get_history_item()

	@WithMockDSTrans
	def test_assessments(self):
		course = CourseInstance()
		user = User.create_user( username='new_user1', dataserver=self.ds )
		now = datetime.utcnow()
		assessment = _get_assessed_question_set()

		# None
		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, none() )

		# Self assessment
		assessment_event = AnalyticsAssessmentRecordedEvent( user, assessment, course, now )
		_analytics_assessment( assessment_event )

		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 1 ))
		assert_that( stats.AssignmentCount, is_( 0 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 1 ))
		assert_that( stats.UniqueAssignmentCount, is_( 0 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# TODO test unique
		# Assignment
		assignment = self.assignment
		assignment_event = AnalyticsAssessmentRecordedEvent( user, assignment, course, now )
		_analytics_assignment( assignment_event )

		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 1 ))
		assert_that( stats.AssignmentCount, is_( 1 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 1 ))
		assert_that( stats.UniqueAssignmentCount, is_( 1 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Second self-assessment
		_analytics_assessment( assessment_event )
		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 2 ))
		assert_that( stats.AssignmentCount, is_( 1 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 2 ))
		assert_that( stats.UniqueAssignmentCount, is_( 1 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Second assignment
		_analytics_assignment( assignment_event )
		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 2 ))
		assert_that( stats.AssignmentCount, is_( 2 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 2 ))
		assert_that( stats.UniqueAssignmentCount, is_( 2 ))
		assert_that( stats.AssignmentLateCount, is_( 0 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Late
		month_ago = now - timedelta( days=30 )
		assignment.Assignment.available_for_submission_ending = month_ago

		_analytics_assignment( assignment_event )
		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 2 ))
		assert_that( stats.AssignmentCount, is_( 3 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 2 ))
		assert_that( stats.UniqueAssignmentCount, is_( 3 ))
		assert_that( stats.AssignmentLateCount, is_( 1 ))
		assert_that( stats.TimedAssignmentCount, is_( 0 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Timed
		assignment.Assignment = QTimedAssignment()
		_analytics_assignment( assignment_event )
		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 2 ))
		assert_that( stats.AssignmentCount, is_( 4 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 2 ))
		assert_that( stats.UniqueAssignmentCount, is_( 4 ))
		assert_that( stats.AssignmentLateCount, is_( 1 ))
		assert_that( stats.TimedAssignmentCount, is_( 1 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 0 ))

		# Timed late
		assignment.Assignment.available_for_submission_ending = month_ago
		_analytics_assignment( assignment_event )
		stats = get_aggregate_assessment_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.SelfAssessmentCount, is_( 2 ))
		assert_that( stats.AssignmentCount, is_( 5 ))
		assert_that( stats.UniqueSelfAssessmentCount, is_( 2 ))
		assert_that( stats.UniqueAssignmentCount, is_( 5 ))
		assert_that( stats.AssignmentLateCount, is_( 2 ))
		assert_that( stats.TimedAssignmentCount, is_( 2 ))
		assert_that( stats.TimedAssignmentLateCount, is_( 1 ))


