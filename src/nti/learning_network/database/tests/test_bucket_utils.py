#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from datetime import datetime

from unittest import TestCase

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import assert_that

from nti.contenttypes.courses.courses import CourseInstance

from nti.dataserver.users import User

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from . import NTIAnalyticsTestCase

from .._bucket_utils import get_bucket_boundaries
from .._bucket_utils import get_bucket_for_timestamp
from .._bucket_utils import get_course_bucket_for_timestamp

from ..access import PlatformAccess
from ..access import LearningAccessZones

class TestBucketUtils( TestCase ):

	def test_bucket_boundaries( self ):
		event_date = datetime( year=2007, month=3, day=6,
								hour=6, minute=10, second=30 )
		early_expected = datetime( year=2007, month=3, day=6 )
		late_expected = datetime( year=2007, month=3, day=7 )

		early_bound, late_bound = get_bucket_boundaries( event_date )
		assert_that( early_bound, is_( early_expected ))
		assert_that( late_bound, is_( late_expected ))


class TestBucketTables( NTIAnalyticsTestCase ):

	def setUp(self):
		self.course = CourseInstance()
		self.course.ContentPackageNTIID = '9999'

	@WithMockDSTrans
	def test_buckets(self):
		table = PlatformAccess
		timestamp = datetime( year=2007, month=3, day=6,
							hour=6, minute=10, second=30 )

		user = User.create_user( username='new_user1', dataserver=self.ds )
		# No record exists, none returned
		bucket_record = get_bucket_for_timestamp( table, timestamp, user )
		assert_that( bucket_record, none() )

		# Lazy create
		bucket_record = get_bucket_for_timestamp( table, timestamp, user, create=True )
		assert_that( bucket_record, not_none() )

		bucket_record2 = get_bucket_for_timestamp( table, timestamp, user )
		assert_that( bucket_record2, not_none() )
		assert_that( bucket_record2, is_( bucket_record ))

		# Boundary condition, following midnight returns nothing.
		timestamp = datetime( year=2007, month=3, day=7 )
		bucket_record = get_bucket_for_timestamp( table, timestamp, user )
		assert_that( bucket_record, none() )

	@WithMockDSTrans
	def test_course_buckets(self):
		table = LearningAccessZones
		timestamp = datetime.utcnow()
		user = User.create_user( username='new_user1', dataserver=self.ds )
		course = None

		# None course, global record
		# No record exists, none returned
		bucket_record = get_course_bucket_for_timestamp( table, timestamp, user, course )
		assert_that( bucket_record, none() )

		# Lazy create
		bucket_record = get_course_bucket_for_timestamp( table, timestamp, user, course, create=True )
		assert_that( bucket_record, not_none() )

		bucket_record2 = get_course_bucket_for_timestamp( table, timestamp, user, course )
		assert_that( bucket_record2, not_none() )
		assert_that( bucket_record2, is_( bucket_record ))

		# Now with course
		course = self.course
		# No record exists, none returned
		bucket_record = get_course_bucket_for_timestamp( table, timestamp, user, course )
		assert_that( bucket_record, none() )

		# Lazy create
		bucket_record = get_course_bucket_for_timestamp( table, timestamp, user, course, create=True )
		assert_that( bucket_record, not_none() )

		bucket_record2 = get_course_bucket_for_timestamp( table, timestamp, user, course )
		assert_that( bucket_record2, not_none() )
		assert_that( bucket_record2, is_( bucket_record ))
