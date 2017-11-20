#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904


class MockTimeRecord(object):

    def __init__(self, time_length=0, end_time=0):
        self.time_length = time_length
        self.Duration = time_length
        self.SessionEndTime = end_time


class _MockAnalyticsRecord(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
