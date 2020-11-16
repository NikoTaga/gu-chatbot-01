from framework.main import Application, DebugApplication, FakeApplication, Render
from urls import routes, routes_post
from views import fronts
from models import site
from logging_mod import debug

application = Application(routes, routes_post, fronts)
# application = DebugApplication(routes, routes_post, fronts)
# application = FakeApplication(routes, routes_post, fronts)
render = Render()


@application.add_route('/copy-course/')
@debug
def copy_course(request):
	request_params = request['request_params']
	course_id = int(request_params['course_id'])
	old_course = site.get_course(course_id)
	if old_course:
		new_name = f'copy_{old_course.name}'
		new_course = old_course.clone()
		new_course.name = new_name
		site.create_course(new_name, new_course.category_id)
	categories = site.categories
	courses = site.courses
	data = {
		'title': 'Созданы курсы',
		'categories': categories,
		'courses': courses,
	}
	content = render('create_course.html', object_list=data)
	code = '202 Accepted'
	return code, content