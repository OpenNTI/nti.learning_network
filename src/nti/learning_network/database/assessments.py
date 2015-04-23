#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy import Integer

from sqlalchemy.schema import Sequence

from nti.analytics.assessments import get_assignment_for_user
from nti.analytics.assessments import get_self_assessments_for_user_and_id

from nti.assessment.interfaces import IQTimedAssignment
from nti.assessment.interfaces import IQAssignmentDateContext

from nti.app.assessment.interfaces import IUsersCourseAssignmentHistoryItem

from . import Base

from ._utils import increment_field
from ._bucket_utils import get_bounded_buckets
from ._bucket_utils import get_course_bucket_for_timestamp
from .meta_mixins import CourseLearningNetworkTableMixin

from ..model import AggregateAssessmentStats

class AssessmentProduction( Base, CourseLearningNetworkTableMixin ):
	__tablename__ = 'AssessmentProduction'

	assessment_prod_id = Column('assessment_prod_id', Integer, Sequence( 'assessment_prod_seq' ),
							index=True, nullable=False, primary_key=True )

	assessment_count = Column('assessment_count', Integer, nullable=True )
	assessment_unique_count = Column('assessment_unique_count', Integer, nullable=True )

	assignment_count = Column('assignment_count', Integer, nullable=True )
	assignment_unique_count = Column('assignment_unique_count', Integer, nullable=True )
	assignment_late_count = Column('assigment_late_count', Integer, nullable=True )

	assignment_timed_count = Column('assignment_timed_count', Integer, nullable=True )
	assignment_timed_late_count = Column('assignment_timed_late_count', Integer, nullable=True )

def _is_first_time( user, assessment_id, assessment_call ):
	# The given assessment should already exist
	results = assessment_call( user, assessment_id )
	return bool( not results or len( results ) == 1 )

def _is_late( course, assessment ):
	assignment = assessment.Assignment
	date_context = IQAssignmentDateContext( course )
	due_date = date_context.of( assignment ).available_for_submission_ending
	submitted_late = assessment.created > due_date if due_date else False
	return submitted_late

def update_assessment( user, timestamp, assessment, course ):
	bucket_record = get_course_bucket_for_timestamp(
							AssessmentProduction, timestamp,
							user, course, create=True )

	bucket_record.last_modified = timestamp

	assessment_id = assessment.questionSetId
	is_first_time = _is_first_time( user, assessment_id, get_self_assessments_for_user_and_id )

	increment_field( bucket_record, 'assessment_count' )
	if is_first_time:
		increment_field( bucket_record, 'assessment_unique_count' )

def update_assignment( user, timestamp, assessment, course ):
	bucket_record = get_course_bucket_for_timestamp(
							AssessmentProduction, timestamp,
							user, course, create=True )

	# Timed assignments are aggregated in assignment columns as well.
	assessment_id = assessment.assignmentId
	is_first_time = _is_first_time( user, assessment_id, get_assignment_for_user )
	is_late = _is_late( course, assessment )

	increment_field( bucket_record, 'assignment_count' )
	if is_late:
		increment_field( bucket_record, 'assignment_late_count' )

	if is_first_time:
		increment_field( bucket_record, 'assignment_unique_count' )

	if IQTimedAssignment.providedBy( assessment.Assignment ):
		increment_field( bucket_record, 'assignment_timed_count' )
		if is_late:
			increment_field( bucket_record, 'assignment_timed_late_count' )

def get_aggregate_assessment_stats( user, timestamp=None ):
	"""
	Get the platform stats for a user starting at the beginning timestamp, inclusive.
	"""
	result = None
	assessment_records = get_bounded_buckets( user, AssessmentProduction, timestamp )

	field_map = { 'assessment_count':'SelfAssessmentCount',
					'assessment_unique_count':'UniqueSelfAssessmentCount',
					'assignment_unique_count':'UniqueAssignmentCount',
					'assignment_count':'AssignmentCount',
					'assignment_late_count':'AssignmentLateCount',
					'assignment_timed_count':'TimedAssignmentCount',
					'assignment_timed_late_count':'TimedAssignmentLateCount' }

	if assessment_records:
		accum = {}

		def accum_fields( obj ):
			for db_field, stat_field in field_map.items():
				field_delta = getattr( obj, db_field ) or 0
				val = accum.setdefault( stat_field, 0 )
				accum[stat_field] = val + field_delta

		map( accum_fields, assessment_records )

		result = AggregateAssessmentStats( **accum )
	return result
