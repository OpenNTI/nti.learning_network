#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.analytics.recorded.interfaces import IAnalyticsAssessmentRecordedEvent

from .database.assessments import update_assessment
from .database.assessments import get_aggregate_assessment_stats

get_aggregate_assessment_stats = get_aggregate_assessment_stats

@component.adapter( IAnalyticsAssessmentRecordedEvent )
def _analytics_assessment( event ):
	course = event.course
	assessment = event.assessment
	update_assessment( event.user, event.timestamp, assessment, course )
