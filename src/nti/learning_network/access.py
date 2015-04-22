#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.analytics.recorded.interfaces import IAnalyticsSessionRecordedEvent

from .database.access import update_access_zones
from .database.access import update_platform_access
from .database.access import get_platform_stats

get_platform_stats = get_platform_stats

# def update_access_zones( user, timestamp, duration, course=None ):
# def update_platform_access( user, timestamp, duration ):

@component.adapter( IAnalyticsSessionRecordedEvent )
def _analytics_session( session ):
	duration = session.SessionEndTime - session.SessionStartTime
	duration = duration.seconds
	if duration > 0:
		update_platform_access( session.user, session.timestamp, duration )
