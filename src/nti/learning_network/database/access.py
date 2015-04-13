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

from .common import get_bucket_for_timestamp
from .common import get_course_bucket_for_timestamp
from .meta_mixins import StatMixin
from .meta_mixins import LearningNetworkTableMixin
from .meta_mixins import CourseLearningNetworkTableMixin

class LearningAccessZones( CourseLearningNetworkTableMixin, StatMixin ):
	__tablename__ = 'LearningAccessZones'

	access_zones_id = Column('access_zones_id', Integer, Sequence( 'access_zones_seq' ),
							index=True, nullable=False, primary_key=True )

class PlatformAccess( LearningNetworkTableMixin, StatMixin ):
	__tablename__ = 'PlatformAccess'

	platform_access_id = Column('platform_access_id', Integer, Sequence( 'platform_access_seq' ),
							index=True, nullable=False, primary_key=True )

def update_access_zones( user, timestamp, duration, course=None ):
	bucket_record = get_course_bucket_for_timestamp(
							LearningAccessZones, timestamp,
							user, course, create=True )
	bucket_record.count += 1
	bucket_record.total_duration += duration

def update_platform_access( user, timestamp, duration ):
	bucket_record = get_bucket_for_timestamp( PlatformAccess, timestamp,
											user, create=True )
	bucket_record.count += 1
	bucket_record.total_duration += duration
