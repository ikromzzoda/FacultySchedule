from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Teacher(models.Model):

    class LessonType(models.TextChoices):
        PRACTICAL = 'practical', 'Практический'
        LECTURE = 'lecture', 'Лекционный'

    fullname = models.CharField(
        max_length=100,
        verbose_name='ФИО преподавателя'
    )
    lesson_type = models.CharField(
        max_length=50,
        choices=LessonType.choices,
        verbose_name='Тип занятия'
    )

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['fullname']

    def __str__(self):
        return f"{self.fullname} ({self.lesson_type})"


class Groups(models.Model):

    class GroupType(models.TextChoices):
        A = 'A', 'A'
        B = 'B', 'B'

    group_name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название группы'
    )
    group_type = models.CharField(
        max_length=10,
        choices=GroupType.choices,
        default=GroupType.A,
        verbose_name='Тип группы'
    )
    group_course = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        default=1,
        verbose_name='Курс'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['group_course', 'group_name']

    def __str__(self):
        return f"{self.group_name} (курс {self.group_course})"


class DayofWeek(models.IntegerChoices):
    MONDAY = 0, 'Понедельник'
    TUESDAY = 1, 'Вторник'
    WEDNESDAY = 2, 'Среда'
    THURSDAY = 3, 'Четверг'
    FRIDAY = 4, 'Пятница'
    SATURDAY = 5, 'Суббота'
    SUNDAY = 6, 'Воскресенье'


class LessonTime(models.IntegerChoices):
    SLOT_0 = 0, '08:00'
    SLOT_1 = 1, '09:00'
    SLOT_2 = 2, '10:00'
    SLOT_3 = 3, '11:00'
    SLOT_4 = 4, '12:00'
    SLOT_5 = 5, '13:00'
    SLOT_6 = 6, '14:00'
    SLOT_7 = 7, '15:00'
    SLOT_8 = 8, '16:00'
    SLOT_9 = 9, '17:00'
    SLOT_10 = 10, '18:00'


class Classroom(models.Model):

    class ClassroomType(models.TextChoices):
        COMPUTER = 'computer', 'Компьютерный'
        LECTURE = 'lecture', 'Лекционный'

    classroom_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Номер аудитории'
    )
    classroom_type = models.CharField(
        max_length=50,
        choices=ClassroomType.choices,
        verbose_name='Тип аудитории'
    )
    capacity = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        verbose_name='Вместимость'
    )

    class Meta:
        verbose_name = 'Аудитория'
        verbose_name_plural = 'Аудитории'
        ordering = ['classroom_number']

    def __str__(self):
        return f"Аудитория {self.classroom_number} ({self.classroom_type})"


class Schedule(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name='Преподаватель'
    )
    group = models.ForeignKey(
        Groups,
        on_delete=models.CASCADE,
        verbose_name='Группа'
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        verbose_name='Аудитория'
    )
    day_of_week = models.IntegerField(
        choices=DayofWeek.choices,
        verbose_name='День недели'
    )
    lesson_time = models.IntegerField(
        choices=LessonTime.choices,
        verbose_name='Время занятия'
    )

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        unique_together = [
            ['teacher', 'day_of_week', 'lesson_time'],
            ['group', 'day_of_week', 'lesson_time'],
            ['classroom', 'day_of_week', 'lesson_time']
        ]
        ordering = ['day_of_week', 'lesson_time']

    def __str__(self):
        return (
            f"{self.group.group_name} - "
            f"{self.teacher.fullname} - "
            f"Ауд. {self.classroom.classroom_number} - "
            f"{self.get_day_of_week_display()} {self.get_lesson_time_display()}"
        )


def find_free_slots(teacher, group, day_of_week, lesson_time):
    """
    Находит свободные слоты для проведения занятия.

    Args:
        teacher: объект Teacher
        group: объект Group
        day_of_week: день недели (0-6)
        lesson_time: время занятия (0-10)

    Returns:
        dict: {
            'teacher_free': bool,
            'group_free': bool,
            'available_classrooms': QuerySet,
            'can_schedule': bool
        }
    """

    # Проверяем, свободен ли преподаватель
    teacher_busy = Schedule.objects.filter(
        teacher=teacher,
        day_of_week=day_of_week,
        lesson_time=lesson_time
    ).exists()

    # Проверяем, свободна ли группа
    group_busy = Schedule.objects.filter(
        group=group,
        day_of_week=day_of_week,
        lesson_time=lesson_time
    ).exists()

    # Получаем занятые аудитории в это время
    busy_classrooms = Schedule.objects.filter(
        day_of_week=day_of_week,
        lesson_time=lesson_time
    ).values_list('classroom_id', flat=True)

    # Сопоставляем тип занятия преподавателя с типом аудитории
    classroom_type_map = {
        'practical': 'computer',
        'lecture': 'lecture'
    }

    required_classroom_type = classroom_type_map.get(teacher.lesson_type)

    # Находим свободные аудитории нужного типа
    available_classrooms = Classroom.objects.filter(
        classroom_type=required_classroom_type
    ).exclude(
        id__in=busy_classrooms
    )

    return {
        'teacher_free': not teacher_busy,
        'group_free': not group_busy,
        'available_classrooms': available_classrooms,
        'can_schedule': not teacher_busy and not group_busy and available_classrooms.exists()
    }


def get_weekly_availability(teacher, group):
    """
    Получает полное расписание доступности на неделю.

    Args:
        teacher: объект Teacher
        group: объект Group

    Returns:
        dict: расписание свободных слотов по дням и времени
    """

    availability = {}

    for day in DayofWeek.values:
        day_name = DayofWeek(day).label
        availability[day_name] = {}

        for time_slot in LessonTime.values:
            time_label = LessonTime(time_slot).label

            result = find_free_slots(teacher, group, day, time_slot)

            availability[day_name][time_label] = {
                'can_schedule': result['can_schedule'],
                'teacher_free': result['teacher_free'],
                'group_free': result['group_free'],
                'available_classrooms': [
                    cls.classroom_number
                    for cls in result['available_classrooms']
                ]
            }

    return availability

