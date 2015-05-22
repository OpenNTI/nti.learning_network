#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import fudge

from hamcrest import is_
from hamcrest import not_none
from hamcrest import assert_that

from datetime import datetime

from zope import component

from nti.analytics.read_models import AnalyticsNote

from nti.dataserver.contenttypes.note import Note
from nti.contenttypes.courses.courses import CourseInstance

from nti.dataserver.users.users import User

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.learning_network.interfaces import IInteractionStatsSource

from ..interaction import _AnalyticsInteractionStatsSource

from nti.learning_network.tests import LearningNetworkTestCase

course = CourseInstance()

def _get_note( user, obj ):
	result = AnalyticsNote( Note=obj,
							user=user,
							timestamp=datetime.utcnow(),
							RootContext=course,
							NoteLength=3,
							Sharing='UNKNOWN',
							Flagged=False,
							LikeCount=2,
							FavoriteCount=3,
							IsReply=False )
	return result

class TestInteraction( LearningNetworkTestCase ):

	def setUp(self):
		self.user = None
		self.stat_source = _AnalyticsInteractionStatsSource( self.user )

	def _get_note_obj(self, user, reply_to=None):
		note = Note()
		note._ds_intid = 123456
		note.body = ('test222',)
		note.creator = user
		note.containerId = 'tag:nti:foo'
		note.inReplyTo = reply_to
		user.addContainedObject( note )
		return note

	@WithMockDSTrans
	@fudge.patch( 	'nti.learning_network.data.interaction.get_contacts_added',
					'nti.learning_network.data.interaction.get_blog_replies',
					'nti.learning_network.data.interaction.get_forum_replies',
					'nti.learning_network.data.interaction.get_note_replies',
					'nti.learning_network.data.interaction.get_blog_user_replies_to_others',
					'nti.learning_network.data.interaction.get_forum_user_replies_to_others',
					'nti.learning_network.data.interaction.get_note_user_replies_to_others' )
	def test_stats( self, mock_get_contacts, mock_blog, mock_forum, mock_note,
					mock_blog_user_replies, mock_forum_user_replies, mock_note_user_replies  ):
		"""
		Test contracts, reply tos, and user replies to others. Notes/Blogs/Comments are
		synonymous when it concerns replies.
		"""
		# Empty
		mock_get_contacts.is_callable().returns( () )
		mock_blog.is_callable().returns( () )
		mock_forum.is_callable().returns( () )
		mock_note.is_callable().returns( () )
		mock_blog_user_replies.is_callable().returns( () )
		mock_forum_user_replies.is_callable().returns( () )
		mock_note_user_replies.is_callable().returns( () )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 0 ) )
		assert_that( stats.DistinctReplyToCount, is_( 0 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 0 ) )

		# Contact
		mock_get_contacts.is_callable().returns( (object(),) )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 1 ) )
		assert_that( stats.DistinctReplyToCount, is_( 0 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 0 ) )

		# Multiple contacts, single reply-to note
		user = User.create_user( username='new_user1' )
		note_obj1 = self._get_note_obj( user )
		note = _get_note( user, note_obj1 )
		mock_note.is_callable().returns( (note,) )
		mock_get_contacts.is_callable().returns( (object(), object(), object()) )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 3 ) )
		assert_that( stats.DistinctReplyToCount, is_( 1 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 0 ) )

		# Multiple reply-to notes
		user2 = User.create_user( username='new_user2' )
		note_obj2 = self._get_note_obj( user2, reply_to=note_obj1 )
		note2 = _get_note( user2, note_obj2 )
		mock_note.is_callable().returns( (note, note2) )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 3 ) )
		assert_that( stats.DistinctReplyToCount, is_( 2 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 0 ) )

		# Dupe reply-to
		mock_note.is_callable().returns( (note, note2, note, note2) )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 3 ) )
		assert_that( stats.DistinctReplyToCount, is_( 2 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 0 ) )

		# User reply
		mock_note_user_replies.is_callable().returns( (note2,) )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 3 ) )
		assert_that( stats.DistinctReplyToCount, is_( 2 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 1 ) )

		# User reply - multiple (with one empty)
		user3 = User.create_user( username='new_user3' )
		note_obj3 = self._get_note_obj( user3, reply_to=note_obj2 )
		note3 = _get_note( user3, note_obj3 )
		mock_note_user_replies.is_callable().returns( ( note, note2, note, note3, note3 ) )
		stats = self.stat_source.SocialStats
		assert_that( stats, not_none() )
		assert_that( stats.ContactsAddedCount, is_( 3 ) )
		assert_that( stats.DistinctReplyToCount, is_( 2 ) )
		assert_that( stats.DistinctUserReplyToOthersCount, is_( 2 ) )

class TestAdapters( LearningNetworkTestCase ):

	def test_adapting(self):
		user = User( username='blehxxxxxxxx' )
		now = datetime.utcnow()

		stats_source = component.queryMultiAdapter( ( user, course, now ), IInteractionStatsSource )
		assert_that( stats_source, not_none() )

		stats_source = component.queryMultiAdapter( ( user, course ), IInteractionStatsSource )
		assert_that( stats_source, not_none() )

		stats_source = IInteractionStatsSource( user )
		assert_that( stats_source, not_none() )
