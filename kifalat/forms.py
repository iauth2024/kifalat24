from django import forms
from .models import Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate, StudentStatusUpdate, Record

class TawassutForm(forms.ModelForm):
    class Meta:
        model = Tawassut
        fields = ['name', 'phone', 'address']

class KafeelForm(forms.ModelForm):
    class Meta:
        model = Kafeel
        fields = ['name', 'phone', 'address', 'status', 'monthly_amount', 'tawassut']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name']

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name']

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['admission_number', 'name', 'father_name', 'phone', 'address', 'course', 'class_field', 'section', 'kafeel', 'sponsoring_since', 'monthly_fees', 'total_fees', 'status']

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = ['kafeel', 'student', 'receipt_number', 'amount_paid', 'study_report', 'paid_date', 'month', 'payment_status']
        widgets = {
            'month': forms.Select(choices=Progress.MONTH_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter Kafeel choices to only Active ones
        self.fields['kafeel'].queryset = Kafeel.objects.filter(status='Active')

        # Dynamically filter student based on the selected kafeel
        if 'kafeel' in self.data:
            try:
                kafeel_id = int(self.data.get('kafeel'))
                self.fields['student'].queryset = Student.objects.filter(kafeel__number=kafeel_id, status='Active')
            except ValueError:
                pass
        elif self.instance and self.instance.kafeel:
            self.fields['student'].queryset = Student.objects.filter(kafeel=self.instance.kafeel, status='Active')

class KafeelStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = KafeelStatusUpdate
        fields = ['kafeel_number', 'status']

class StudentStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentStatusUpdate
        fields = ['admission_number', 'status']

class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['student', 'month', 'receipt_number', 'amount_paid', 'study_report', 'paid_date', 'payment_status']
