#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
from nti.learning_network.interfaces import IAccessScoreProvider
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from zope import interface

@interface.implementer( IAccessScoreProvider )
class _AccessScoreProvider( object ):

	def __init__(self, user):
		self.user = user

	def get_score( self, course=None, timestamp=None ):
		pass

