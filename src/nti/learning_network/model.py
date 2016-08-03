#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.learning_network.interfaces import IConnection
from nti.learning_network.interfaces import IGroupStats
from nti.learning_network.interfaces import ISocialStats
from nti.learning_network.interfaces import IBadgeOutcomeStats
from nti.learning_network.interfaces import IAssignmentOutcomeStats

from nti.schema.eqhash import EqHash

from nti.schema.field import SchemaConfigured

@interface.implementer(IAssignmentOutcomeStats)
class AssignmentOutcomeStats(SchemaConfigured):
	__external_class_name__ = "AssignmentOutcomeStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.assignmentoutcomestats'

@interface.implementer(IBadgeOutcomeStats)
class BadgeOutcomeStats(SchemaConfigured):
	__external_class_name__ = "BadgeOutcomeStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.badgeoutcomestats'

@EqHash('ContactsAddedCount', 'DistinctReplyToCount', 'DistinctUserReplyToOthersCount')
@interface.implementer(ISocialStats)
class SocialStats(SchemaConfigured):

	__external_class_name__ = "SocialStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.socialstats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@EqHash('GroupsJoinedCount', 'GroupsCreatedCount',
		'UsersInGroups', 'DistinctUsersInGroups')
@interface.implementer(IGroupStats)
class GroupStats(SchemaConfigured):

	__external_class_name__ = "GroupStats"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.groupstats'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)

@EqHash('Source', 'Target')
@interface.implementer(IConnection)
class Connection(SchemaConfigured):

	__external_class_name__ = "Connection"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.connection'

	def __init__(self, *args, **kwargs):
		SchemaConfigured.__init__(self, *args, **kwargs)
