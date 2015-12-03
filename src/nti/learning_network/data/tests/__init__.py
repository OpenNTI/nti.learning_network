#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

class MockTimeRecord( object ):

	def __init__(self, time_length=0, end_time=0):
		self.time_length = time_length
		self.Duration = time_length
		self.SessionEndTime = end_time

class _MockAnalyticsRecord( object ):

	def __init__(self, **kwargs):
		for k,v in kwargs.items():
			setattr( self, k, v )
