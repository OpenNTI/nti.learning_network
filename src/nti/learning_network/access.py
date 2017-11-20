#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.learning_network.interfaces import IAccessScoreProvider

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IAccessScoreProvider)
class _AccessScoreProvider(object):

    def __init__(self, user):
        self.user = user

    def get_score(self, course=None, timestamp=None):
        pass
