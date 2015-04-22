#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.schema.field import Number
from nti.schema.field import Float

class IStats( interface.Interface ):
	"""
	A container for holding various stats.
	"""

	StandardDeviation = Float( title="Standard deviation", required=True )
	Average = Float( title="Average", required=True )

class IAggregateAssessmentStats( interface.Interface ):
	"""
	A container for holding assessment aggregate stats.
	"""

	SelfAssessmentCount = Number( title="Self assessment count", required=True )
	UniqueSelfAssessmentCount = Number( title="Unique self assessment count", required=True )

	AssignmentCount = Number( title="Assignment count", required=True )
	UniqueAssignmentCount = Number( title="Unique assignment count", required=True )
	AssignmentLateCount = Number( title="Unique self assessment count", required=True )
	TimedAssignmentCount = Number( title="Unique assignment count", required=True )
	TimedAssignmentLateCount = Number( title="Late assignment timed count", required=True )
