from django.urls import path
from .views import (
    get_students, kafeel_delete, kafeel_edit, kafeel_list, 
    sponsor_dashboard, student_details, progress_form, home, 
    complete_details, tawassut_delete, tawassut_edit, tawassut_list,
    student_list, student_edit, student_delete
)
from kifalat import views

urlpatterns = [
    path('', home, name='home'),
    path('admin/get_students/', get_students, name='get_students'),
    path('sponsor_dashboard/<int:kafeel_id>/', sponsor_dashboard, name='sponsor_dashboard'),
    path('student_details/<int:admission_number>/', student_details, name='student_details'),
    path('progress_form/<int:kafeel_id>/<int:admission_number>/', progress_form, name='progress_form'),
    path('complete_details/<int:kafeel_id>/<int:admission_number>/', complete_details, name='complete_details'),
    path('student_records/<str:admission_number>/', views.student_record_details, name='student_record_details'),
    # Tawassut URLs
    path('tawassut/', tawassut_list, name='tawassut_list'),
    path('tawassut/edit/<int:id>/', tawassut_edit, name='tawassut_edit'),
    path('tawassut/delete/<int:id>/', tawassut_delete, name='tawassut_delete'),
    
    # Kafeel URLs
    path('kafeel/', kafeel_list, name='kafeel_list'),
    path('kafeel/edit/<int:id>/', kafeel_edit, name='kafeel_edit'),
    path('kafeel/delete/<int:id>/', kafeel_delete, name='kafeel_delete'),

    # Student URLs
    path('student/', student_list, name='student_list'),
    path('student/edit/<str:id>/', student_edit, name='student_edit'),
    path('student/delete/<str:id>/', student_delete, name='student_delete'),
]
