#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id: interfaces.py 84218 2016-03-08 19:12:37Z josh.zuech $
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import DateTime
from nti.schema.field import ValidTextLine

from nti.analytics.stats.interfaces import IStats
from nti.analytics.stats.interfaces import INoteStats
from nti.analytics.stats.interfaces import ITimeStats
from nti.analytics.stats.interfaces import ICommentStats
from nti.analytics.stats.interfaces import IAssignmentStats
from nti.analytics.stats.interfaces import IThoughtCommentStats
from nti.analytics.stats.interfaces import ISelfAssessmentStats


class ISocialStats(IStats):
	"""
	A container for holding various social statistics.
	"""
	ContactsAddedCount = Number(title="Number of contacts user has added.", required=True)
	DistinctReplyToCount = Number(title="Number of distinct users replying to user.", required=True)
	DistinctUserReplyToOthersCount = Number(title="Number of distinct users replied to.", required=True)


class IGroupStats(IStats):
	"""
	A container for holding various group statistics.
	"""
	GroupsJoinedCount = Number(title="Number of groups user has joined.", required=True)
	GroupsCreatedCount = Number(title="Number of groups user has created.", required=True)
	UsersInGroupsCount = Number(title="Number of users in groups.", required=True)
	DistinctUsersInGroupsCount = Number(title="Number of distinct users in groups.", required=True)


class IAssignmentOutcomeStats(IAssignmentStats):
	"""
	A container for holding assignment outcome stats.
	"""
	FinalGradeAlpha = ValidTextLine(title="The final grade", required=False)
	FinalGradeNumeric = Number(title="The final grade.", required=False)
	AverageGrade = Number(title="The average grade on assignments.", required=False)
	TotalPoints = Number( title="Number of points in assignments", required=False)
	MaxPointCount = Number( title="Maximum points of assignments.", required=False )
	MaxAssignmentCount = Number( title="Maximum number of assignments.", required=False )


class IBadgeOutcomeStats(IStats):
	"""
	A container for holding badge outcome stats.
	"""
	HasBadge = Bool(title="Does the user have a badge.", required=False)


class ILearningNetworkScoreProvider(interface.Interface):
	"""
	For a given context, typically a user, able to answer
	various learning network related questions.
	"""

	def get_score(course=None, timestamp=None):
		"""
		Return the learning network score for context, optionally
		with a course or timestamp filter.
		"""


class IAccessScoreProvider(ILearningNetworkScoreProvider):
	"""
	Provides learning network scores for access.
	"""


class IResourceAccessStatsSource(interface.Interface):
	"""
	A source of learning network access stats, broken down by resource.
	"""

	def get_all_resource_names(self):
		"""
		Get all resource names that possibly have stats.
		"""

	def get_resource_stats(self):
		"""
		Return a map of resource identifier to :class:`IStats` object.
		"""


class IAccessStatsSource(interface.Interface):
	"""
	A source of learning network access stats.
	"""
	PlatformStats = Object(ITimeStats,
							title="The platform timing view stats for the context.")
	ForumStats = Object(ITimeStats,
						title="The forum timing view stats for the context.")
	VideoStats = Object(ITimeStats,
						title="The video timing view stats for the context.")
	ReadingStats = Object(ITimeStats,
						title="The reading timing view stats for the context.")
	AssignmentStats = Object(ITimeStats,
							title="The assignment timing view stats for the context.")
	SelfAssessmentStats = Object(ITimeStats,
								title="The self-assessment timing view stats for the context.")


class IProductionStatsSource(interface.Interface):
	"""
	A source of learning network production stats.
	"""

	AssignmentStats = Object(IAssignmentStats,
							 title="Stats on contextual assignment production.")
	SelfAssessmentStats = Object(ISelfAssessmentStats,
								 title="Stats on contextual self-assessment production.")
	CommentStats = Object(ICommentStats,
						title="Stats on contextual comment production.")
	ThoughtStats = Object(IStats,
						title="Stats on contextual thought production.")
	ThoughtCommentStats = Object(IThoughtCommentStats,
						title="Stats on contextual thought comment production.")
	NoteStats = Object(INoteStats,
						title="Stats on contextual note production.")
	HighlightStats = Object(IStats,
							title="Stats on contextual highlight production.")
	BookmarkStats = Object(IStats,
						   title="Stats on contextual bookmark production.")


class IInteractionStatsSource(interface.Interface):
	"""
	A source of learning network interaction stats.
	"""

	SocialStats = Object(ISocialStats,
							title="Stats on contextual interaction with others.")

	GroupStats = Object( IGroupStats,
							title="Stats on contextual group interaction with others." )


class IOutcomeStatsSource(interface.Interface):
	"""
	A source of learning network outcome stats. These stats are generally `result`
	stats, that may possibly be predicted using other stats.
	"""

	AssignmentStats = Object(IAssignmentOutcomeStats,
							 title="Stats on contextual assignment production.")

	BadgeStats = Object( IBadgeOutcomeStats, title="Badge stats" )


class IConnectionsSource( IStats ):
	"""
	Defines user-to-user connections.
	"""
	def get_connections(self, timestamp=None):
		"""
		Returns the connections for the context for a given timestamp.
		"""

class IConnection( interface.Interface ):
	"""
	Defines a connection between users.
	"""
	Source = ValidTextLine( title="The user who intiated the connection.", required=True )
	Target = ValidTextLine( title="The (possibly passive) recipient of the connection.", required=True )
	Timestamp = DateTime( title=u"The timestamp when this connection was created.", required=False )
