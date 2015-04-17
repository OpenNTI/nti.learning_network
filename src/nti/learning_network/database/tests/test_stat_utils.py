#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import numpy

from unittest import TestCase

from hamcrest import is_
from hamcrest import assert_that

from ..meta_mixins import StatMixin

from .._stat_utils import _get_new_variance
from .._stat_utils import update_record_stats

class StatRecord( StatMixin ):

	def __init__(self):
		self.count = None
		self.total_duration = None
		self.sum_of_squares = None

class TestStatUtils( TestCase ):

	def test_incremental_variance( self ):
		"""
		Test that our incremental variance is accurate.
		"""
		values = [ 0, 1, 5, 10, 20, 30, 40, 50, 1000 ]
		old_count = old_total = old_squared_sum = 0

		current_vals = []

		for value in values:
			current_vals.append( value )
			expected_var = numpy.var( current_vals )

			new_count = old_count + 1
			new_variance = _get_new_variance( new_count, old_total,
											value, old_squared_sum )

			# Numpy uses decimals, we use floating pt for speed
			is_close = numpy.isclose( new_variance, expected_var )
			assert_that( is_close )

			# Update for next iter
			old_count = new_count
			old_total += value
			old_squared_sum += value ** 2

	def test_stat_update( self ):
		record = StatRecord()

		update_record_stats( record, 3 )
		assert_that( record.count, is_( 1 ))
		assert_that( record.total_duration, is_( 3 ))
		assert_that( record.sum_of_squares, is_( 9 ))

		update_record_stats( record, 9 )
		assert_that( record.count, is_( 2 ))
		assert_that( record.total_duration, is_( 12 ))
		assert_that( record.sum_of_squares, is_( 90 ))

