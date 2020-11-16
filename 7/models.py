from orm import UserBase, CategoryBase, CourseBase, SiteUsersBase, session


class TrainingSite(SiteUsersBase):

    def __init__(self):
    
        self.categories = session.query(CategoryBase).all()
        self.courses = session.query(CourseBase).all()
        self.user_types = UserFactory.user_types
        self.users = session.query(UserBase).all()

    def create_category(self, name):
        category = Category(name)
        category.create_object(category)
        self.categories = session.query(CategoryBase).all()
        return category

    def find_category_by_id(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        raise Exception(f'Нет категории с category_id = {category_id}')

    def create_course(self, name, category_id):
        course = CourseFactory.create(name, category_id)
        course.create_object(course)
        self.courses = session.query(CourseBase).all()
        return course

    def get_course(self, course_id):
        for course in self.courses:
            if course.id == course_id:
                return course
        return None
    
    def create_user(self, name, user_type):
        user = UserFactory.create(name, user_type)
        user.create_object(user)
        self.users = session.query(UserBase).all()
        return user
        
    def find_user_by_id(self, user_id):
        for user in self.users:
            if user.id == user_id:
                return user
    
    def create_personal_course(self, course_name, course_id, user_id):
        personal_course = SiteUsers(course_name, course_id, user_id)
        SiteUsersBase.create_object(personal_course)

    def delete_personal_course(self, personal_course_id):
        SiteUsersBase.delete_object(personal_course_id)


class SiteUsers(SiteUsersBase):
    def __init__(self, course_name, course_id, user_id):
        self.name = course_name
        self.course_id = course_id
        self.user_id = user_id


class Category(CategoryBase):

    def __init__(self, name):
        self.name = name
        self.quantity_of_courses = 0


class Course(CourseBase):

    def __init__(self, name, category_id):
        self.name = name
        self.category_id = category_id


class CourseFactory:
    course_class = Course

    @classmethod
    def create(cls, name, category_id):
        return cls.course_class(name, category_id)
    
    
class User(UserBase):

    def __init__(self, name, user_type_, sample_discount):
        self.name = name
        self.user_type = user_type_
        self.sample_discount = sample_discount
        self.variable_discount = sample_discount
        self.discount_percent = str(int(self.variable_discount*100)) + '%'
        self.quantity_of_courses = 0

    @staticmethod
    def course_count(user):
        quantity_of_courses = 0
        personal_courses = SiteUsersBase.course_count(user)
        for course in personal_courses:
            quantity_of_courses += 1
        user.quantity_of_courses = quantity_of_courses
        UserBase.update_object(user)

        return personal_courses, quantity_of_courses

    @staticmethod
    def discount_course(user, quantity):
        user.quantity_of_courses = quantity
        if user.quantity_of_courses <= 2:
            user.variable_discount = user.sample_discount
        if user.quantity_of_courses > 2 and user.quantity_of_courses < 5:
            user.variable_discount = 0.05
            user.variable_discount += user.sample_discount
        if user.quantity_of_courses >= 5 and user.quantity_of_courses < 10:
            user.variable_discount = 0.1
            user.variable_discount += user.sample_discount
        if user.quantity_of_courses >= 10 and user.quantity_of_courses < 20:
            user.variable_discount = 0.2
            user.variable_discount += user.sample_discount
        if user.quantity_of_courses >= 20:
            user.variable_discount = 0.4
            user.variable_discount += user.sample_discount
        user.discount_percent = str(int(user.variable_discount * 100)) + '%'
        """ обновляет поля в БД (3 поля :variable_discount, discount_percent, quantity_of_courses) """
        UserBase.update_object(user)
        return user.discount_percent


class Teacher(User):
    discount = 0.5
    pass


class Student(User):
    discount = 0.1
    pass


class View(User):
    discount = 0
    pass


class UserFactory:
    user_types = {
        'Студент': Student,
        'Учитель': Teacher,
        'Для просмотра': View,
    }

    @classmethod
    def create(cls, name, user_type_):
        discount = cls.user_types[user_type_].discount
        return cls.user_types[user_type_](name, user_type_, discount)


site = TrainingSite()




