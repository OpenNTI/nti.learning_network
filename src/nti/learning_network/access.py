#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import component

from nti.analytics.recorded.interfaces import VideoWatchRecordedEvent
from nti.analytics.recorded.interfaces import TopicViewedRecordedEvent
from nti.analytics.recorded.interfaces import ResourceViewedRecordedEvent
from nti.analytics.recorded.interfaces import IAnalyticsSessionRecordedEvent

from nti.ntiids.ntiids import find_object_with_ntiid

from .database.access import get_platform_stats
from .database.access import update_video_access
from .database.access import update_reading_access
from .database.access import update_platform_access
from .database.access import update_assessment_access
from .database.access import update_assignment_access
from .database.access import update_discussion_access

get_platform_stats = get_platform_stats

def _update_access( to_call, event, duration ):
	if duration > 0:
		to_call( event.user, event.timestamp, duration )

@component.adapter( IAnalyticsSessionRecordedEvent )
def _analytics_session( session ):
	duration = session.SessionEndTime - session.SessionStartTime
	duration = duration.seconds
	_update_access( update_platform_access, session, duration )

@component.adapter( VideoWatchRecordedEvent )
def _video_view( event ):
	_update_access( update_video_access, event, event.duration )

@component.adapter( TopicViewedRecordedEvent )
def _discussion_view( event ):
	_update_access( update_discussion_access, event, event.duration )

@component.adapter( ResourceViewedRecordedEvent )
def _reading_view( event ):
	# FIXME We need to know if we have assessment/assignment/reading/external
	# probably distinct events
	#from IPython.core.debugger import Tracer;Tracer()()
	_update_access( update_reading_access, event, event.duration )

# FIXME
@component.adapter( ResourceViewedRecordedEvent )
def _assessment_view( event ):
	pass
# 	from IPython.core.debugger import Tracer;Tracer()()
# 	_update_access( update_assessment_access, event, event.duration )

# FIXME
@component.adapter( ResourceViewedRecordedEvent )
def _assignment_view( event ):
	pass
# 	from IPython.core.debugger import Tracer;Tracer()()
# 	_update_access( update_assignment_access, event, event.duration )

