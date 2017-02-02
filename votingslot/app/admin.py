from django.contrib import admin

from models import Appointment, Slot, Student
admin.site.site_header = 'Slot Booking Portal'


class SlotModel(admin.ModelAdmin):
    list_display = ['start_time', 'end_time', 'stud_count']

admin.site.register(Appointment)
admin.site.register(Slot, SlotModel)
admin.site.register(Student)
