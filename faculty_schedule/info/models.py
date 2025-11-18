from django.db import models

class Teacher(models.Model):
    LESSON_TYPE = (
        ('Practics', 'Практический'),
        ('Lection', 'Лексионный')
    )
    fullname = models.CharField(max_length=100, blank=False)
    lesson_type = models.CharField(max_length=50, choices=LESSON_TYPE, blank=False)

    def __str__(self):
        return self.fullname


class Group(models.Model):
    TYPE_CHOICES = (
        ('A', 'A'),
        ('B', 'B')
    )
    COURSE_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4')
    )
    group_name = models.CharField(max_length=100, blank=False)
    group_type = models.CharField(max_length=1, choices=TYPE_CHOICES, default="A", blank=False)
    group_course = models.IntegerField(choices=COURSE_CHOICES, default=1, blank=False)

    def __str__(self):
        return self.group_name


class Classroom(models.Model):
    CLASSROOM_TYPE = (
        ('Computer', 'Компютерный'),
        ('Lection', 'Лексионный')
    )
    LESSON_TIME = (
        (0, '08:00'),
        (1, '09:00'),
        (2, '10:00'),
        (3, '11:00'),
        (4, '12:00'),
        (5, '13:00'),
        (6, '14:00'),
        (7, '15:00'),
        (8, '16:00'),
        (9, '17:00'),
        (10, '18:00'),
    )
    DAY_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    )

    day_of_week = models.IntegerField(choices=DAY_OF_WEEK)
    classroom_number = models.CharField(max_length=100, blank=False)
    classroom_type = models.CharField(max_length=50, choices=CLASSROOM_TYPE, blank=False)
    lesson_time = models.IntegerField(choices=LESSON_TIME, blank=False)


    def __str__(self):
        return self.classroom_number