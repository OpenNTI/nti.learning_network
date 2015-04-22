#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.common.property import alias

from nti.schema.field import SchemaConfigured
from nti.schema.schema import EqHash

from nti.learning_network.interfaces import IStats
from nti.learning_network.interfaces import IAggregateAssessmentStats

@EqHash( 'average', 'std_dev' )
@interface.implementer(IStats)
class Stats( SchemaConfigured ):

	std_dev = alias( 'StandardDeviation' )
	average = alias( 'Average' )

	__external_class_name__ = "Stats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.stats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@EqHash( 'assessment_count', 'assignment_count', 'assessment_unique_count',
		'assignment_unique_count', 'assignment_late_count',
		'assignment_timed_count', 'assignment_timed_late_count' )
@interface.implementer(IAggregateAssessmentStats)
class AggregateAssessmentStats( SchemaConfigured ):

	assessment_count = alias( 'SelfAssessmentCount' )
	assignment_count = alias( 'AssignmentCount' )
	assessment_unique_count = alias( 'UniqueSelfAssessmentCount' )
	assignment_unique_count = alias( 'UniqueAssignmentCount' )
	assignment_late_count = alias( 'AssignmentLateCount' )
	assignment_timed_count = alias( 'TimedAssignmentCount' )
	assignment_timed_late_count = alias( 'TimedAssignmentLateCount' )

	__external_class_name__ = "AggregateAssessmentStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.aggregateassessmentstats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)
