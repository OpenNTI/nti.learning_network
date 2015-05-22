#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
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

from nti.analytics.social import get_contacts_added

from nti.common.property import readproperty

from nti.learning_network.interfaces import IInteractionStatsSource

from ..model import SocialStats

@interface.implementer( IInteractionStatsSource )
class _AnalyticsInteractionStatsSource( object ):
	"""
	An interaction stats source that pulls data from analytics.
	"""
	__external_class_name__ = "InteractionStatsSource"
	mime_type = mimeType = 'application/vnd.nextthought.learningnetwork.interactionstatssource'

	def __init__(self, user, course=None, timestamp=None):
		self.user = user
		self.course = course
		self.timestamp = timestamp

	def _get_contacts_added_count(self):
		contacts_added = get_contacts_added( self.user, self.timestamp )
		return len( contacts_added )

	def _get_distinct_reply_to_count(self):
		blog_replies = get_blog_replies( self.user, self.timestamp )
		note_replies = get_note_replies( self.user, self.course, self.timestamp )
		forum_replies = get_forum_replies( self.user, self.course, self.timestamp )
		usernames = set( (	x.user.username
							for x in chain( blog_replies, note_replies, forum_replies )) )
		return len( usernames )

	def _get_distinct_user_reply_to_others_count(self):
		blog_replies = get_blog_user_replies_to_others( self.user, self.timestamp )
		note_replies = get_note_user_replies_to_others( self.user, self.course, self.timestamp )
		forum_replies = get_forum_user_replies_to_others( self.user, self.course, self.timestamp )

		def get_user( obj, obj_field ):
			obj = getattr( obj, obj_field )
			in_reply = obj.inReplyTo
			# This could be an assertion...
			if in_reply and in_reply.creator:
				return in_reply.creator.username
			return None

		# Build our set up
		username_set = set()
		for replies, obj_field in ( (blog_replies, 'Comment'),
									(note_replies, 'Note'),
									(forum_replies, 'Comment' ) ):
			username_set.update( (get_user(x, obj_field) for x in replies) )
		username_set.discard( None )
		return len( username_set )

	@readproperty
	def SocialStats( self ):
		"""
		Return the learning network social stats.
		"""
		contact_count = self._get_contacts_added_count()
		reply_to_count = self._get_distinct_reply_to_count()
		user_reply_count = self._get_distinct_user_reply_to_others_count()

		# FIXME Determine what 'groups' counts are needed.
		group_count = group_created_count = 0
		social_stats = SocialStats( ContactsAddedCount=contact_count,
									GroupsJoinedCount=group_count,
									GroupsCreatedCount=group_created_count,
									DistinctReplyToCount=reply_to_count,
									DistinctUserReplyToOthersCount=user_reply_count )

		return social_stats

