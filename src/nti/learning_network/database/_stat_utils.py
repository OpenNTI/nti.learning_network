#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from math import sqrt

from nti.learning_network.model import Stats

from ._utils import increment_field

def _get_new_variance( new_count, old_total, delta, old_sum_of_squares ):
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

def update_record_stats( record, duration ):
	"""
	For a stat database record, update the stat columns appropriately.
	"""
	increment_field( record, 'count' )
	increment_field( record, 'total_duration', delta=duration )

	duration_squared = duration ** 2
	increment_field( record, 'sum_of_squares', delta=duration_squared )

def get_aggregate_stats( statmixin_iter ):
	"""
	For an iterable of ``StatMixin`` rows, return some aggregate statistics.
	"""
	summation = 0
	count = 0
	sum_of_squares = 0
	stats = None

	for row in statmixin_iter:
		summation += row.total_duration
		count += row.count
		sum_of_squares += row.sum_of_squares

	if count:
		variance = sum_of_squares / count - ( summation / count ) ** 2
		average = summation / count
		std_dev = sqrt( variance )
		stats = Stats( Average=average, StandardDeviation=std_dev )
	return stats

