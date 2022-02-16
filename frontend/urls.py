from django.urls import path

from .views import DashboardView, DatasetView, AnnotationView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard_view'),
    path('<int:project_id>/', DatasetView.as_view(), name='dataset_list_view'),
    path('<int:project_id>/<int:dataset_id>', AnnotationView.as_view(), name='annotation_view'),

]