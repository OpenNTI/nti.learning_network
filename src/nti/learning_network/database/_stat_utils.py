#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

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
	if record.count is not None:
		record.count += 1
	else:
		record.count = 1

	if record.total_duration is not None:
		record.total_duration += duration
	else:
		record.total_duration = duration

	duration_squared = duration ** 2

	if record.sum_of_squares is not None:
		record.sum_of_squares += duration_squared
	else:
		record.sum_of_squares = duration_squared

