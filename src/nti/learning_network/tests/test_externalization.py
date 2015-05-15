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

from ..interfaces import ITimeStats
from ..interfaces import IAdvancedStats
from ..interfaces import IAssignmentStats
from ..interfaces import ISelfAssessmentStats

from ..model import TimeStats
from ..model import AdvancedStats
from ..model import SelfAssessmentStats
from ..model import AssignmentStats

from . import LearningNetworkTestCase

class TestExternalization( LearningNetworkTestCase ):

	def test_time_stats(self):
		count = 10
		std_dev = 1.3
		average = 4.3
		total_time = count * average
		time_stats = TimeStats( Count=count,
							StandardDeviation=std_dev,
							Average=average,
							AggregateTime=total_time )
		assert_that(time_stats, verifiably_provides( ITimeStats ) )

		ext_obj = toExternalObject(time_stats)
		assert_that(ext_obj, has_entry('Class', TimeStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', TimeStats.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))
		assert_that(ext_obj, has_entry('StandardDeviation', std_dev ))
		assert_that(ext_obj, has_entry('Average', average ))
		assert_that(ext_obj, has_entry('AggregateTime', total_time ))

	def test_adv_stats(self):
		count = 10
		std_dev = 1.3
		average = 4.3
		adv_stats = AdvancedStats( Count=count, StandardDeviation=std_dev, Average=average )
		assert_that( adv_stats, verifiably_provides( IAdvancedStats ) )

		ext_obj = toExternalObject( adv_stats )
		assert_that(ext_obj, has_entry('Class', AdvancedStats.__external_class_name__ ))
		assert_that(ext_obj, has_entry('MimeType', AdvancedStats.mimeType ))
		assert_that(ext_obj, has_entry('Count', count ))
		assert_that(ext_obj, has_entry('StandardDeviation', std_dev ))
		assert_that(ext_obj, has_entry('Average', average ))

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
		timed_count = 4
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

