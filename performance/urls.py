from django.urls import path

from performance.views import IndicatorView, indicator_delete, indicator_edit, indicator_form_edit, PerformanceView, \
    PerformanceListView, performance_delete, performance_graph, performance_graph_detail, PerformanceEmployeeView, \
    employee_performance_detail, publish_performance

urlpatterns = [
    path('indicators/', IndicatorView.as_view(), name='indicator'),
    path('indicator_delete/<int:pk>/', indicator_delete, name='indicator_delete'),
    path('indicator_edit/<int:pk>/', indicator_edit, name='indicator_edit'),
    path('indicator_form_edit/<int:pk>/', indicator_form_edit, name='indicator_form_edit'),
    path('performance/', PerformanceView.as_view(), name='performance'),
    path('performance_list/', PerformanceListView.as_view(), name='performance_list'),
    path('performance_delete/<int:pk>', performance_delete, name='performance_delete'),
    path('performance_graph/<int:pk>', performance_graph, name='performance_graph'),
    path('performance_details/<int:pk>', performance_graph_detail, name='performance_detail'),
    path('performance_employee/', PerformanceEmployeeView.as_view(), name='performance_detail_employee'),
    path('employee_performance_detail/<int:performance_id>/', employee_performance_detail, name='employee_performance_detail'),
    path('performance_status/<int:performance_id>/', publish_performance, name='performance_status'),

]