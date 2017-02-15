from django.contrib import admin

from models import Appointment, Slot, Student
admin.site.site_header = 'Slot Booking Portal'


class SlotAdmin(admin.ModelAdmin):
    list_display = ['start_time', 'end_time', 'stud_count', 'max_limit']


class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'web_mail', 'department', 'token_booked']


class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['slot', 'student', 'token', 'created_on']

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Student, StudentAdmin)
