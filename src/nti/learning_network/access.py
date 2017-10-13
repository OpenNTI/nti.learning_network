#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
.. $Id: access.py 84008 2016-03-04 01:39:05Z carlos.sanchez $
"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

from nti.learning_network.interfaces import IAccessScoreProvider


@interface.implementer(IAccessScoreProvider)
class _AccessScoreProvider(object):

	def __init__(self, user):
		self.user = user

	def get_score(self, course=None, timestamp=None):
		pass
