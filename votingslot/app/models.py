from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
    max_limit = models.IntegerField(default=100)
    stud_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['start_time']

    def __unicode__(self):
        start_time = self.start_time.strftime("%I:%M %p")
        end_time = self.end_time.strftime("%I:%M %p")
        return "{} to {}".format(start_time, end_time)
    
    def save(self, **kwargs):
        if self.max_limit < self.stud_count:
            raise ValidationError("Slot limit reached.")
        super(Slot, self).save(**kwargs)


class Appointment(models.Model):
    student = models.ForeignKey(Student, null=False)
    slot = models.ForeignKey(Slot, null=False)
    token = models.CharField(max_length=15, null=True)
    created_on = models.DateTimeField()

    class Meta:
        unique_together = ('student', 'slot')

    def __unicode__(self):
        return self.token

    def generate_token(self):
        start_time = self.slot.start_time.strftime("%I")
        end_time = self.slot.end_time.strftime("%I")
        count = self.slot.stud_count
        return "{}-{}-{}".format(start_time, count+1, end_time)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_on = timezone.now()
            self.token = self.generate_token()
            slot = self.slot
            slot.stud_count += 1
            slot.save()
            student = self.student
            student.token_booked = True
            student.save()
        super(Appointment, self).save(*args, **kwargs)
