#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import not_none
from hamcrest import assert_that

from datetime import datetime

import fudge

from zope import component

from zope.intid.interfaces import IIntIds

from nti.contenttypes.courses.courses import CourseInstance

from nti.dataserver.contenttypes.note import Note

from nti.dataserver.tests.mock_dataserver import WithMockDSTrans

from nti.dataserver.users.friends_lists import DynamicFriendsList

from nti.dataserver.users.users import User

from nti.learning_network.data.interaction import _AnalyticsInteractionStatsSource

from nti.learning_network.data.tests import _MockAnalyticsRecord

from nti.learning_network.interfaces import IInteractionStatsSource

from nti.learning_network.tests import LearningNetworkTestCase

course = CourseInstance()


def _get_note(user, obj, replied_to_user=None):
    result = _MockAnalyticsRecord(Note=obj,
                                  user=user,
                                  timestamp=datetime.utcnow(),
                                  RootContext=course,
                                  NoteLength=3,
                                  Sharing=u'PRIVATE',
                                  Flagged=False,
                                  LikeCount=2,
                                  FavoriteCount=3,
                                  IsReply=False,
                                  RepliedToUser=replied_to_user)
    return result


def _get_group(user, group):
    result = _MockAnalyticsRecord(user=user,
                                  timestamp=datetime.utcnow(),
                                  Group=group)
    return result


