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

from hamcrest import assert_that

from nti.analytics.learning_network.database.common import _get_new_variance

class TestVariance( TestCase ):

	def test_incremental_variance( self ):
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
			old_variance = new_variance
			old_squared_sum += value ** 2

