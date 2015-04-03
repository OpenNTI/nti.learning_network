#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
$Id$
"""
from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

from sqlalchemy.ext.declarative import declared_attr

class LearningNetworkTableMixin(object):

	@declared_attr
	def user_id(cls):
		return Column('user_id', Integer, ForeignKey("Users.user_id"), index=True, nullable=True )

	# The last time this bucket/row was updated.
	last_modified = Column('last_modified', DateTime, nullable=True )

	bucket_start_time = Column('bucket_start_time', DateTime, nullable=False, index=True )

	bucket_end_time = Column('bucket_end_time', DateTime, nullable=False, index=True )

class CourseLearningNetworkTableMixin( LearningNetworkTableMixin ):

	course_id = Column('course_id', Integer, nullable=True,
					index=True, autoincrement=False, default=None)

class StatMixin( object ):
	"""
	A collection of stat columns.
	"""

	total_duration = Column('total_duration', Integer, nullable=False, autoincrement=False, default=0 )
	count = Column('count', Integer, nullable=False, autoincrement=False, default=0 )
	sum_of_squares = Column('sum_of_squares', Integer, nullable=False, autoincrement=False, default=0 )
