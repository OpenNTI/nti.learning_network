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

from ..production import _AnalyticsProductionStatsSource

class TestProduction( unittest.TestCase ):

	def setUp(self):
		self.user = None
		self.stat_source = _AnalyticsProductionStatsSource( self.user )

	def test_assessment_stats(self):
		pass


