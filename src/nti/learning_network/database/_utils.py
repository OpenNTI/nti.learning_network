#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division

__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

def increment_field( obj, field, delta=1 ):
	old_val = getattr( obj, field ) or 0
	setattr( obj, field, old_val + delta )

