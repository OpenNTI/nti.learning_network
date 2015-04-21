#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

try:
	import numpy as _numpy
except ImportError:
	_numpy = None

from unittest import TestCase

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

from ..meta_mixins import StatMixin

from .._stat_utils import get_stats
from .._stat_utils import _get_new_variance
from .._stat_utils import update_record_stats

class StatRecord( StatMixin ):

	def __init__( self, count=None, total_duration=None, sum_of_squares=None ):
		self.count = count
		self.total_duration = total_duration
		self.sum_of_squares = sum_of_squares

class TestStatUtils( TestCase ):

	def test_incremental_variance( self ):
		"""
		Test that our incremental variance is accurate.
		"""
		if _numpy is None:
			return

		values = [ 0, 1, 5, 10, 20, 30, 40, 50, 1000 ]
		old_count = old_total = old_squared_sum = 0

		current_vals = []

		for value in values:
			current_vals.append( value )
			expected_var = _numpy.var( current_vals )

			new_count = old_count + 1
			new_variance = _get_new_variance( new_count, old_total,
											value, old_squared_sum )

			# Numpy uses decimals, we use floating pt for speed
			is_close = _numpy.isclose( new_variance, expected_var )
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

	def test_get_stats( self ):
		# Empty/none
		result = get_stats( [] )
		assert_that( result, none() )

		record = StatRecord( 0, 10, 100 )
		result = get_stats( (record,) )
		assert_that( result, none() )

		# Single value
		record = StatRecord( 1, 10, 100 )
		result = get_stats( (record,) )
		assert_that( result.average, is_( 10 ))
		assert_that( result.std_dev, is_( 0 ))

		# Single record with values
		values = [ 0, 1, 5, 10, 20, 30, 40, 50, 1000 ]
		record = StatRecord( len( values ), sum( values ), sum( x ** 2 for x in values ) )
		result = get_stats( (record,) )
		average = sum( values ) / len( values )
		assert_that( result.average, is_( average ))

		if _numpy:
			expected_std_dev = _numpy.std( values )
			is_close = _numpy.isclose( result.std_dev, expected_std_dev )
			assert_that( is_close )

		# Multiple records
		values1 = [ 0, 1, 5 ]
		values2 = [ 10 ]
		values3 = [ 20, 30, 40, 50, 1000 ]
		records = []
		for value in ( values1, values2, values3 ):
			record = StatRecord( len( value ), sum( value ), sum( x ** 2 for x in value ) )
			records.append( record )

		result = get_stats( records )
		assert_that( result.average, is_( average ))

		if _numpy:
			is_close = _numpy.isclose( result.std_dev, expected_std_dev )
			assert_that( is_close )

