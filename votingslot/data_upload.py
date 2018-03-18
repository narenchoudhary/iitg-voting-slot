"""
How to use:

1. Provide CSV_PATH: path to CSV containing data.
2. Run the script.

"""

import csv
import os
import string
import random

from django.core.exceptions import ValidationError
from django.core.wsgi import get_wsgi_application
from django.db import IntegrityError

CSV_PATH = "cc_acad_combined.csv"
failures = []
successes = []


def load_application():
    # following two lines are needed to access Django models
    os.environ['DJANGO_SETTINGS_MODULE'] = 'votingslot.settings'
    get_wsgi_application()


def create_user_object(web_mail, save=False):
    load_application()

    from app.models import User

    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(10))
    try:
        user = User(username=web_mail, password=password)
        user.full_clean()
        if save:
            user.save()
            assert len(User.objects.filter(username=web_mail)) != 0
        return user
    except (IntegrityError, ValidationError) as e:
        raise e


def create_student_object(web_mail, roll_no, full_name, gender, dept, programme, save=False):
    load_application()

    from app.models import User, Student

    try:
        user = User.objects.get(username=web_mail)
    except User.DoesNotExist as e:
        return e

    try:
        student = Student(user=user, roll_no=roll_no, full_name=full_name, web_mail=web_mail,
                          gender=gender, department=dept, programme=programme)
        student.full_clean()
        if save:
            student.save()
            assert len(Student.objects.filter(user=user, roll_no=roll_no)) != 0
            return student
    except (IntegrityError, ValidationError) as e:
        raise e


def validate_and_save_data(row):
    roll_no, full_name, web_mail, dept, programme, gender = [row[i] for i in range(0, 6)]
    try:
        user = create_user_object(web_mail, save=True)
    except (IntegrityError, ValidationError) as e:
        return e
    try:
        student = create_student_object(web_mail, roll_no, full_name, gender, dept, programme, save=True)
    except (IntegrityError, ValidationError) as e:
        raise e


def upload_data():
    with open(CSV_PATH, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        row_number = 0
        for row in reader:
            row_number += 1
            try:
                validate_and_save_data(row)
                success_message = "{} added. User: {} ".format(row_number, row[0])
                successes.append(success_message)
            except (IntegrityError, ValidationError) as e:
                error_message = "Error in row {} : {}".format(str(row_number), str(e))
                failures.append(error_message)


if __name__ == '__main__':
    print("Start...")
    upload_data()

    if len(failures) > 0:
        print("FAILED TO UPLOAD {} RECORDS".format(str(len(failures))))
    for message in failures:
        print(message)

    print("-------------------------------------")

    if len(successes) > 0:
        print("SUCCESSFULLY UPLOADED {} RECORDS".format(str(len(successes))))
    for message in successes:
        print(message)
