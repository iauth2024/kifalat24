from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from .models import Record, StudentStatusUpdate, Tawassut, Kafeel, Course, Class, Section, Student, Progress, KafeelStatusUpdate
from django.shortcuts import get_object_or_404, render

# Define the admin classes for each model
@admin.register(Tawassut)
class TawassutAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'address')

@admin.register(Kafeel)
class KafeelAdmin(admin.ModelAdmin):
    actions = ['get_students_action']

    def get_students_action(self, request, queryset):
        for kafeel in queryset:
            student_list = Student.objects.filter(kafeel=kafeel, status='Active')

            if student_list.exists():
                message = f"Students connected/sponsored by {kafeel.name}:\n"
                for student in student_list:
                    message += f"{student.name}, "

                self.message_user(request, message)
            else:
                self.message_user(request, f"No active students connected/sponsored by {kafeel.name}.")

        return HttpResponseRedirect(request.get_full_path())

    get_students_action.short_description = "Get Students"

    list_display = ('number', 'name', 'phone', 'address', 'tawassut_link', 'status')

    def tawassut_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('admin:kifalat_tawassut_change', args=[obj.tawassut.id]), obj.tawassut)
    tawassut_link.short_description = 'Tawassut'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(KafeelStatusUpdate)
class KafeelStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('kafeel_number', 'get_kafeel_name', 'status', 'updated_at')
    search_fields = ('kafeel_number',)
    list_filter = ('status', 'updated_at')

    def get_kafeel_name(self, obj):
        try:
            kafeel = Kafeel.objects.get(number=obj.kafeel_number)
            return kafeel.name
        except Kafeel.DoesNotExist:
            return "Kafeel not found"

    get_kafeel_name.short_description = 'Kafeel Name'

@admin.register(StudentStatusUpdate)
class StudentStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'status', 'updated_at')
    search_fields = ('admission_number',)
    list_filter = ('status', 'updated_at')

# Define the inline admin class for Record
class RecordInline(admin.TabularInline):
    model = Record
    extra = 0
    fields = ['month', 'receipt_number', 'amount_paid', 'payment_status', 'study_report']
    search_fields = ['student__admission_number', 'student__name']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student')

    def has_add_permission(self, request, obj=None):
        if obj and obj.status == 'Active':
            return True
        return False

    def display_admission_number(self, obj):
        return obj.student.admission_number

    display_admission_number.short_description = 'Admission Number'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    inlines = [RecordInline]
    list_display = ['admission_number', 'name', 'father_name', 'phone', 'address', 'course', 'class_field', 'section', 'kafeel', 'sponsoring_since', 'monthly_fees', 'total_fees', 'status']
    search_fields = ['admission_number', 'name']
    ordering = ['status', 'name']  # Sorting students alphabetically by status and then by name
    def get_inline_instances(self, request, obj=None):
        inline_instances = super().get_inline_instances(request, obj)
        for inline in inline_instances:
            if isinstance(inline, RecordInline):
                inline.obj = obj
        return inline_instances
    

# Register the RecordAdmin separately
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('student_with_admission_number', 'get_month_display')
    search_fields = ['student__admission_number', 'student__name']  # Add search fields for admission number and student name

    def student_with_admission_number(self, obj):
        return f"{obj.student.name}'s record for {obj.get_month_display()} ({obj.student.admission_number})"
    student_with_admission_number.short_description = 'Record'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'student':
            # Filter only active students
            kwargs['queryset'] = kwargs.get('queryset', self.model._meta.get_field('student').remote_field.model.objects).filter(status='Active')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # Check if the student is active before saving the record
        if obj.student.status != 'Active':
            raise ValidationError("Cannot add a record for an inactive student.")
        super().save_model(request, obj, form, change)
