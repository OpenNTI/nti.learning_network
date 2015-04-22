#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from datetime import datetime
from datetime import timedelta

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import assert_that

from nti.analytics.recorded.interfaces import AnalyticsSessionRecordedEvent

from nti.dataserver.users import User

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from . import NTIAnalyticsTestCase

from ..access import _analytics_session
from ..access import get_platform_stats

class TestAccess( NTIAnalyticsTestCase ):

	@WithMockDSTrans
	def test_platform_access(self):
		start = datetime( year=2007, month=3, day=6,
							hour=6, minute=10, second=30 )
		seconds_delta = 3600
		end = start + timedelta( seconds=seconds_delta )
		user = User.create_user( username='new_user1', dataserver=self.ds )
		now = datetime.utcnow()

		# Test start = end
		session_event = AnalyticsSessionRecordedEvent( user, start, start, now )
		_analytics_session( session_event )

		stats = get_platform_stats( user )
		assert_that( stats, none() )

		# One hour gap
		session_event = AnalyticsSessionRecordedEvent( user, start, end, now )
		_analytics_session( session_event )

		stats = get_platform_stats( user )
		assert_that( stats, not_none() )
		assert_that( stats.average, is_( seconds_delta ) )
		assert_that( stats.std_dev, is_( 0 ))

		# Give timestamp boundary (nothing changes)
		time_bounded_stats = get_platform_stats( user, timestamp=start )
		assert_that( time_bounded_stats, is_( stats ))


