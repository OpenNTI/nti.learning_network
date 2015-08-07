#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.app.products.gradebook.grading import calculate_predicted_grade
from nti.app.products.gradebook.grading import find_grading_policy_for_course

from nti.assessment.interfaces import IQTimedAssignment

from nti.analytics.assessments import get_assignments_for_user

from nti.common.property import readproperty

from nti.learning_network.interfaces import IOutcomeStatsSource

from nti.learning_network.model import AssignmentOutcomeStats

@interface.implementer(IOutcomeStatsSource)
class _AnalyticsOutcomeStatsSource(object):
	"""
	A outcome stats source that pulls data from analytics.
	"""
	__external_class_name__ = "OutcomeStatsSource"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.outcomestatssource'

	def __init__(self, user, course=None, timestamp=None):
		self.user = user
		self.course = course
		self.timestamp = timestamp

	def _get_predicted_grade(self, user, grade_policy):
		result = calculate_predicted_grade( user, grade_policy )
		return result

	@readproperty
	def AssignmentStats(self):
		"""
		Return the learning network stats for assignments, optionally
		with a course or timestamp filter.
		"""
		assignments = get_assignments_for_user(self.user, course=self.course,
											   timestamp=self.timestamp)
		count = unique_count = 0
		late_count = timed_count = timed_late_count = 0
		final_grade_alpha = final_grade = average_grade = None

		if assignments:
			id_set = set()
			for assignment_record in assignments:
				count += 1
				id_set.add(assignment_record.AssignmentId)

				if 'final_grade' in assignment_record.AssignmentId.lower():
					final_grade_alpha = assignment_record.Grade
					final_grade = assignment_record.GradeNum

				if assignment_record.IsLate:
					late_count += 1

				assignment = assignment_record.Submission.Assignment

				if IQTimedAssignment.providedBy(assignment):
					timed_count += 1
					if assignment_record.IsLate:
						timed_late_count += 1

			unique_count = len(id_set)

		if final_grade is None:
			grade_policy = find_grading_policy_for_course( self.course )
			if grade_policy is not None:
				predicted_grade = self._get_predicted_grade( self.user, grade_policy )
				final_grade = predicted_grade.Correctness
				final_grade_alpha = predicted_grade.Grade

		stats = AssignmentOutcomeStats(Count=count,
								UniqueCount=unique_count,
								AssignmentLateCount=late_count,
								TimedAssignmentCount=timed_count,
								TimedAssignmentLateCount=timed_late_count,
								FinalGradeAlpha=final_grade_alpha,
								FinalGradeNumeric=final_grade,
								AverageGrade=average_grade )
		return stats