class TestInteraction(LearningNetworkTestCase):

    def setUp(self):
        self.user = None

    @property
    def stat_source(self):
        return _AnalyticsInteractionStatsSource(self.user)

    def _get_note_obj(self, user):
        note = Note()
        note._ds_intid = 123456
        note.body = (u'test222',)
        note.creator = user
        note.containerId = u'tag:nti:foo'
        user.addContainedObject(note)
        return note

    def _get_group_obj(self, user):
        fl = DynamicFriendsList(username=user.username)
        fl.creator = user
        fl._ds_intid = 123456
        intids = component.getUtility(IIntIds)
        intids.register(fl)
        return fl

    def _add_member(self, group, member):
        group.addFriend(member)

    @WithMockDSTrans
    @fudge.patch('nti.learning_network.data.interaction.get_contacts_added',
                 'nti.learning_network.data.interaction.get_blog_replies',
                 'nti.learning_network.data.interaction.get_forum_replies',
                 'nti.learning_network.data.interaction.get_note_replies',
                 'nti.learning_network.data.interaction.get_blog_user_replies_to_others',
                 'nti.learning_network.data.interaction.get_forum_user_replies_to_others',
                 'nti.learning_network.data.interaction.get_note_user_replies_to_others')
    def test_stats(self, mock_get_contacts, mock_blog, mock_forum, mock_note,
                   mock_blog_user_replies, mock_forum_user_replies, mock_note_user_replies):
        """
        Test contacts, reply tos, and user replies to others. Notes/Blogs/Comments are
        synonymous when it concerns replies.
        """
        # Empty
        mock_get_contacts.is_callable().returns(())
        mock_blog.is_callable().returns(())
        mock_forum.is_callable().returns(())
        mock_note.is_callable().returns(())
        mock_blog_user_replies.is_callable().returns(())
        mock_forum_user_replies.is_callable().returns(())
        mock_note_user_replies.is_callable().returns(())
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(0))
        assert_that(stats.DistinctReplyToCount, is_(0))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(0))

        # Contact
        mock_get_contacts.is_callable().returns((object(),))
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(1))
        assert_that(stats.DistinctReplyToCount, is_(0))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(0))

        # Multiple contacts, single reply-to note
        user = User.create_user(username=u'new_user1')
        note_obj1 = self._get_note_obj(user)
        note = _get_note(user, note_obj1)
        mock_note.is_callable().returns((note,))
        mock_get_contacts.is_callable().returns((object(), object(), object()))
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(3))
        assert_that(stats.DistinctReplyToCount, is_(1))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(0))

        # Multiple reply-to notes
        user2 = User.create_user(username=u'new_user2')
        note_obj2 = self._get_note_obj(user2)
        note2 = _get_note(user2, note_obj2, replied_to_user=user)
        mock_note.is_callable().returns((note, note2))
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(3))
        assert_that(stats.DistinctReplyToCount, is_(2))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(0))

        # Dupe reply-to
        mock_note.is_callable().returns((note, note2, note, note2))
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(3))
        assert_that(stats.DistinctReplyToCount, is_(2))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(0))

        # User reply
        mock_note_user_replies.is_callable().returns((note2,))
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(3))
        assert_that(stats.DistinctReplyToCount, is_(2))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(1))

        # User reply - multiple (with one empty)
        user3 = User.create_user(username=u'new_user3')
        note_obj3 = self._get_note_obj(user3)
        note3 = _get_note(user3, note_obj3, replied_to_user=user2)
        mock_note_user_replies.is_callable().returns((note, note2, note, note3, note3))
        stats = self.stat_source.SocialStats
        assert_that(stats, not_none())
        assert_that(stats.ContactsAddedCount, is_(3))
        assert_that(stats.DistinctReplyToCount, is_(2))
        assert_that(stats.DistinctUserReplyToOthersCount, is_(2))

    @WithMockDSTrans
    @fudge.patch('nti.learning_network.data.interaction.get_groups_created',
                 'nti.learning_network.data.interaction.get_groups_joined')
    def test_groups(self, mock_get_created, mock_get_joined):
        """
        Test groups created and joined.
        """
        # Empty
        mock_get_created.is_callable().returns(())
        mock_get_joined.is_callable().returns(())
        stats = self.stat_source.GroupStats
        assert_that(stats, not_none())
        assert_that(stats.GroupsJoinedCount, is_(0))
        assert_that(stats.GroupsCreatedCount, is_(0))
        assert_that(stats.UsersInGroupsCount, is_(0))
        assert_that(stats.DistinctUsersInGroupsCount, is_(0))

        # Create group
        user = User.create_user(username=u'new_user1')
        group_obj = self._get_group_obj(user)
        group = _get_group(user, group_obj)
        mock_get_created.is_callable().returns((group,))

        stats = self.stat_source.GroupStats
        assert_that(stats.GroupsJoinedCount, is_(0))
        assert_that(stats.GroupsCreatedCount, is_(1))
        assert_that(stats.UsersInGroupsCount, is_(0))
        assert_that(stats.DistinctUsersInGroupsCount, is_(0))

        # Add some friends
        user0 = User.create_user(username=u'new_user0')
        user2 = User.create_user(username=u'new_user2')
        user3 = User.create_user(username=u'new_user3')
        user4 = User.create_user(username=u'new_user4')
        self._add_member(group_obj, user0)
        self._add_member(group_obj, user2)
        self._add_member(group_obj, user3)
        self._add_member(group_obj, user4)

        stats = self.stat_source.GroupStats
        assert_that(stats.GroupsJoinedCount, is_(0))
        assert_that(stats.GroupsCreatedCount, is_(1))
        assert_that(stats.UsersInGroupsCount, is_(4))
        assert_that(stats.DistinctUsersInGroupsCount, is_(4))

        # New group; different owner; one new friend; one dupe friend.
        user5 = User.create_user(username=u'new_user5')
        group_obj2 = self._get_group_obj(user4)
        self._add_member(group_obj2, user0)
        self._add_member(group_obj2, user5)
        group2 = _get_group(user, group_obj2)
        mock_get_joined.is_callable().returns((group2,))

        stats = self.stat_source.GroupStats
        assert_that(stats.GroupsJoinedCount, is_(1))
        assert_that(stats.GroupsCreatedCount, is_(1))
        assert_that(stats.UsersInGroupsCount, is_(6))
        assert_that(stats.DistinctUsersInGroupsCount, is_(5))


class TestAdapters(LearningNetworkTestCase):

    def test_adapting(self):
        user = User(username=u'blehxxxxxxxx')
        now = datetime.utcnow()

        stats_source = component.queryMultiAdapter((user, course, now),
                                                   IInteractionStatsSource)
        assert_that(stats_source, not_none())

        stats_source = component.queryMultiAdapter((user, course),
                                                   IInteractionStatsSource)
        assert_that(stats_source, not_none())

        stats_source = IInteractionStatsSource(user)
        assert_that(stats_source, not_none())
