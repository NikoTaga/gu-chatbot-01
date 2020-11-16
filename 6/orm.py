from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import func
import copy


base = declarative_base()
engine = create_engine('sqlite:///database.db', echo=True)


class CategoryBase(base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	datetime = Column(DateTime(timezone=False), server_default=func.now())
	
	@staticmethod
	def create_object(object):
		session.add(object)
		session.commit()


class CourseBase(base):
	__tablename__ = 'course'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	category_id = Column(Integer, ForeignKey('category.id'))
	datetime = Column(DateTime(timezone=False), server_default=func.now())
	
	@staticmethod
	def create_object(object):
		session.add(object)
		session.commit()
	
	def clone(self):
		"""Clone a registered object and update inner attributes dictionary"""
		return copy.deepcopy(self)


class SiteUsersBase(base):
	__tablename__ = 'site'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	course_id = Column(Integer, ForeignKey('course.id'))
	user_id = Column(Integer, ForeignKey('users.id'))
	datetime = Column(DateTime(timezone=False), server_default=func.now())
	
	@staticmethod
	def create_object(object):
		session.add(object)
		session.commit()
	
	@staticmethod
	def delete_object(object):
		session.query(SiteUsersBase).filter_by(id=object).delete()
		session.commit()


class UserBase(base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	user_type = Column(String)
	sample_discount = Column(Integer)
	variable_discount = Column(Integer)
	discount_percent = Column(String)
	quantity_of_courses = Column(Integer)
	datetime = Column(DateTime(timezone=False), server_default=func.now())
	
	@staticmethod
	def create_object(object):
		session.add(object)
		session.commit()
	
	@staticmethod
	def update_object(object):
		session.query(UserBase).filter_by(id=object.id).update({'variable_discount': object.variable_discount})
		session.query(UserBase).filter_by(id=object.id).update({'discount_percent': object.discount_percent})
		session.query(UserBase).filter_by(id=object.id).update({'quantity_of_courses': object.quantity_of_courses})
		session.commit()


base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
session = Session()
