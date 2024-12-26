from django import forms
from .models import Kafeel, KafeelStatusUpdate, Progress, Student

from django import forms
from .models import Progress

class ProgressForm(forms.ModelForm):
    class Meta:
        model = Progress
        fields = '__all__'
        widgets = {
            'month': forms.Select(choices=Progress.MONTH_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kafeel'].queryset = Kafeel.objects.filter(status='Active')

        if 'kafeel' in self.data:
            try:
                kafeel_id = int(self.data.get('kafeel'))
                self.fields['student'].queryset = Student.objects.filter(kafeel__number=kafeel_id, status='Active')
            except ValueError:
                pass
        elif self.instance and self.instance.kafeel:
            self.fields['student'].queryset = Student.objects.filter(kafeel=self.instance.kafeel, status='Active')

        # Adding the following line to filter students dynamically in the form
        self.fields['student'].queryset = Student.objects.none()

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



#   py manage.py makemigrations
#   py manage.py migrate
#   py manage.py runserver