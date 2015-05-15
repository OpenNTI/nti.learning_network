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
from nti.learning_network.interfaces import ITimeStats
from nti.learning_network.interfaces import IAdvancedStats
from nti.learning_network.interfaces import IAssignmentStats
from nti.learning_network.interfaces import ISelfAssessmentStats

@EqHash( 'count' )
@interface.implementer(IStats)
class Stats( SchemaConfigured ):

	count = alias( 'Count' )
	__external_class_name__ = "Stats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.stats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@EqHash( 'average', 'std_dev', 'count' )
@interface.implementer(IAdvancedStats)
class AdvancedStats( Stats ):
	std_dev = alias( 'StandardDeviation' )
	average = alias( 'Average' )
	__external_class_name__ = "AdvancedStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.advancedstats'

@EqHash( 'aggregate_time', 'average', 'std_dev', 'count' )
@interface.implementer(ITimeStats)
class TimeStats( AdvancedStats ):
	aggregate_time = alias( 'AggregateTime' )
	__external_class_name__ = "TimeStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.timestats'

@EqHash( 'Count', 'UniqueCount' )
@interface.implementer(ISelfAssessmentStats)
class SelfAssessmentStats( Stats ):
	__external_class_name__ = "SelfAssessmentStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.selfassessmentstats'

@EqHash( 'Count', 'UniqueCount', 'AssignmentLateCount',
		'TimedAssignmentCount', 'TimedAssignmentLateCount' )
@interface.implementer(IAssignmentStats)
class AssignmentStats( Stats ):
	__external_class_name__ = "AssignmentStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.assignmentstats'
