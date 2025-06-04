import calendar
from django.db import models
from django.forms import ValidationError


class Tawassut(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.TextField()

    def __str__(self):
        return self.name


class Kafeel(models.Model):
    number = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    tawassut = models.ForeignKey(Tawassut, on_delete=models.SET_NULL, null=True)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    monthly_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Student(models.Model):
    admission_number = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    address = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_field = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    kafeel = models.ForeignKey(Kafeel, on_delete=models.CASCADE)
    sponsoring_since = models.DateField(null=True)
    monthly_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
        ('Dropped Out', 'Dropped Out'),
        ('Course Complete', 'Course Complete'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Calculate total fees based on monthly fees
        self.total_fees = self.monthly_fees * 12
        super().save(*args, **kwargs)
    def get_total_paid(self):
        return sum(record.amount_paid for record in self.record_set.filter(payment_status='paid') if record.amount_paid)

    def get_due_amount(self):
        return self.total_fees - self.get_total_paid()

    def save(self, *args, **kwargs):
        self.total_fees = self.monthly_fees * 12
        super().save(*args, **kwargs)

from django.db import models

import calendar
from django.db import models

import calendar

class Progress(models.Model):
    PAID_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    MONTH_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1, 13)]
    
    kafeel = models.ForeignKey(Kafeel, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=255, unique=True, null=True, blank=True, default='N/A')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default='N/A')

    study_report = models.TextField(null=True, blank=True)  # Allow null and blank for later update
    paid_date = models.DateTimeField()
    month = models.CharField(max_length=20, choices=MONTH_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAID_CHOICES, default='unpaid', null=True, blank=True)  # Allow null and blank for later update

    def clean(self):
        if self.kafeel and hasattr(self.kafeel, 'status') and self.kafeel.status == 'Deactive':
            raise ValidationError("Cannot accept payment for a deactivated Kafeel.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class KafeelStatusUpdate(models.Model):
    kafeel_number = models.IntegerField()
    status = models.CharField(max_length=20, choices=[
        ('Activate', 'Activate'),
        ('Deactivate', 'Deactivate'),
    ])
    updated_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Validate Kafeel number
        try:
            kafeel = Kafeel.objects.get(number=self.kafeel_number)
        except Kafeel.DoesNotExist:
            raise ValidationError("Kafeel with the provided number does not exist.")

        # Update Kafeel status
        if self.status == 'Activate':
            kafeel.status = 'Active'
        elif self.status == 'Deactivate':
            kafeel.status = 'Deactive'

        kafeel.save()

        super().save(*args, **kwargs)


class StudentStatusUpdate(models.Model):
    admission_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=[
        ('Active', 'Active'),
        ('Deactive', 'Deactive'),
    ])
    updated_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        try:
            student = Student.objects.get(admission_number=self.admission_number)
        except Student.DoesNotExist:
            raise ValidationError("Student with the provided admission number does not exist.")

        if student.status == self.status:
            raise ValidationError(f"The student is already {self.status}.")

    def save(self, *args, **kwargs):
        self.full_clean()

        # Update Student status
        student = Student.objects.get(admission_number=self.admission_number)
        student.status = self.status
        student.save()

        super().save(*args, **kwargs)

from django.db import models
import calendar

from django.db import models
from django.core.exceptions import ValidationError
import calendar

class Record(models.Model):
    month_CHOICES = [
        ('Muharram', 'Muharram'),
        ('Safar', 'Safar'),
        ('Rabi\' al-awwal', 'Rabi\' al-awwal'),
        ('Rabi\' al-thani', 'Rabi\' al-thani'),
        ('Jumada al-awwal', 'Jumada al-awwal'),
        ('Jumada al-thani', 'Jumada al-thani'),
        ('Rajab', 'Rajab'),
        ('Sha\'ban', 'Sha\'ban'),
        ('Ramadan', 'Ramadan'),
        ('Shawwal', 'Shawwal'),
        ('Dhu al-Qi\'dah', 'Dhu al-Qi\'dah'),
        ('Dhu al-Hijjah', 'Dhu al-Hijjah'),
    ]

    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=month_CHOICES)
    receipt_number = models.CharField(max_length=255, blank=True, default='--')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    study_report = models.TextField(max_length=255, blank=True, default='')
    paid_date = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=[
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ], default='unpaid', blank=False)

    def clean(self):
        # Allow amount_paid=0 with payment_status='paid' for advance payments
        if self.payment_status == 'unpaid' and self.amount_paid and self.amount_paid > 0:
            raise ValidationError("Payment status 'Unpaid' cannot have a non-zero amount paid.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name}'s record for {self.month}"