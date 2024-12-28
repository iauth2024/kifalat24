# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import StudentStatusUpdate, Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate
from .forms import ProgressForm, KafeelStatusUpdateForm
from kifalat import models


def home(request):
    return render(request, 'home.html')

def student_details(request, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    progress = Progress.objects.filter(student=student)

    total_paid = progress.aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or 0.0
    total_fees = student.total_fees or 0.0
    due_amount = total_fees - total_paid

    context = {'student': student, 'progress': progress, 'total_paid': total_paid, 'total_fees': total_fees, 'due_amount': due_amount}
    return render(request, 'student_details.html', context)

def progress_form(request, kafeel_id, admission_number):
    kafeel = get_object_or_404(Kafeel, number=kafeel_id)
    student = get_object_or_404(Student, admission_number=admission_number)

    if request.method == 'POST':
        form = ProgressForm(request.POST)
        form.fields['student'].queryset = Student.objects.filter(kafeel=kafeel, status='Active')
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Progress data saved successfully!')
                return redirect('progress_form', kafeel_id=kafeel_id, admission_number=admission_number)
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ProgressForm(initial={'kafeel': kafeel, 'student': student})
        form.fields['student'].queryset = Student.objects.filter(kafeel=kafeel, status='Active')

    context = {'kafeel': kafeel, 'student': student, 'form': form}
    return render(request, 'progress_form.html', context)

def kafeel_status_update(request):
    if request.method == 'POST':
        form = KafeelStatusUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kafeel status updated successfully.')
            return redirect('kafeel_status_update')
        else:
            messages.error(request, 'Error updating Kafeel status. Please check the form data.')
    else:
        form = KafeelStatusUpdateForm()

    context = {'form': form}
    return render(request, 'kafeel_status_update.html', context)
from django.shortcuts import render

from django.db.models import Sum
from decimal import Decimal

# ... (other imports)

def sponsor_dashboard(request, kafeel_id):
    if request.method == 'POST':
        entered_number = request.POST.get('kafeel_number')
        entered_phone = request.POST.get('kafeel_phone')

        try:
            entered_number = int(entered_number)
            entered_phone = int(entered_phone)
            kafeel = get_object_or_404(Kafeel, number=entered_number, phone=entered_phone)

            # Retrieve students associated with the kafeel
            students = Student.objects.filter(kafeel=kafeel, sponsoring_since__isnull=False).order_by('status', 'name')

            # Calculate progress data for each student
            for student in students:
                student.progress_data = Progress.objects.filter(student=student)
                # Calculate total paid
                total_paid = student.progress_data.aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.0')
                # Fetch total fees for the student
                total_fees = Decimal(str(student.total_fees)) if student.total_fees is not None else Decimal('0.0')
                # Calculate due amount
                due_amount = total_fees - total_paid
                # Assign calculated values to the student object
                student.total_paid = total_paid
                student.total_fees = total_fees
                student.due_amount = due_amount

            # Render the sponsor_dashboard template with the kafeel and students data
            context = {'kafeel': kafeel, 'students': students}
            return render(request, 'sponsor_dashboard.html', context)

        except (ValueError, Kafeel.DoesNotExist):
            return render(request, 'sponsor_dashboard_login.html', {'error_message': 'Invalid Kafeel credentials. Please try again.'})

    return render(request, 'sponsor_dashboard_login.html', {'kafeel_id': kafeel_id})

def get_students(request):
    # Your view logic for get_students goes here
    return render(request, 'fetch_students.html', {'students': StudentStatusUpdate})


# views.py

from .models import Progress  # Import the Progress model

from django.shortcuts import render, get_object_or_404
from .models import Student, Record

def complete_details(request, kafeel_id, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    
    # Query records for the student
    records = Record.objects.filter(student=student)
    
    return render(request, 'complete_details.html', {'student': student, 'records': records})


from django.shortcuts import render
from .models import Progress

def progress_view(request):
    progress_data = Progress.objects.all()
    return render(request, 'progress_template.html', {'progress_data': progress_data})

from django.shortcuts import render
from .models import Progress
from .forms import ProgressForm

def create_progress(request):
    if request.method == 'POST':
        form = ProgressForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect or show success message
    else:
        form = ProgressForm()
    return render(request, 'progress_form.html', {'form': form})

from django.shortcuts import render
from .models import Student, Record

def student_detail(request, admission_number):
    student = Student.objects.get(admission_number=admission_number)
    records = Record.objects.filter(student=student)
    return render(request, 'student_detail.html', {'student': student, 'records': records})

from django.shortcuts import render
from .models import Record

def monthly_progress_view(request):
    progress_data = Record.objects.all()  # Retrieve all records from the Record model
    return render(request, 'monthly_progress.html', {'progress_data': progress_data})


###########################################################################################################

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate, StudentStatusUpdate, Record
from .forms import TawassutForm, KafeelForm, CourseForm, ClassForm, SectionForm, StudentForm, ProgressForm, KafeelStatusUpdateForm, StudentStatusUpdateForm, RecordForm

# Tawassut Views
def tawassut_list(request):
    tawassuts = Tawassut.objects.all()
    return render(request, 'tawassut_list.html', {'tawassuts': tawassuts})

def tawassut_add(request):
    if request.method == 'POST':
        form = TawassutForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tawassut_list')
    else:
        form = TawassutForm()
    return render(request, 'tawassut_form.html', {'form': form})

def tawassut_edit(request, pk):
    tawassut = get_object_or_404(Tawassut, pk=pk)
    if request.method == 'POST':
        form = TawassutForm(request.POST, instance=tawassut)
        if form.is_valid():
            form.save()
            return redirect('tawassut_list')
    else:
        form = TawassutForm(instance=tawassut)
    return render(request, 'tawassut_form.html', {'form': form})

def tawassut_delete(request, pk):
    tawassut = get_object_or_404(Tawassut, pk=pk)
    tawassut.delete()
    return redirect('tawassut_list')

# Repeat similar views for other models (Kafeel, Course, Student, etc.)


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Kafeel
from .forms import KafeelForm

# List of Kafeels
def kafeel_list(request):
    kafeels = Kafeel.objects.all()
    return render(request, 'kafeel_list.html', {'kafeels': kafeels})

# Add a new Kafeel
def kafeel_add(request):
    if request.method == 'POST':
        form = KafeelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kafeel_list')
    else:
        form = KafeelForm()
    return render(request, 'kafeel_form.html', {'form': form})

# Edit a Kafeel
def kafeel_edit(request, number):
    kafeel = get_object_or_404(Kafeel, number=number)
    if request.method == 'POST':
        form = KafeelForm(request.POST, instance=kafeel)
        if form.is_valid():
            form.save()
            return redirect('kafeel_list')
    else:
        form = KafeelForm(instance=kafeel)
    return render(request, 'kafeel_form.html', {'form': form})

# Delete a Kafeel
def kafeel_delete(request, number):
    kafeel = get_object_or_404(Kafeel, number=number)
    if request.method == 'POST':
        kafeel.delete()
        return redirect('kafeel_list')
    return render(request, 'kafeel_confirm_delete.html', {'kafeel': kafeel})

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
from .forms import StudentForm

# List of Students
def student_list(request):
    students = Student.objects.all()
    return render(request, 'student_list.html', {'students': students})

# Add a new Student
def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'student_form.html', {'form': form})

# Edit a Student
def student_edit(request, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'student_form.html', {'form': form})

# Delete a Student
def student_delete(request, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'student_confirm_delete.html', {'student': student})



# views.py
