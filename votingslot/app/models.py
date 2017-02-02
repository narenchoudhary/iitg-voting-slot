from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

from constants import GENDER, DEPARTMENT, PROGRAMMES


class Student(models.Model):
    user = models.ForeignKey(User, null=False)
    roll_no = models.IntegerField(unique=True, verbose_name=_('Roll No'))
    full_name = models.CharField(max_length=120, verbose_name=_('Full Name'))
    web_mail = models.CharField(max_length=60, verbose_name=_('Web-mail'))
    gender = models.CharField(max_length=6, choices=GENDER)
    department = models.CharField(max_length=120, choices=DEPARTMENT)
    programme = models.CharField(max_length=20, choices=PROGRAMMES)
    token_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['roll_no']

    def __unicode__(self):
        return str(self.roll_no)


class Slot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    stud_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['start_time']

    def __unicode__(self):
        start_time = self.start_time.strftime("%I:%M %p")
        end_time = self.end_time.strftime("%I:%M %p")
        return "{} to {}".format(start_time, end_time)


class Appointment(models.Model):
    student = models.ForeignKey(Student, null=False)
    slot = models.ForeignKey(Slot, null=False)
    token = models.CharField(max_length=15, null=True)
    created_on = models.DateTimeField()

    class Meta:
        unique_together = ('student', 'slot')

    def __unicode__(self):
        return self.token

    @staticmethod
    def generate_token():
        return str(uuid.uuid4())[0:8]

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_on = timezone.now()
            self.token = Appointment.generate_token()
            slot = self.slot
            slot.stud_count += 1
            slot.save()
            student = self.student
            student.token_booked = True
            student.save()
        super(Appointment, self).save(*args, **kwargs)
