from django.urls import path

from .views import HomeView, UpdateHomeTodo, DeleteHomeTodo, CustomPolicyView, get_policy, get_policy_user, \
    admin_dashboard, landing_page, contact_page, features_page, pricing_page, graph, organization_hirearchy, \
    EquipmentView, equipment_status, equipment_delete, equipment_edit, equipment_form_edit, equipment_search, \
    demo_request, BookmarkView, bookmark_delete, BookmarkEmployeeView, FileManagerView, \
    create_n_edit_file_directory_type, delete_file_directory_type, company_file_directory_type, \
    delete_file_manager_file, bookmark_edit, bookmark_form_edit, share_file, file_share_list

urlpatterns = [
    # urls for Landing Website
    path('', landing_page, name='landing_page_home'),
    path('contact-us/', contact_page, name='contact_page'),
    path('features/', features_page, name='features_page'),
    path('pricing/', pricing_page, name='pricing_page'),
    path('team-hierarchy/', graph, name='hierarchy'),
    path('get_graph/', organization_hirearchy, name='graph'),

    # remaining urls
    path('index/', HomeView.as_view(), name='index'),
    path('assign_policies/', CustomPolicyView.as_view(), name='add_custom_policy'),
    path('policies/<str:pol_id>/get/', get_policy, name='add_custom_policy_policy'),
    path('policyUser/<int:pol_id>/<str:policy>/get/', get_policy_user, name='custom_policy_user_policy_type'),
    path('adminDashboard', admin_dashboard, name='admin_dashboard'),
    path('index/<int:pk>/', HomeView.as_view(), name='index'),
    path('update_home_todo/<str:pk>/', UpdateHomeTodo.as_view(), name='update_home_todo'),
    path('delete_home_todo/<str:pk>/', DeleteHomeTodo.as_view(), name='delete_home_todo'),
    path('equipments/', EquipmentView.as_view(), name='equipments'),
    path('equipment_delete/<int:pk>', equipment_delete, name='equipment_delete'),
    path('equipment_status/<int:equipment_id>/<str:name>', equipment_status, name='equipment_status_update'),
    path('equipment_edit/<int:pk>/', equipment_edit, name='equipment_edit'),
    path('equipment_form_edit/<int:pk>/', equipment_form_edit, name='equipment_form_edit'),
    path('equipment_search/', equipment_search, name='equipment_search'),
    path('demo/', demo_request, name='demo_request'),
    path('bookmarks/', BookmarkView.as_view(), name='bookmarks'),
    path('employee_bookmarks/', BookmarkEmployeeView.as_view(), name='employee_bookmarks'),
    path('bookmark_delete/<int:pk>/', bookmark_delete, name='bookmark_delete'),
    path('file_manager/', FileManagerView.as_view(), name='file_manager'),
    path('file_directory_type/', company_file_directory_type, name='showFileDirectoryType'),
    path('file_directory_type/<str:type>/', create_n_edit_file_directory_type, name='createFileDirectoryType'),
    path('file_directory_type/<int:file_directory_type_id>/edit/', create_n_edit_file_directory_type, name='editFileDirectoryType'),
    path('file_directory_type/<int:file_directory_type_id>/delete/', delete_file_directory_type, name='deleteFileDirectoryType'),
    path('file_manager/<int:pk>/delete/file/', delete_file_manager_file, name='delete_file_manager_file'),
    path('bookmark_edit/<int:pk>/', bookmark_edit, name='bookmark_edit'),
    path('bookmark_form_edit/<int:pk>/', bookmark_form_edit, name='bookmark_form_edit'),
    path('share_file/<int:file>/', share_file, name='share_file'),
    path('file_share_list/<int:file>/', file_share_list, name='file_share_list'),
]