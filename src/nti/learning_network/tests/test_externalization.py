#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import has_entry
from hamcrest import assert_that

from nti.externalization.externalization import toExternalObject

from nti.testing.matchers import verifiably_provides

from ..interfaces import IStats
from ..interfaces import INoteStats
from ..interfaces import ITimeStats
from ..interfaces import IGroupStats
from ..interfaces import ISocialStats
from ..interfaces import ICommentStats
from ..interfaces import IAssignmentStats
from ..interfaces import IThoughtCommentStats
from ..interfaces import ISelfAssessmentStats

from ..model import Stats
from ..model import NoteStats
from ..model import TimeStats
from ..model import GroupStats
from ..model import SocialStats
from ..model import CommentStats
from ..model import AssignmentStats
from ..model import ThoughtCommentStats
from ..model import SelfAssessmentStats

from . import LearningNetworkTestCase

class TestExternalization( LearningNetworkTestCase ):

	def test_stats(self):
		count = 10
		count_stats = Stats( Count=count )
		assert_that(count_stats, verifiably_provides( IStats ) )

		ext_obj = toExternalObject(count_stats)
		assert_that(ext_obj, has_entry('Class', Stats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', Stats.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))

	def test_time_stats(self):
		count = 10
		std_dev = 1.3
		average = 4.3
		total_time = count * average
		time_stats = TimeStats( Count=count,
								StandardDeviationDuration=std_dev,
								AverageDuration=average,
								AggregateTime=total_time )
		assert_that(time_stats, verifiably_provides( ITimeStats ) )

		ext_obj = toExternalObject(time_stats)
		assert_that(ext_obj, has_entry('Class', TimeStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', TimeStats.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))
		assert_that(ext_obj, has_entry('StandardDeviationDuration', std_dev ))
		assert_that(ext_obj, has_entry('AverageDuration', average ))
		assert_that(ext_obj, has_entry('AggregateTime', total_time ))

	def test_assess_stats(self):
		count = 10
		unique_count = 4
		assess_stats = SelfAssessmentStats( Count=count, UniqueCount=unique_count )
		assert_that( assess_stats, verifiably_provides( ISelfAssessmentStats ) )

		ext_obj = toExternalObject( assess_stats )
		assert_that(ext_obj, has_entry('Class', SelfAssessmentStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', SelfAssessmentStats.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))
		assert_that(ext_obj, has_entry('UniqueCount', unique_count ))

	def test_assignment_stats(self):
		count = 10
		unique_count = 4
		late_count = 2
		timed_count = 3
		timed_late_count = 1
		assignment_stats = AssignmentStats( Count=count,
										UniqueCount=unique_count,
										AssignmentLateCount=late_count,
										TimedAssignmentCount=timed_count,
										TimedAssignmentLateCount=timed_late_count )
		assert_that( assignment_stats, verifiably_provides( IAssignmentStats ) )

		ext_obj = toExternalObject( assignment_stats )
		assert_that(ext_obj, has_entry('Class', AssignmentStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', AssignmentStats.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))
		assert_that(ext_obj, has_entry('UniqueCount', unique_count ))
		assert_that(ext_obj, has_entry('AssignmentLateCount', late_count ))
		assert_that(ext_obj, has_entry('TimedAssignmentCount', timed_count ))
		assert_that(ext_obj, has_entry('TimedAssignmentLateCount', timed_late_count ))

	def _test_post_stats( self, clazz, iface, std_dev_length ):
		count = 10
		reply_count = 4
		top_level_count = 6
		distinct_like_count = 3
		distinct_fave_count = 2
		total_likes = 12
		total_faves = 8
		recursive_child_count = 24
		average_length = 50
		contains_board_count = 5

		post_stats = clazz( Count=count,
							ReplyCount=reply_count,
							TopLevelCount=top_level_count,
							DistinctPostsLiked=distinct_like_count,
							DistinctPostsFavorited=distinct_fave_count,
							TotalLikes=total_likes,
							TotalFavorites=total_faves,
							RecursiveChildrenCount=recursive_child_count,
							StandardDeviationLength=std_dev_length,
							AverageLength=average_length,
							ContainsWhiteboardCount=contains_board_count )
		assert_that( post_stats, verifiably_provides( iface ) )

		ext_obj = toExternalObject( post_stats )
		assert_that(ext_obj, has_entry('Class', clazz.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', clazz.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))
		assert_that(ext_obj, has_entry('ReplyCount', reply_count ))
		assert_that(ext_obj, has_entry('TopLevelCount', top_level_count ))
		assert_that(ext_obj, has_entry('DistinctPostsLiked', distinct_like_count ))
		assert_that(ext_obj, has_entry('DistinctPostsFavorited', distinct_fave_count ))
		assert_that(ext_obj, has_entry('TotalLikes', total_likes ))
		assert_that(ext_obj, has_entry('TotalFavorites', total_faves ))
		assert_that(ext_obj, has_entry('RecursiveChildrenCount', recursive_child_count ))
		assert_that(ext_obj, has_entry('StandardDeviationLength', std_dev_length ))
		assert_that(ext_obj, has_entry('AverageLength', average_length ))
		assert_that(ext_obj, has_entry('ContainsWhiteboardCount', contains_board_count ))

	def test_note_stats(self):
		self._test_post_stats( NoteStats, INoteStats, 17.3 )
		self._test_post_stats( NoteStats, INoteStats, None )

	def test_comment_stats(self):
		self._test_post_stats( CommentStats, ICommentStats, 18.4 )
		self._test_post_stats( CommentStats, ICommentStats, None )

	def test_thought_comment_stats(self):
		self._test_post_stats( ThoughtCommentStats, IThoughtCommentStats, 18.4 )
		self._test_post_stats( ThoughtCommentStats, IThoughtCommentStats, None )

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
