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
from nti.learning_network.interfaces import INoteStats
from nti.learning_network.interfaces import ITimeStats
from nti.learning_network.interfaces import IGroupStats
from nti.learning_network.interfaces import ISocialStats
from nti.learning_network.interfaces import ICommentStats
from nti.learning_network.interfaces import IAssignmentStats
from nti.learning_network.interfaces import IThoughtCommentStats
from nti.learning_network.interfaces import ISelfAssessmentStats

@EqHash( 'count' )
@interface.implementer(IStats)
class Stats( SchemaConfigured ):

	count = alias( 'Count' )
	__external_class_name__ = "Stats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.stats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@EqHash( 'aggregate_time', 'average', 'std_dev', 'count' )
@interface.implementer(ITimeStats)
class TimeStats( Stats ):
	aggregate_time = alias( 'AggregateTime' )
	std_dev = alias( 'StandardDeviationDuration' )
	average = alias( 'AverageDuration' )
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

@EqHash( 'Count', 'TopLevelCount', 'ReplyCount',
		'DistinctPostsLiked', 'DistinctPostsFavorited',
		'TotalLikes', 'TotalFavorites', 'RecursiveChildrenCount',
		'StandardDeviationLength', 'AverageLength', 'ContainsWhiteboardCount' )
class PostStats( Stats ):
	pass

@interface.implementer(INoteStats)
class NoteStats( PostStats ):
	__external_class_name__ = "NoteStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.notestats'

@interface.implementer(ICommentStats)
class CommentStats( PostStats ):
	__external_class_name__ = "CommentStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.commentstats'

@interface.implementer(IThoughtCommentStats)
class ThoughtCommentStats( PostStats ):
	__external_class_name__ = "ThoughtCommentStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.thoughtcommentstats'

@EqHash( 'ContactsAddedCount', 'DistinctReplyToCount', 'DistinctUserReplyToOthersCount' )
@interface.implementer(ISocialStats)
class SocialStats( SchemaConfigured ):

	__external_class_name__ = "SocialStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.socialstats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@EqHash( 'GroupsJoinedCount', 'GroupsCreatedCount',
		'UsersInGroups', 'DistinctUsersInGroups' )
@interface.implementer(IGroupStats)
class GroupStats( SchemaConfigured ):

	__external_class_name__ = "GroupStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.groupstats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)
