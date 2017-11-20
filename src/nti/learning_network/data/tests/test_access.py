#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import not_none
from hamcrest import assert_that

import unittest
from datetime import datetime

import fudge

from zope import component

from nti.contenttypes.courses.courses import CourseInstance

from nti.dataserver.users.users import User

from nti.learning_network.data.access import _AnalyticsAccessStatsSource

from nti.learning_network.data.tests import MockTimeRecord

from nti.learning_network.interfaces import IAccessStatsSource

from nti.learning_network.tests import LearningNetworkTestCase


class TestAccess(unittest.TestCase):

    def setUp(self):
        self.user = None

    @property
    def stat_source(self):
        return _AnalyticsAccessStatsSource(self.user)

    @fudge.patch('nti.learning_network.data.access.get_user_sessions')
    def test_platform_stats(self, mock_get_sessions):
        # Empty
        mock_get_sessions.is_callable().returns(None)
        platform_stats = self.stat_source.PlatformStats
        assert_that(platform_stats.average, is_(0))
        assert_that(platform_stats.count, is_(0))

        mock_get_sessions.is_callable().returns([])
        platform_stats = self.stat_source.PlatformStats
        assert_that(platform_stats.average, is_(0))
        assert_that(platform_stats.count, is_(0))

        # Without end time
        records = [MockTimeRecord(10, None), MockTimeRecord(10, None)]
        mock_get_sessions.is_callable().returns(records)
        platform_stats = self.stat_source.PlatformStats
        assert_that(platform_stats.average, is_(0))
        assert_that(platform_stats.count, is_(0))

        # Single valid
        records = [MockTimeRecord(10, 1), MockTimeRecord(10, 0)]
        mock_get_sessions.is_callable().returns(records)
        platform_stats = self.stat_source.PlatformStats
        assert_that(platform_stats, not_none())
        assert_that(platform_stats.average, is_(10))
        assert_that(platform_stats.count, is_(1))
        assert_that(platform_stats.std_dev, is_(0))
        assert_that(platform_stats.aggregate_time, is_(10))

        # Multiple valid
        records = [MockTimeRecord(10, 1),
                   MockTimeRecord(10, None),
                   MockTimeRecord(20, 1),
                   MockTimeRecord(30, 1),
                   MockTimeRecord(40, 1)]
        mock_get_sessions.is_callable().returns(records)
        platform_stats = self.stat_source.PlatformStats
        assert_that(platform_stats, not_none())
        assert_that(platform_stats.average, is_(25))
        assert_that(platform_stats.count, is_(4))
        assert_that(platform_stats.aggregate_time, is_(100))


class TestAdapters(LearningNetworkTestCase):

    def test_adapting(self):
        course = CourseInstance()
        user = User(username='blehxxxxxxxx')
        now = datetime.utcnow()

        stats_source = component.queryMultiAdapter((user, course, now),
												   IAccessStatsSource)
        assert_that(stats_source, not_none())

        stats_source = component.queryMultiAdapter((user, course), 
												   IAccessStatsSource)
        assert_that(stats_source, not_none())

        stats_source = IAccessStatsSource(user)
        assert_that(stats_source, not_none())
