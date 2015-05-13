#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import fudge
import unittest

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import assert_that

from . import MockTimeRecord
from ..access import _AnalyticsAccessStatsSource

class TestAccess( unittest.TestCase ):

	def setUp(self):
		self.user = None
		self.stat_source = _AnalyticsAccessStatsSource( self.user )

	@fudge.patch( 'nti.learning_network.data.access.get_user_sessions' )
	def test_platform_stats(self, mock_get_sessions):
		# Empty
		mock_get_sessions.is_callable().returns( None )
		platform_stats = self.stat_source.get_platform_stats()
		assert_that( platform_stats, none() )

		mock_get_sessions.is_callable().returns( [] )
		platform_stats = self.stat_source.get_platform_stats()
		assert_that( platform_stats, none() )

		# Without end time
		records = [ MockTimeRecord( 10, None ), MockTimeRecord( 10, None ) ]
		mock_get_sessions.is_callable().returns( records )
		platform_stats = self.stat_source.get_platform_stats()
		assert_that( platform_stats, none() )

		# Single valid
		records = [ MockTimeRecord( 10, 1 ), MockTimeRecord( 10, 0 ) ]
		mock_get_sessions.is_callable().returns( records )
		platform_stats = self.stat_source.get_platform_stats()
		assert_that( platform_stats, not_none() )
		assert_that( platform_stats.average, is_( 10 ) )
		assert_that( platform_stats.count, is_( 1 ) )
		assert_that( platform_stats.std_dev, is_( 0 ) )
		assert_that( platform_stats.aggregate_time, is_( 10 ) )

		# Multiple valid
		records = [ MockTimeRecord( 10, 1 ),
					MockTimeRecord( 10, None ),
					MockTimeRecord( 20, 1 ),
					MockTimeRecord( 30, 1 ),
					MockTimeRecord( 40, 1 ) ]
		mock_get_sessions.is_callable().returns( records )
		platform_stats = self.stat_source.get_platform_stats()
		assert_that( platform_stats, not_none() )
		assert_that( platform_stats.average, is_( 25 ) )
		assert_that( platform_stats.count, is_( 4 ) )
		assert_that( platform_stats.aggregate_time, is_( 100 ) )



