from django.urls import path

from todo.views import Todos, DeleteTodo, UpdateTodo, update_todo_list, delete_todo_list, add_todo_list

urlpatterns = [
    path('todo/', Todos.as_view(), name='todo'),
    path('delete_todo/<int:pk>/', DeleteTodo.as_view(), name='delete_todo'),
    path('update_todo/<int:pk>/', UpdateTodo.as_view(), name='update_todo'),
    path('delete_todo_list/<int:pk>/', delete_todo_list, name='delete_todo_list'),
    path('update_todo_list/<int:pk>/', update_todo_list, name='update_todo_list'),
    path('add_todo_list/', add_todo_list, name='add_todo'),

]