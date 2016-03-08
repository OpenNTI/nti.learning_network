#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import assert_that

from datetime import datetime

from nti.externalization.externalization import toExternalObject

from nti.testing.matchers import verifiably_provides

from nti.learning_network.interfaces import IGroupStats
from nti.learning_network.interfaces import ISocialStats
from nti.learning_network.interfaces import IConnection

from nti.learning_network.model import GroupStats
from nti.learning_network.model import SocialStats
from nti.learning_network.model import Connection

from nti.learning_network.tests import LearningNetworkTestCase

class TestExternalization( LearningNetworkTestCase ):

	def test_social_stats(self):
		contact_count = 10
		reply_to_count = 7
		user_reply_count = 1
		social_stats = SocialStats( ContactsAddedCount=contact_count,
									DistinctReplyToCount=reply_to_count,
									DistinctUserReplyToOthersCount=user_reply_count )
		assert_that( social_stats, verifiably_provides( ISocialStats ) )

		ext_obj = toExternalObject( social_stats )
		assert_that(ext_obj, has_entry('Class', SocialStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', SocialStats.mimeType ))
		assert_that(ext_obj, has_entry('ContactsAddedCount', contact_count ))
		assert_that(ext_obj, has_entry('DistinctReplyToCount', reply_to_count ))
		assert_that(ext_obj, has_entry('DistinctUserReplyToOthersCount', user_reply_count ))

	def test_group_stats(self):
		group_count = 4
		group_created_count = 2
		user_count = 7
		distinct_user_count = 1
		group_stats = GroupStats( 	GroupsJoinedCount=group_count,
									GroupsCreatedCount=group_created_count,
									UsersInGroupsCount=user_count,
									DistinctUsersInGroupsCount=distinct_user_count )
		assert_that( group_stats, verifiably_provides( IGroupStats ) )

		ext_obj = toExternalObject( group_stats )
		assert_that(ext_obj, has_entry('Class', GroupStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', GroupStats.mimeType ))
		assert_that(ext_obj, has_entry('GroupsJoinedCount', group_count ))
		assert_that(ext_obj, has_entry('GroupsCreatedCount', group_created_count ))
		assert_that(ext_obj, has_entry('UsersInGroupsCount', user_count ))
		assert_that(ext_obj, has_entry('DistinctUsersInGroupsCount', distinct_user_count ))

	def test_connection(self):
		source = 'bobodenkirk'
		target = 'davidcross'
		now = datetime.utcnow()
		connection = Connection( Source=source,
								Target=target,
								Timestamp=now )
		assert_that( connection, verifiably_provides( IConnection ) )

		ext_obj = toExternalObject( connection )
		assert_that(ext_obj, has_entry('Class', Connection.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', Connection.mimeType ))
		assert_that(ext_obj, has_entry('Source', source ))
		assert_that(ext_obj, has_entry('Target', target ))
