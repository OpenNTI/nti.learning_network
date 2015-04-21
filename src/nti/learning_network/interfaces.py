#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

from zope import interface

from nti.schema.field import Float

class Stats( interface.Interface ):
	"""
	A container for holding various stats.
	"""

	std_dev = Float( title="Standard deviation", required=True )
	average = Float( title="Average", required=True )
