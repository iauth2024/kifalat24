# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import StudentStatusUpdate, Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate
from .forms import ProgressForm, KafeelStatusUpdateForm
from kifalat import models 
from django.db.models import Sum

def home(request):
    return render(request, 'home.html')

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from decimal import Decimal
from kifalat.models import Student, Progress

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from decimal import Decimal
from .models import Student, Record

def student_details(request, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    records = Record.objects.filter(student=student)
    
    # Calculate total paid from primary payments
    total_paid = records.filter(payment_status='paid', amount_paid__gt=0).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.0')
    # Count paid months (including advance payments)
    paid_months = records.filter(payment_status='paid').count()
    total_fees = student.total_fees or Decimal('0.0')
    due_amount = total_fees - (student.monthly_fees * paid_months)

    context = {
        'student': student,
        'records': records,
        'total_paid': total_paid,
        'total_fees': total_fees,
        'due_amount': due_amount,
        'paid_months': paid_months
    }
    return render(request, 'student_details.html', context)

# kifalat/views.py
from decimal import Decimal
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404
from .models import Student, Record

def student_record_details(request, admission_number):
    student = get_object_or_404(Student, admission_number=admission_number)
    records = Record.objects.filter(student=student)

    # Filters from GET request
    month_filter = request.GET.get('month_filter')
    receipt_filter = request.GET.get('receipt_filter')
    payment_status_filter = request.GET.get('payment_status_filter')
    study_report_filter = request.GET.get('study_report_filter')

    # Apply filters
    if month_filter:
        records = records.filter(month=month_filter)
    if receipt_filter:
        records = records.filter(receipt_number__icontains=receipt_filter)
    if payment_status_filter:
        records = records.filter(payment_status=payment_status_filter)
    if study_report_filter:
        records = records.filter(study_report=study_report_filter)

    # Sum only where payment_status is 'paid' (case-insensitive)
    total_paid = records.filter(
        Q(payment_status__iexact='paid')
    ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.0')

    # Count paid months (even if amount is 0)
    paid_months = records.filter(Q(payment_status__iexact='paid')).count()

    # Fees and balance logic
    total_fees = Decimal(str(student.total_fees)) if student.total_fees is not None else Decimal('0.0')
    monthly_fees = Decimal(str(student.monthly_fees)) if student.monthly_fees is not None else Decimal('0.0')

    # Option A (recommended): use total_fees - total_paid
    balance = total_fees - total_paid

    # Option B (if using monthly fees): uncomment below if that's your logic
    # balance = total_fees - (monthly_fees * paid_months)

    # Get study report options
    study_reports = Record.objects.filter(
        student=student
    ).exclude(study_report='').values_list('study_report', flat=True).distinct()

    record_month_choices = Record.month_CHOICES

    context = {
        'student': student,
        'records': records,
        'total_paid': total_paid,
        'balance': balance,
        'paid_months': paid_months,
        'total_fees': total_fees,
        'monthly_fees': monthly_fees,
        'study_reports': study_reports,
        'record_month_choices': record_month_choices,
        'month_filter': month_filter,
        'receipt_filter': receipt_filter,
        'payment_status_filter': payment_status_filter,
        'study_report_filter': study_report_filter
    }

    return render(request, 'student_record_details.html', context)

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

from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from decimal import Decimal
from .models import Kafeel, Student, Record
from decimal import Decimal
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404
from .models import Kafeel, Student, Record

from decimal import Decimal
from django.db.models import Q, Sum
from django.shortcuts import render, get_object_or_404
from .models import Kafeel, Student, Record

def sponsor_dashboard(request, kafeel_id):
    if request.method == 'POST':
        entered_number = request.POST.get('kafeel_number')
        entered_phone = request.POST.get('kafeel_phone')

        try:
            entered_number = int(entered_number)
            entered_phone = str(entered_phone)

            # Fetch Kafeel
            kafeel = get_object_or_404(Kafeel, number=entered_number, phone=entered_phone)

            # Fetch sponsored students
            students = Student.objects.filter(
                kafeel=kafeel,
                sponsoring_since__isnull=False
            ).order_by('status', 'name')

            # Initialize totals
            kafeel_total_paid = Decimal('0.0')
            kafeel_total_due = Decimal('0.0')

            for student in students:
                # Get records for the student
                student.records = Record.objects.filter(student=student)

                # Calculate total paid (case-insensitive filter)
                total_paid = student.records.filter(
                    Q(payment_status__iexact='paid')
                ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.0')

                # Total fees
                total_fees = Decimal(str(student.total_fees)) if student.total_fees is not None else Decimal('0.0')

                # Due amount
                due_amount = total_fees - total_paid

                # Attach to student object
                student.total_paid = total_paid
                student.total_fees = total_fees
                student.due_amount = due_amount

                # Add to sponsor-level totals
                kafeel_total_paid += total_paid
                kafeel_total_due += due_amount

            sponsored_students = students.filter(status='Active').count()

            context = {
                'kafeel': kafeel,
                'students': students,
                'kafeel_total_paid': kafeel_total_paid,
                'kafeel_total_due': kafeel_total_due,
                'sponsored_students': sponsored_students
            }

            return render(request, 'sponsor_dashboard.html', context)

        except (ValueError, Kafeel.DoesNotExist):
            return render(request, 'sponsor_dashboard_login.html', {
                'error_message': 'Invalid Kafeel credentials. Please try again.'
            })

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
