from django.urls import path
from .views import get_students, sponsor_dashboard, student_details, progress_form, home, complete_details

urlpatterns = [
    path('', home, name='home'),
    path('admin/get_students/', get_students, name='get_students'),
    path('sponsor_dashboard/<int:kafeel_id>/', sponsor_dashboard, name='sponsor_dashboard'),
    path('student_details/<int:admission_number>/', student_details, name='student_details'),
    path('progress_form/<int:kafeel_id>/<int:admission_number>/', progress_form, name='progress_form'),
    path('complete_details/<int:kafeel_id>/<int:admission_number>/', complete_details, name='complete_details'),  # Updated path for complete_details
    # Add more paths for other views as needed
]
