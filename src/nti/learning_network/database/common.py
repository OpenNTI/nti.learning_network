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

from nti.analytics.learning_network.database import get_analytics_db

def _get_new_variance( new_count, old_total, delta, old_sum_of_squares ):
	"""
	"""
	result = ( old_sum_of_squares + delta ** 2 ) / new_count \
			- ( ( old_total + delta ) / new_count ) ** 2
	return result

def increment_variance( old_record, duration_delta ):
	old_total = old_record.total_duration
	old_sum_of_squares = old_record.sum_of_squares

	old_count = old_record.count
	new_count = old_count + 1

	new_variance = _get_new_variance( new_count, old_total,
									duration_delta, old_sum_of_squares )
	return new_variance


def get_bucket_boundaries( timestamp ):
	"""
	Get our bucket boundaries (as tuple) for the given timestamp.
	"""
	beginning = timestamp.replace(hour=0, minute=0,
								second=0, microsecond=0)
	ending = beginning + timedelta( days=1 )
	return beginning, ending

def create_bucket_for_timestamp( db, table, user, timestamp ):
	"""
	Create a bounded bucket for the give user, table, timestamp.
	"""
	user = get_or_create_user( user )
	user_id = user.user_id

	beginning, ending = get_bucket_boundaries( timestamp )

	result = table( user_id=user_id,
					last_modified=timestamp,
					bucket_start_time=beginning,
					bucket_end_time=ending )
	db.session.add( result )
	return result

def get_bucket_for_timestamp( table, timestamp, user, create=False ):
	"""
	Get the bounded bucket record for the give user, table, timestamp.
	"""
	db = get_analytics_db()
	user_id = get_user_db_id( user )

	if user_id:
		result = db.session.query( table ).filter(
						table.user_id == user_id,
						table.bucket_start_time >= timestamp,
						table.bucket_end_time <= timestamp ).first()

	if result is None and create:
		result = create_bucket_for_timestamp( db, table, user, timestamp )
	return result

def create_course_bucket_for_timestamp( db, table, user, timestamp, course=None ):
	"""
	Create a bounded bucket for the give user, table, course, timestamp.
	"""
	user = get_or_create_user( user )
	user_id = user.user_id

	course_id = get_root_context_id( db, course, create=True ) if course else None

	beginning, ending = get_bucket_boundaries( timestamp )

	result = table( user_id=user_id,
					last_modified=timestamp,
					bucket_start_time=beginning,
					bucket_end_time=ending,
					course_id=course_id )
	db.session.add( result )
	return result

def get_course_bucket_for_timestamp( table, timestamp, user, course=None, create=False ):
	"""
	Get the bounded bucket record for the give user, table, course, timestamp.
	"""
	db = get_analytics_db()
	user_id = get_user_db_id( user )
	course_id = get_root_context_id( db, course, create=create ) if course else None

	if user_id:
		result = db.session.query( table ).filter(
						table.user_id == user_id,
						table.course_id == course_id,
						table.bucket_start_time >= timestamp,
						table.bucket_end_time <= timestamp ).first()

	if result is None and create:
		result = create_course_bucket_for_timestamp( db, table, user,
													timestamp, course=course )
	return result
