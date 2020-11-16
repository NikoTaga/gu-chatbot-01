from jinja2 import Template
from urllib.parse import unquote_plus

from jinja2 import FileSystemLoader
from jinja2.environment import Environment



class Application:
	
	def __init__(self, routes, routes_post, fronts):
		self.routes = routes
		self.routes_post = routes_post
		self.fronts = fronts
	def __call__(self, environ, start_response):
		type_of_request = TypeOfRequest()
		view, dict_data = type_of_request(environ, self.routes, self.routes_post)
		# # #пока не придумал, в чём задействовать front
		# # #for front in self.fronts:
		# # #	front(request)
		code, body = view(dict_data)
		start_response(code, [('Content-Type', 'text/html')])
		return body
	
	def add_route(self, url):
		# паттерн декоратор
		def inner(view):
			self.routes[url] = view
		return inner

class TypeOfRequest:
	"""
	# Определяет тип запроса(post или get), если post, то ищет в теле ENVIRON данные,
	# вытаскиевает их ,декодирует и парсит в словарь.Возвращает view и dict_data
	"""
	def __call__(self, environ, routes, routes_post):
		dict_data = {}
		method = environ['REQUEST_METHOD']
		path = environ['PATH_INFO']
		query_string = environ['QUERY_STRING']
		""" добавление закрывающего слеша """
		if not path.endswith('/'):
			path = f'{path}/'
		""" определяем какой контроллер будем использовать routes или  routes_post """
		if method == 'GET':
			if path in routes:
				view = routes[path]
				query_string_decode = unquote_plus(query_string)
				# dict_data['request_params'] = query_string_decode
				""" получаем словарь из input_data с помощью класса ParseInputData """
				parse_input_data = ParseInputData()
				dict_name = parse_input_data(query_string_decode)
				dict_data['request_params'] = dict_name
			else:
				view = NotFound404View()
		elif method == 'POST':
			if path in routes_post:
				view = routes_post[path]
			else:
				view = NotFound404View()
			""" получаем данные в теле ENVIRON с помощью класса PostMethod"""
			post_method = PostMethod()
			input_encode_data = post_method(environ)
			""" получаем декодированные данные с помощью класса WsgiInputDataDecode """
			wsgi_input_data_decode = WsgiInputDataDecode()
			input_data = wsgi_input_data_decode(input_encode_data)
			""" получаем словарь из input_data с помощью класса ParseInputData """
			parse_input_data = ParseInputData()
			dict_data = parse_input_data(input_data)

		return view, dict_data



class NotFound404View:
	""" если не найден адресс в URL строке, то Page Not Found"""
	def __call__(self, request):
		content = [b'<p style="font-size: 120px;">404 Page Not Found</p>']

		return '404 Page Not Found', content
	
	
class Render:
	"""
	# вставляет данные в страницу HTML и кодирует данные с помощью encode('UTF-8')
	"""
	def __call__(self, template_name, folder='templates', **kwargs):
		env = Environment()
		env.loader = FileSystemLoader(folder)
		template = env.get_template(template_name)
		template_render = template.render(**kwargs)
		template_render_encode = template_render.encode('UTF-8')
		
		return template_render_encode

class PostMethod:
	"""
	# смотрим, есть ли данные в теле ENVIRON (CONTENT_LENGTH должен быть > 0)
	# возвращает данные в байтовом представлении
	"""
	def __call__(self, environ):
		content_length_data = environ.get('CONTENT_LENGTH')
		content_length = int(content_length_data) if content_length_data else 0
		input_encode_data = environ['wsgi.input'].read(content_length) if content_length > 0 else b''
		
		return input_encode_data



class WsgiInputDataDecode:
	"""
	# получаем словарь из данных полученных из POST запроса с помощью parse_qs
	"""
	def __call__(self, input_encode_data: bytes) -> dict:
		if input_encode_data:
			input_decode_data = unquote_plus(input_encode_data.decode('UTF-8'))

		return input_decode_data


class ParseInputData():
	""" преобразуем декодированные данные в словарь dict_data """
	def __call__(self, input_data):
		dict_data = {}
		if input_data:
			param = input_data.split('&')
			for item in param:
				k, v = item.split('=')
				dict_data[k] = v

		return dict_data
	
	
class DebugApplication(Application):
	
	def __init__(self, routes, routes_post, fronts):
		self.application = Application(routes, routes_post, fronts)
		super().__init__(routes, routes_post, fronts)

	def __call__(self, environ, start_response):
		print('DEBUG MODE')
		
		print(environ)
		return self.application(environ, start_response)
	
	
class FakeApplication(Application):

	def __init__(self, routes, routes_post, fronts):
		self.application = Application(routes, routes_post, fronts)
		super().__init__(routes, routes_post, fronts)

	def __call__(self, environ, start_response):
		start_response('200 OK', [('Content-Type', 'text/html')])
		content = [b'<p style="font-size: 120px;">Hello from Fake</p>']
		
		return content