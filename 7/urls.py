from views import Index, CategoryList, CourseList, CreateCourse, CreateUser, CreateCoursePost, CreateCategory, \
	CreateCategoryPost, CreateUserPost, UserList, SelectedUser, SelectedUserPost, AttachCourse, RemoveCourse
		

routes = {
	'/': Index(),
	'/course-list/': CourseList(),
	'/category-list/': CategoryList(),
	'/user-list/': UserList(),
	'/create-course/': CreateCourse(),
	'/create-category/': CreateCategory(),
	'/create-user/': CreateUser(),
	'/selected_user/': SelectedUser(),
	'/attach-course/': AttachCourse(),
	'/remove-course/': RemoveCourse(),
}

routes_post = {
	'/create-course/': CreateCoursePost(),
	'/create-category/': CreateCategoryPost(),
	'/create-user/': CreateUserPost(),
	'/selected_user/': SelectedUserPost(),
}