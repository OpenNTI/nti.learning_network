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
from nti.learning_network.model import TimeStats

def _get_std_dev( values, summation=None ):
	result = None

	if values:
		count = len( values )
		summation = summation if summation else sum( values )
		sum_of_squares = sum( [x ** 2 for x in values if x is not None] )
		variance = sum_of_squares / count - ( summation / count ) ** 2
		result = sqrt( variance )
	return result

def get_count_stats( records ):
	"""
	For a sequence of records, return Stats.
	"""
	stats = None

	if records is not None:
		count = len( records )
		stats = Stats( Count=count )
	return stats

def get_time_stats( time_lengths ):
	"""
	For a sequence of time lengths, return the TimeStats.
	"""
	stats = None

	if time_lengths:
		total_time = sum( time_lengths )
		count = len( time_lengths )
		average = total_time / count
		std_dev = _get_std_dev( time_lengths, total_time )
		stats = TimeStats( 	AggregateTime=total_time,
							StandardDeviation=std_dev,
							Average=average,
							Count=count )
	return stats
