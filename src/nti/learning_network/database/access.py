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

from . import Base

from ._stat_utils import get_aggregate_stats
from ._stat_utils import update_record_stats
from ._bucket_utils import get_bounded_buckets
from ._bucket_utils import get_bucket_for_timestamp
from ._bucket_utils import get_course_bucket_for_timestamp

from .meta_mixins import StatMixin
from .meta_mixins import LearningNetworkTableMixin
from .meta_mixins import CourseLearningNetworkTableMixin

class _LearningAccessZones( CourseLearningNetworkTableMixin, StatMixin ):
	pass

class DiscussionAccess( Base, _LearningAccessZones ):
	__tablename__ = 'DiscussionAccess'

	discussion_access_id = Column('discussion_access_id', Integer, Sequence( 'discussion_access_seq' ),
							index=True, nullable=False, primary_key=True )

class VideoAccess( Base, _LearningAccessZones ):
	__tablename__ = 'VideoAccess'

	video_access_id = Column('video_access_id', Integer, Sequence( 'video_access_seq' ),
							index=True, nullable=False, primary_key=True )

class ReadingAccess( Base, _LearningAccessZones ):
	__tablename__ = 'ReadingAccess'

	reading_access_id = Column('reading_access_id', Integer, Sequence( 'reading_access_seq' ),
							index=True, nullable=False, primary_key=True )

class SelfAssessmentAccess( Base, _LearningAccessZones ):
	__tablename__ = 'SelfAssessmentAccess'

	assessment_access_id = Column('assessment_access_id', Integer, Sequence( 'assessment_access_seq' ),
							index=True, nullable=False, primary_key=True )

class AssignmentAccess( Base, _LearningAccessZones ):
	__tablename__ = 'AssignmentAccess'

	assignment_access_id = Column('assignment_access_id', Integer, Sequence( 'discussion_access_seq' ),
							index=True, nullable=False, primary_key=True )

class PlatformAccess( Base, LearningNetworkTableMixin, StatMixin ):
	__tablename__ = 'PlatformAccess'

	platform_access_id = Column('platform_access_id', Integer, Sequence( 'platform_access_seq' ),
							index=True, nullable=False, primary_key=True )

def _update_access_for_table( table, user, timestamp, duration, course=None ):
	bucket_record = get_course_bucket_for_timestamp(
							table, timestamp,
							user, course, create=True )
	bucket_record.last_modified = timestamp
	update_record_stats( bucket_record, duration )

def update_discussion_access( user, timestamp, duration, course=None ):
	_update_access_for_table( DiscussionAccess, user, timestamp, duration, course=course )

def update_video_access( user, timestamp, duration, course=None ):
	_update_access_for_table( VideoAccess, user, timestamp, duration, course=course )

def update_reading_access( user, timestamp, duration, course=None ):
	_update_access_for_table( ReadingAccess, user, timestamp, duration, course=course )

def update_assessment_access( user, timestamp, duration, course=None ):
	_update_access_for_table( SelfAssessmentAccess, user, timestamp, duration, course=course )

def update_assignment_access( user, timestamp, duration, course=None ):
	_update_access_for_table( AssignmentAccess, user, timestamp, duration, course=course )

def update_platform_access( user, timestamp, duration ):
	bucket_record = get_bucket_for_timestamp( PlatformAccess, timestamp,
											user, create=True )
	bucket_record.last_modified = timestamp
	update_record_stats( bucket_record, duration )

def get_platform_stats( user, timestamp=None ):
	"""
	Get the platform stats for a user starting at the beginning timestamp, inclusive.
	"""
	stats = get_bounded_buckets( user, PlatformAccess, timestamp )
	stats = get_aggregate_stats( stats )
	return stats
