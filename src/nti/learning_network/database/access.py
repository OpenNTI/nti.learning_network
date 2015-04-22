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

from nti.analytics.database.users import get_user_db_id

from . import Base
from . import get_learning_db

from ._stat_utils import get_aggregate_stats
from ._stat_utils import update_record_stats
from ._bucket_utils import get_bucket_boundaries
from ._bucket_utils import get_bucket_for_timestamp
from ._bucket_utils import get_course_bucket_for_timestamp

from .meta_mixins import StatMixin
from .meta_mixins import LearningNetworkTableMixin
from .meta_mixins import CourseLearningNetworkTableMixin

class LearningAccessZones( Base, CourseLearningNetworkTableMixin, StatMixin ):
	__tablename__ = 'LearningAccessZones'

	access_zones_id = Column('access_zones_id', Integer, Sequence( 'access_zones_seq' ),
							index=True, nullable=False, primary_key=True )

class PlatformAccess( Base, LearningNetworkTableMixin, StatMixin ):
	__tablename__ = 'PlatformAccess'

	platform_access_id = Column('platform_access_id', Integer, Sequence( 'platform_access_seq' ),
							index=True, nullable=False, primary_key=True )

def update_access_zones( user, timestamp, duration, course=None ):
	bucket_record = get_course_bucket_for_timestamp(
							LearningAccessZones, timestamp,
							user, course, create=True )
	bucket_record.last_modified = timestamp
	update_record_stats( bucket_record, duration )

def update_platform_access( user, timestamp, duration ):
	bucket_record = get_bucket_for_timestamp( PlatformAccess, timestamp,
											user, create=True )
	bucket_record.last_modified = timestamp
	update_record_stats( bucket_record, duration )

def get_platform_stats( user, timestamp=None ):
	"""
	Get the platform stats for a user starting at the beginning timestamp, inclusive.
	"""
	db = get_learning_db()
	user_id = get_user_db_id( user )
	if timestamp is None:
		stats = db.session.query( PlatformAccess ).filter(
								PlatformAccess.user_id == user_id ).all()
	else:
		beginning, _ = get_bucket_boundaries( timestamp )
		stats = db.session.query( PlatformAccess ).filter(
								PlatformAccess.user_id == user_id,
								PlatformAccess.bucket_start_time >= beginning ).all()

	stats = get_aggregate_stats( stats )
	return stats
