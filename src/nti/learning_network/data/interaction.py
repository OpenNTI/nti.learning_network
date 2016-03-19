#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from itertools import chain

from zope import interface

from nti.analytics.blogs import get_replies_to_user as get_blog_replies
from nti.analytics.blogs import get_user_replies_to_others as get_blog_user_replies_to_others

from nti.analytics.boards import get_replies_to_user as get_forum_replies
from nti.analytics.boards import get_user_replies_to_others as get_forum_user_replies_to_others

from nti.analytics.resource_tags import get_replies_to_user as get_note_replies
from nti.analytics.resource_tags import get_user_replies_to_others as get_note_user_replies_to_others

from nti.analytics.social import get_groups_joined
from nti.analytics.social import get_groups_created
from nti.analytics.social import get_contacts_added

from nti.common.property import readproperty

from nti.learning_network.interfaces import IInteractionStatsSource

from nti.learning_network.model import GroupStats
from nti.learning_network.model import SocialStats

@interface.implementer(IInteractionStatsSource)
class _AnalyticsInteractionStatsSource(object):
	"""
	An interaction stats source that pulls data from analytics.
	"""

	__external_class_name__ = "InteractionStatsSource"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.interactionstatssource'

	def __init__(self, user, course=None, timestamp=None, max_timestamp=None):
		self.user = user
		self.course = course
		self.timestamp = timestamp
		self.max_timestamp = max_timestamp

	def _get_contacts_added_count(self):
		contacts_added = get_contacts_added(self.user,
											timestamp=self.timestamp,
											max_timestamp=self.max_timestamp)
		return len(contacts_added)

	def _get_distinct_reply_to_count(self):
		blog_replies = get_blog_replies(self.user,
										timestamp=self.timestamp,
										max_timestamp=self.max_timestamp)
		note_replies = get_note_replies(self.user, self.course,
										timestamp=self.timestamp,
										max_timestamp=self.max_timestamp)
		forum_replies = get_forum_replies(self.user, self.course,
										timestamp=self.timestamp,
										max_timestamp=self.max_timestamp)
		usernames = set((x.user.username
							for x in chain(blog_replies, note_replies, forum_replies)))
		return len(usernames)

	def _get_distinct_user_reply_to_others_count(self):
		blog_replies = get_blog_user_replies_to_others(self.user,
													   timestamp=self.timestamp,
													   max_timestamp=self.max_timestamp)
		note_replies = get_note_user_replies_to_others(self.user,
													   self.course,
													   timestamp=self.timestamp,
													   max_timestamp=self.max_timestamp)
		forum_replies = get_forum_user_replies_to_others(self.user,
														 self.course,
														 timestamp=self.timestamp,
														 max_timestamp=self.max_timestamp)

		# Build our set up
		username_set = set()
		for obj in chain( blog_replies, note_replies, forum_replies ):
			if obj.RepliedToUser:
				username_set.add( obj.RepliedToUser.username )
		username_set.discard( None )
		return len( username_set )

	@readproperty
	def SocialStats(self):
		"""
		Return the learning network social stats.
		"""
		contact_count = self._get_contacts_added_count()
		reply_to_count = self._get_distinct_reply_to_count()
		user_reply_count = self._get_distinct_user_reply_to_others_count()

		social_stats = SocialStats(ContactsAddedCount=contact_count,
								   DistinctReplyToCount=reply_to_count,
								   DistinctUserReplyToOthersCount=user_reply_count)

		return social_stats

	@readproperty
	def GroupStats(self):
		"""
		Return the learning network group stats.
		"""
		groups_created = get_groups_created(self.user,
											timestamp=self.timestamp,
											max_timestamp=self.max_timestamp)
		groups_joined = get_groups_joined(self.user,
										  timestamp=self.timestamp,
										  max_timestamp=self.max_timestamp)
		created_count = len(groups_created)
		joined_count = len(groups_joined)

		user_count = 0
		usernames = set()
		for group in chain(groups_created, groups_joined):
			# TODO: Group may be None now; should retrieve from analytics.
			group_users = {x.username for x in group.Group or () if x is not None}
			usernames.update(group_users)
			user_count += len(group_users)

		distinct_user_count = len(usernames)

		group_stats = GroupStats(GroupsJoinedCount=joined_count,
								 GroupsCreatedCount=created_count,
								 UsersInGroupsCount=user_count,
								 DistinctUsersInGroupsCount=distinct_user_count)

		return group_stats
