#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from zope.cachedescriptors.property import Lazy

# TODO: Break dependency
from nti.app.products.gradebook.grading import calculate_predicted_grade

from nti.analytics.assessments import get_assignments_for_user

from nti.assessment.interfaces import IQTimedAssignment

from nti.contenttypes.courses.interfaces import ICourseAssignmentCatalog
from nti.contenttypes.courses.interfaces import get_course_assessment_predicate_for_user

from nti.contenttypes.courses.grading import find_grading_policy_for_course

from nti.learning_network.interfaces import IOutcomeStatsSource

from nti.learning_network.model import AssignmentOutcomeStats

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IOutcomeStatsSource)
class _AnalyticsOutcomeStatsSource(object):
    """
    A outcome stats source that pulls data from analytics.
    """
    __external_class_name__ = "OutcomeStatsSource"
    mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.outcomestatssource'

    display_name = 'Outcome'

    def __init__(self, user, course=None, timestamp=None, max_timestamp=None):
        self.user = user
        self.course = course
        self.timestamp = timestamp
        self.max_timestamp = max_timestamp

    def _get_predicted_grade(self, user, grade_policy):
        result = calculate_predicted_grade(user, grade_policy)
        return result

    def _get_course_maxes(self):
        # TODO: Cache this
        catalog = ICourseAssignmentCatalog(self.course, None)
        count = point_count = 0
        if catalog is not None:
            uber_filter = get_course_assessment_predicate_for_user(self.user,
                                                                   self.course)
            for asg in (x for x in catalog.iter_assignments() if uber_filter(x)):

                for part in asg.parts:
                    try:
                        qs = part.question_set
                        for qs_part in qs.parts:
                            for q_part in qs_part.parts:
                                for solution in q_part.solutions:
                                    point_count += int(solution.weight)
                    except AttributeError:
                        pass
                count += 1
        return count, point_count

    @Lazy
    def AssignmentStats(self):
        """
        Return the learning network stats for assignments, optionally
        with a course or timestamp filter.
        """
        assignments = get_assignments_for_user(self.user, course=self.course,
                                               timestamp=self.timestamp)
        count = unique_count = 0
        late_count = timed_count = timed_late_count = total_points = 0
        final_grade_alpha = final_grade = average_grade = None

        if assignments:
            id_set = set()
            for assignment_record in assignments:
                if assignment_record.Submission is None:
                    continue
                count += 1
                id_set.add(assignment_record.AssignmentId)

                if     'final_grade' in assignment_record.AssignmentId.lower() \
                    or 'final_letter_grade' in assignment_record.AssignmentId.lower():
                    final_grade_alpha = assignment_record.Grade
                    final_grade = assignment_record.GradeNum

                if assignment_record.IsLate:
                    late_count += 1

                assignment = assignment_record.Submission.Assignment

                if IQTimedAssignment.providedBy(assignment):
                    timed_count += 1
                    if assignment_record.IsLate:
                        timed_late_count += 1

                if assignment_record.GradeNum:
                    if 'Final_Exam' in assignment_record.AssignmentId:
                        # TODO: For some courses (e.g. LSTD), the final exam
                        # grade is worth a certain amount of points in the
                        # syllabus, such that we need a multiplier.  This is
                        # hard until we have more data available to us.
                        pt_delta = assignment_record.GradeNum
                    else:
                        pt_delta = assignment_record.GradeNum
                    total_points += pt_delta

            unique_count = len(id_set)

        if final_grade is None:
            grade_policy = find_grading_policy_for_course(self.course)
            if grade_policy is not None:
                predicted_grade = self._get_predicted_grade(self.user,
                                                            grade_policy)
                if predicted_grade is not None:
                    final_grade = predicted_grade.Correctness
                    final_grade_alpha = predicted_grade.Grade

        max_assignment_count, max_point_count = self._get_course_maxes()

        stats = AssignmentOutcomeStats(Count=count,
                                       UniqueCount=unique_count,
                                       AssignmentLateCount=late_count,
                                       TimedAssignmentCount=timed_count,
                                       TimedAssignmentLateCount=timed_late_count,
                                       FinalGradeAlpha=final_grade_alpha,
                                       FinalGradeNumeric=final_grade,
                                       AverageGrade=average_grade,
                                       TotalPoints=total_points,
                                       MaxPointCount=max_point_count,
                                       MaxAssignmentCount=max_assignment_count)
        return stats
