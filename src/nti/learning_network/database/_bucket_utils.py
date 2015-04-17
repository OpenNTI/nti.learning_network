#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from datetime import timedelta

from nti.analytics.database.users import get_user_db_id
from nti.analytics.database.users import get_or_create_user
from nti.analytics.database.root_context import get_root_context_id

from . import get_analytics_db

def get_bucket_boundaries( timestamp ):
	"""
	Get our bucket boundaries (as tuple) for the given timestamp.
	"""
	beginning = timestamp.replace(hour=0, minute=0,
								second=0, microsecond=0)
	ending = beginning + timedelta( days=1 )
	return beginning, ending

def create_bucket_for_timestamp( db, table, user_id, timestamp, **kwargs ):
	"""
	Create a bounded bucket for the give user, table, timestamp.
	"""
	beginning, ending = get_bucket_boundaries( timestamp )

	effective_kwargs = {'user_id': user_id,
						'last_modified': timestamp,
						'bucket_start_time': beginning,
						'bucket_end_time': ending }
	effective_kwargs.update( kwargs )

	result = table( **effective_kwargs )
	db.session.add( result )
	return result

def get_bucket_for_timestamp( table, timestamp, user, create=False ):
	"""
	Get the bounded bucket record for the give user, table, timestamp;
	creating on request.
	"""
	db = get_analytics_db()
	if create:
		user = get_or_create_user( user )
		user_id = user.user_id
	else:
		user_id = get_user_db_id( user )

	result = None

	if user_id:
		result = db.session.query( table ).filter(
						table.user_id == user_id,
						table.bucket_start_time <= timestamp,
						table.bucket_end_time > timestamp ).first()

	if result is None and create:
		result = create_bucket_for_timestamp( db, table, user_id, timestamp )
	return result

def get_course_bucket_for_timestamp( table, timestamp, user, course=None, create=False ):
	"""
	Get the bounded bucket record for the give user, table, course, timestamp;
	creating on request.  A ``None`` course indicates an aggregate across
	all courses.
	"""
	db = get_analytics_db()
	result = None

	if create:
		user = get_or_create_user( user )
		user_id = user.user_id
	else:
		user_id = get_user_db_id( user )

	# A None course would indicate a global aggregate
	course_id = get_root_context_id( db, course, create=create ) if course else None

	# Only query if we have a course (w/course_id) or no course at all.
	# We don't want to return the global record for a course without a
	# db id yet (in a read).
	if 		( course is None or course_id is not None ) \
		and user_id:
			result = db.session.query( table ).filter(
							table.user_id == user_id,
							table.course_id == course_id,
							table.bucket_start_time <= timestamp,
							table.bucket_end_time >= timestamp ).first()

	if result is None and create:
		result = create_bucket_for_timestamp( db, table, user_id,
											timestamp, course_id=course_id )
	return result
