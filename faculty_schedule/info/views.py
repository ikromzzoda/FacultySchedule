import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Teacher, Groups, Subject, Classroom, Schedule, DayofWeek, LessonTime


@csrf_exempt
def create_teacher(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        teacher = Teacher.objects.create(
            fullname=data['fullname'],
            lesson_type=data['lesson_type']
        )
        return JsonResponse({'id': teacher.id, 'fullname': teacher.fullname, 'lesson_type': teacher.lesson_type})
    return JsonResponse({'error': 'Invalid request method'})


@csrf_exempt
def edit_teacher(request, teacher_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.fullname = data.get('fullname', teacher.fullname)
        teacher.lesson_type = data.get('lesson_type', teacher.lesson_type)
        teacher.save()
        return JsonResponse({'id': teacher.id, 'fullname': teacher.fullname, 'lesson_type': teacher.lesson_type})
    return JsonResponse({'error': 'Invalid request method'})


def get_teachers(request):
    teachers = Teacher.objects.all().values('id', 'fullname', 'lesson_type')
    return JsonResponse(list(teachers), safe=False)


@csrf_exempt
def create_group(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        group = Groups.objects.create(
            group_name=data['group_name'],
            group_type=data['group_type'],
            group_course=data['group_course']
        )
        return JsonResponse({'id': group.id, 'group_name': group.group_name, 'group_type': group.group_type,
                             'group_course': group.group_course})
    return JsonResponse({'error': 'Invalid request method'})


@csrf_exempt
def edit_group(request, group_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        group = Groups.objects.get(id=group_id)
        group.group_name = data.get('group_name', group.group_name)
        group.group_type = data.get('group_type', group.group_type)
        group.group_course = data.get('group_course', group.group_course)
        group.save()
        return JsonResponse({'id': group.id, 'group_name': group.group_name, 'group_type': group.group_type,
                             'group_course': group.group_course})
    return JsonResponse({'error': 'Invalid request method'})


def get_groups(request):
    groups = Groups.objects.all().values('id', 'group_name', 'group_type', 'group_course')
    return JsonResponse(list(groups), safe=False)


@csrf_exempt
def add_subject(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.create(subject_name=data['subject_name'])
        if 'teachers' in data:
            subject.teachers.set(data['teachers'])
        return JsonResponse({'id': subject.id, 'subject_name': subject.subject_name})
    return JsonResponse({'error': 'Invalid request method'})


@csrf_exempt
def edit_subject(request, subject_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        subject = Subject.objects.get(id=subject_id)
        subject.subject_name = data.get('subject_name', subject.subject_name)
        if 'teachers' in data:
            subject.teachers.set(data['teachers'])
        subject.save()
        return JsonResponse({'id': subject.id, 'subject_name': subject.subject_name})
    return JsonResponse({'error': 'Invalid request method'})


def get_subjects(request):
    subjects = Subject.objects.all().values('id', 'subject_name')
    return JsonResponse(list(subjects), safe=False)


@csrf_exempt
def add_classroom(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        classroom = Classroom.objects.create(
            classroom_number=data['classroom_number'],
            classroom_type=data['classroom_type']
        )
        return JsonResponse({'id': classroom.id, 'classroom_number': classroom.classroom_number,
                             'classroom_type': classroom.classroom_type})
    return JsonResponse({'error': 'Invalid request method'})


@csrf_exempt
def edit_classroom(request, classroom_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        classroom = Classroom.objects.get(id=classroom_id)
        classroom.classroom_number = data.get('classroom_number', classroom.classroom_number)
        classroom.classroom_type = data.get('classroom_type', classroom.classroom_type)
        classroom.save()
        return JsonResponse({'id': classroom.id, 'classroom_number': classroom.classroom_number,
                             'classroom_type': classroom.classroom_type})
    return JsonResponse({'error': 'Invalid request method'})


def get_classrooms(request):
    classrooms = Classroom.objects.all().values('id', 'classroom_number', 'classroom_type')
    return JsonResponse(list(classrooms), safe=False)


# Новые функции для работы с расписанием

def find_free_slots(teacher, group, day_of_week, lesson_time):
    """
    Находит свободные слоты для проведения занятия.
    """
    # --- Проверяем, занята ли группа ---
    group_busy = Schedule.objects.filter(
        groups=group,
        day_of_week=day_of_week,
        lesson_time=lesson_time
    ).exists()

    # Карта типов аудиторий
    classroom_type_map = {
        'practical': 'computer',
        'lecture': 'lecture'
    }
    required_classroom_type = classroom_type_map.get(teacher.lesson_type)

    # Ищем существующую урок преподавателя в это время
    teacher_existing = Schedule.objects.filter(
        teacher=teacher,
        day_of_week=day_of_week,
        lesson_time=lesson_time
    ).first()

    if teacher_existing:
        # Учитель уже ведёт урок → можно добавить ещё группу в ту же аудиторию
        available_classrooms = Classroom.objects.filter(id=teacher_existing.classroom_id)
        teacher_free = True
    else:
        # Ищем свободные аудитории
        busy_classrooms = Schedule.objects.filter(
            day_of_week=day_of_week,
            lesson_time=lesson_time
        ).values_list('classroom_id', flat=True)

        available_classrooms = Classroom.objects.filter(
            classroom_type=required_classroom_type
        ).exclude(id__in=busy_classrooms)

        teacher_free = False  # Учитель всегда свободен по логике

    group_free = not group_busy
    can_schedule = teacher_free and group_free and available_classrooms.exists()

    return {
        'can_schedule': can_schedule,
        'teacher_free': teacher_free,
        'group_free': group_free,
        'available_classrooms': available_classrooms,
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


# View-функция для использования через HTTP запрос
@csrf_exempt
def check_availability(request):
    """
    API endpoint для проверки доступности слотов.
    Принимает teacher_id и group_id, возвращает недельное расписание.
    """
    if request.method == 'GET':
        teacher_id = request.GET.get('teacher_id')
        group_id = request.GET.get('group_id')

        if not teacher_id or not group_id:
            return JsonResponse({'error': 'teacher_id and group_id are required'}, status=400)

        try:
            teacher = Teacher.objects.get(id=teacher_id)
            group = Groups.objects.get(id=group_id)

            availability = get_weekly_availability(teacher, group)
            return JsonResponse(availability, safe=False)
        except (Teacher.DoesNotExist, Groups.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def create_schedule(request):
    """
    Создает новую запись в расписании с проверкой конфликтов.
    """
    if request.method == 'POST':
        data = json.loads(request.body)

        teacher_id = data.get('teacher_id')
        group_id = data.get('group_id')
        classroom_id = data.get('classroom_id')
        day_of_week = data.get('day_of_week')
        lesson_time = data.get('lesson_time')
        subject_id = data.get('subject_id')

        try:
            teacher = Teacher.objects.get(id=teacher_id)
            group = Groups.objects.get(id=group_id)
            classroom = Classroom.objects.get(id=classroom_id)
            subject = Subject.objects.get(id=subject_id)

            # Проверка 1: Группа уже занята?
            if Schedule.objects.filter(groups=group, day_of_week=day_of_week, lesson_time=lesson_time).exists():
                return JsonResponse({
                    'error': 'Эта группа уже занята в это время'
                }, status=400)

            # Проверка 2: Учитель ведет урок в ДРУГОЙ аудитории?
            teacher_schedule = Schedule.objects.filter(
                teacher=teacher,
                day_of_week=day_of_week,
                lesson_time=lesson_time
            ).first()

            if teacher_schedule and teacher_schedule.classroom_id != classroom_id:
                return JsonResponse({
                    'error': f'Преподаватель уже ведет урок в это время в аудитории {teacher_schedule.classroom.classroom_number}'
                }, status=400)

            # Проверка 3: Аудитория занята ДРУГИМ преподавателем?
            classroom_schedule = Schedule.objects.filter(
                classroom=classroom,
                day_of_week=day_of_week,
                lesson_time=lesson_time
            ).exclude(teacher=teacher)

            if classroom_schedule.exists():
                return JsonResponse({
                    'error': 'Эта аудитория занята другим преподавателем'
                }, status=400)

            # Проверка 4: Тип аудитории соответствует типу урока?
            classroom_type_map = {
                'practical': 'computer',
                'lecture': 'lecture'
            }
            required_type = classroom_type_map.get(teacher.lesson_type)

            if classroom.classroom_type != required_type:
                return JsonResponse({
                    'error': f'Неподходящий тип аудитории. Требуется: {required_type}'
                }, status=400)

            # Все проверки пройдены - создаем расписание
            schedule = Schedule.objects.create(
                teacher=teacher,
                classroom=classroom,
                subject=subject,
                day_of_week=day_of_week,
                lesson_time=lesson_time
            )
            schedule.groups.add(group)

            return JsonResponse({
                'id': schedule.id,
                'message': 'Расписание успешно создано',
                'teacher': teacher.fullname,
                'group': group.group_name,
                'classroom': classroom.classroom_number,
                'day': day_of_week,
                'time': lesson_time
            })

        except (Teacher.DoesNotExist, Groups.DoesNotExist, Classroom.DoesNotExist, Subject.DoesNotExist) as e:
            return JsonResponse({'error': f'Объект не найден: {str(e)}'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def add_group_to_schedule(request, schedule_id):
    """
    Добавляет группу к существующему расписанию (для нескольких групп в одной аудитории).
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        group_id = data.get('group_id')

        try:
            schedule = Schedule.objects.get(id=schedule_id)
            group = Groups.objects.get(id=group_id)

            # Проверка: группа уже занята в это время?
            if Schedule.objects.filter(
                    groups=group,
                    day_of_week=schedule.day_of_week,
                    lesson_time=schedule.lesson_time
            ).exists():
                return JsonResponse({
                    'error': 'Эта группа уже занята в это время'
                }, status=400)

            # Добавляем группу
            schedule.groups.add(group)

            return JsonResponse({
                'message': f'Группа {group.group_name} добавлена к расписанию',
                'schedule_id': schedule.id,
                'groups': [g.group_name for g in schedule.groups.all()]
            })

        except (Schedule.DoesNotExist, Groups.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
