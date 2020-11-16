from framework.main import Render
from models import site, User
from logging_mod import Logger, debug

logger = Logger('main')


class Index:
	@debug
	def __call__(self, request):
		logger.log('Главная страница')
		data = {
			'title': 'Главная страница',
		}
		content = render('index.html', object_list=data)
		code = '200 OK'
		return code, content


class CreateCourse:
	@debug
	def __call__(self, request):
		logger.log('Создание курсов')
		categories = site.categories
		data = {
			'title': 'Создание курсов',
			'categories': categories,
		}
		content = render('create_course.html', object_list=data)
		code = '200 OK'
		return code, content


class CreateCategory:
	@debug
	def __call__(self, request):
		logger.log('Создание категорий курсов')
		categories = site.categories
		data = {
			'title': 'Создание категорий курсов',
			'categories': categories,
		}
		content = render('create_category.html', object_list=data)
		code = '200 OK'
		return code, content
		
	
class CreateUser:
	@debug
	def __call__(self, request):
		logger.log('Создание пользователя')
		user_types = site.user_types
		data = {
			'title': 'Создание пользователя',
			'user_types': user_types,
		}
		content = render('create_user.html', object_list=data)
		code = '200 OK'
		return code, content
		


class CreateCategoryPost:
	@debug
	def __call__(self, request):
		logger.log('Созданы категории')
		name = request['name']
		new_category = site.create_category(name)
		categories = site.categories
		data = {
			'title': 'Созданы категории',
			'new_category': new_category,
			'categories': categories,
		}
		content = render('create_category.html', object_list=data)
		code = '202 Accepted'
		return code, content


class CreateCoursePost:
	@debug
	def __call__(self, request):
		logger.log('Созданы курсы')
		name = request['name']
		category_id = request['category_id']
		new_course = site.create_course(name, category_id)
		categories = site.categories
		courses = site.courses
		data = {
			'title': 'Созданы курсы',
			'categories': categories,
			'courses': courses,
			'new_course': new_course,
		}
		content = render('create_course.html', object_list=data)
		code = '202 Accepted'
		return code, content


class CreateUserPost:
	@debug
	def __call__(self, request):
		logger.log('Создание пользователя')
		name = request['name']
		user_type = request['user_type']
		new_user = site.create_user(name, user_type)
		users = site.users
		user_types = site.user_types
		data = {
			'title': 'Создание пользователя',
			'user_types': user_types,
			'users': users,
		}
		content = render('create_user.html', object_list=data)
		code = '202 Accepted'
		return code, content

	
class CategoryList:
	@debug
	def __call__(self, request):
		logger.log('Список категорий')
		categories = site.categories
		data = {
			'title': 'Список категорий',
			'categories': categories,
		}
		content = render('category_list.html', object_list=data)
		code = '200 OK'
		return code, content
	
	
class CourseList:
	@debug
	def __call__(self, request):
		logger.log('Список курсов')
		courses = site.courses
		data = {
			'title': 'Список курсов',
			'courses': courses,
		}
		content = render('course_list.html', object_list=data)
		code = '200 OK'
		return code, content
	
	
class UserList:
	@debug
	def __call__(self, request):
		logger.log('Список пользователей')
		users = site.users
		data = {
			'title': 'Список пользователей',
			'users': users,
		}
		content = render('user_list.html', object_list=data)
		code = '200 OK'
		return code, content
	
	
class SelectedUser:
	@debug
	def __call__(self, request):
		logger.log('Выбрать пользователя и привязать курсы')
		users = site.users
		data = {
			'title': 'Выбрать пользователя и привязать курсы',
			'users': users,
		}
		content = render('selected_user.html', object_list=data)
		code = '200 OK'
		return code, content
	
	
class SelectedUserPost:
	@debug
	def __call__(self, request):
		logger.log('Выбрать пользователя и привязать курсы')
		user_id = int(request['user_id'])
		user = site.find_user_by_id(user_id)
		courses = site.courses
		personal_courses, quantity = User.course_count(user)
		User.discount_course(user, quantity)
		data = {
			'title': 'Выбрать пользователя и привязать курсы',
			'user': user,
			'courses': courses,
			'personal_courses': personal_courses,
			'quantity': quantity,
		}
		content = render('view_selected_user.html', object_list=data)
		code = '202 Accepted'
		return code, content
	
	
class AttachCourse:
	@debug
	def __call__(self, request):
		logger.log('Прикрепление курсов')
		course_name = request['request_params']['course_name']
		course_id = int(request['request_params']['course_id'])
		user_id = int(request['request_params']['user_id'])
		user = site.find_user_by_id(user_id)
		site.create_personal_course(course_name, course_id, user_id)
		personal_courses, quantity = User.course_count(user)
		User.discount_course(user, quantity)
		courses = site.courses
		data = {
			'title': 'Выбрать пользователя и привязать курсы',
			'user': user,
			'courses': courses,
			'personal_courses': personal_courses,
			'quantity': quantity,
		}
		content = render('view_selected_user.html', object_list=data)
		code = '202 Accepted'
		return code, content
	
	
class RemoveCourse:
	@debug
	def __call__(self, request):
		logger.log('Удаление курсов')
		user_id = int(request['request_params']['user_id'])
		personal_course_id = int(request['request_params']['personal_course_id'])
		user = site.find_user_by_id(user_id)
		site.delete_personal_course(personal_course_id)
		personal_courses, quantity = User.course_count(user)
		user.discount_percent = User.discount_course(user, quantity)
		courses = site.courses
		data = {
			'title': 'Выбрать пользователя и привязать курсы',
			'user': user,
			'courses': courses,
			'personal_courses': personal_courses,
			'quantity': quantity,
		}
		content = render('view_selected_user.html', object_list=data)
		code = '202 Accepted'
		return code, content
	
	
def secret_front(request):
	request['secret'] = 'some secret'


def other_front(request):
	request['key'] = 'key'


fronts = [secret_front, other_front]

render = Render()
