#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from nti.analytics.stats.interfaces import IStats
from nti.analytics.stats.interfaces import INoteStats
from nti.analytics.stats.interfaces import ITimeStats
from nti.analytics.stats.interfaces import ICommentStats
from nti.analytics.stats.interfaces import IAssignmentStats
from nti.analytics.stats.interfaces import IThoughtCommentStats
from nti.analytics.stats.interfaces import ISelfAssessmentStats

from nti.schema.field import Bool
from nti.schema.field import Number
from nti.schema.field import Object
from nti.schema.field import DateTime
from nti.schema.field import ValidTextLine


class ISocialStats(IStats):
    """
    A container for holding various social statistics.
    """
    ContactsAddedCount = Number(title=u"Number of contacts user has added.", 
								required=True)

    DistinctReplyToCount = Number(title=u"Number of distinct users replying to user.", 
								  required=True)

    DistinctUserReplyToOthersCount = Number(title=u"Number of distinct users replied to.", 
											required=True)


class IGroupStats(IStats):
    """
    A container for holding various group statistics.
    """
    GroupsJoinedCount = Number(title=u"Number of groups user has joined.", 
							   required=True)

    GroupsCreatedCount = Number(title=u"Number of groups user has created.", 
								required=True)

    UsersInGroupsCount = Number(title=u"Number of users in groups.", 
								required=True)

    DistinctUsersInGroupsCount = Number(title=u"Number of distinct users in groups.", 
										required=True)


class IAssignmentOutcomeStats(IAssignmentStats):
    """
    A container for holding assignment outcome stats.
    """
    FinalGradeAlpha = ValidTextLine(title=u"The final grade", required=False)

    FinalGradeNumeric = Number(title=u"The final grade.", required=False)

    AverageGrade = Number(title=u"The average grade on assignments.", 
						  required=False)

    TotalPoints = Number(title=u"Number of points in assignments", 
						 required=False)

    MaxPointCount = Number(title=u"Maximum points of assignments.", 
						   required=False)

    MaxAssignmentCount = Number(title=u"Maximum number of assignments.", 
								required=False)


class IBadgeOutcomeStats(IStats):
    """
    A container for holding badge outcome stats.
    """
    HasBadge = Bool(title=u"Does the user have a badge.", required=False)


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
                           title=u"The platform timing view stats for the context.")

    ForumStats = Object(ITimeStats,
                        title=u"The forum timing view stats for the context.")

    VideoStats = Object(ITimeStats,
                        title=u"The video timing view stats for the context.")

    ReadingStats = Object(ITimeStats,
                          title=u"The reading timing view stats for the context.")

    AssignmentStats = Object(ITimeStats,
                             title=u"The assignment timing view stats for the context.")

    SelfAssessmentStats = Object(ITimeStats,
                                 title=u"The self-assessment timing view stats for the context.")


class IProductionStatsSource(interface.Interface):
    """
    A source of learning network production stats.
    """

    AssignmentStats = Object(IAssignmentStats,
                             title=u"Stats on contextual assignment production.")

    SelfAssessmentStats = Object(ISelfAssessmentStats,
                                 title=u"Stats on contextual self-assessment production.")

    CommentStats = Object(ICommentStats,
                          title=u"Stats on contextual comment production.")
 
    ThoughtStats = Object(IStats,
                          title=u"Stats on contextual thought production.")

    ThoughtCommentStats = Object(IThoughtCommentStats,
                                 title=u"Stats on contextual thought comment production.")
 
    NoteStats = Object(INoteStats,
                       title=u"Stats on contextual note production.")

    HighlightStats = Object(IStats,
                            title=u"Stats on contextual highlight production.")

    BookmarkStats = Object(IStats,
                           title=u"Stats on contextual bookmark production.")


class IInteractionStatsSource(interface.Interface):
    """
    A source of learning network interaction stats.
    """

    SocialStats = Object(ISocialStats,
                         title=u"Stats on contextual interaction with others.")

    GroupStats = Object(IGroupStats,
                        title=u"Stats on contextual group interaction with others.")


class IOutcomeStatsSource(interface.Interface):
    """
    A source of learning network outcome stats. These stats are generally `result`
    stats, that may possibly be predicted using other stats.
    """

    AssignmentStats = Object(IAssignmentOutcomeStats,
                             title=u"Stats on contextual assignment production.")

    BadgeStats = Object(IBadgeOutcomeStats, title=u"Badge stats")


class IConnectionsSource(IStats):
    """
    Defines user-to-user connections.
    """

    def get_connections(self, timestamp=None):
        """
        Returns the connections for the context for a given timestamp.
        """


class IConnection(interface.Interface):
    """
    Defines a connection between users.
    """
    Source = ValidTextLine(title=u"The user who intiated the connection.",
                           required=True)

    Target = ValidTextLine(title=u"The (possibly passive) recipient of the connection.",
                           required=True)

    Timestamp = DateTime(title=u"The timestamp when this connection was created.", 
						 required=False)
