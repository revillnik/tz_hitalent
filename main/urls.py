from django.urls import path

from .views import DepartmentView, DepartmentIdEmployeesView, DepartmentIdView



urlpatterns = [
    path('departments/', DepartmentView.as_view(), name='departments'),
    path('departments/<int:id>/employees/', DepartmentIdEmployeesView.as_view(), name='departments_id_employees'),
    path('departments/<int:id>', DepartmentIdView.as_view(), name='departments_id'),
]
