from django.contrib import admin
from django.utils.html import format_html
from .models import Teacher, Groups, Classroom, Schedule, Users, Subject
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

admin.site.unregister(Group)
@admin.register(Users)
class UserAdmin(BaseUserAdmin):
    model = Users
    list_display = ("id", "username", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")

    # Поля в деталях пользователя
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )

    # Поля для создания нового пользователя
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    search_fields = ("username",)
    ordering = ("id",)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Админ-панель для предметов"""

    list_display = ['subject_name']
    search_fields = ['subject_name']
    ordering = ['subject_name']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Админ-панель для преподавателей"""

    list_display = ['fullname', 'lesson_type_badge', 'get_subjects', 'schedule_count']
    list_filter = ['lesson_type']
    search_fields = ['fullname']
    ordering = ['fullname']
    filter_horizontal = ['subjects'] 

    def get_subjects(self, obj):
        """Получение списка предметов"""
        return ", ".join([s.subject_name for s in obj.subjects.all()])
    
    get_subjects.short_description = 'Предметы'


    def lesson_type_badge(self, obj):
        """Цветная метка типа занятия"""
        colors = {
            'practical': '#28a745',
            'lecture': '#007bff'
        }
        color = colors.get(obj.lesson_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_lesson_type_display()
        )

    lesson_type_badge.short_description = 'Тип занятия'

    def schedule_count(self, obj):
        """Количество занятий"""
        return obj.schedule_set.count()

    schedule_count.short_description = 'Кол-во занятий'


@admin.register(Groups)
class GroupAdmin(admin.ModelAdmin):
    """Админ-панель для групп"""

    list_display = ['group_name', 'group_type', 'group_course', 'schedule_count']
    list_filter = ['group_type', 'group_course']
    search_fields = ['group_name']
    ordering = ['group_course', 'group_name']

    fieldsets = (
        ('Основная информация', {
            'fields': ('group_name',)
        }),
        ('Параметры', {
            'fields': ('group_type', 'group_course')
        }),
    )

    def schedule_count(self, obj):
        """Количество занятий"""
        return obj.schedule_set.count()

    schedule_count.short_description = 'Кол-во занятий'


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """Админ-панель для аудиторий"""

    list_display = ['classroom_number', 'classroom_type_badge', 'utilization'] #'capacity',
    list_filter = ['classroom_type']
    search_fields = ['classroom_number']
    ordering = ['classroom_number']

    fieldsets = (
        ('Основная информация', {
            'fields': ('classroom_number', 'classroom_type')
        }),
        # ('Характеристики', {
        #     'fields': ('capacity',)
        # }),
    )

    def classroom_type_badge(self, obj):
        """Цветная метка типа аудитории"""
        colors = {
            'computer': '#17a2b8',
            'lecture': '#ffc107'
        }
        color = colors.get(obj.classroom_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_classroom_type_display()
        )

    classroom_type_badge.short_description = 'Тип аудитории'

    def utilization(self, obj):
        """Загруженность аудитории"""
        total_slots = 6 * 11  # 7 дней × 11 временных слотов
        used_slots = obj.schedule_set.count()
        if total_slots > 0:
            percentage = (used_slots / total_slots) * 100
            return f"{used_slots}/{total_slots} ({percentage:.1f}%)"
        return "0/66 (0%)"

    utilization.short_description = 'Загруженность'


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Админ-панель для расписания"""

    def get_groups(self, obj):
        return ", ".join([g.group_name for g in obj.groups.all()])

    list_display = [
        'get_day_time',
        'teacher',
        'get_groups',
        'classroom'
    ] #'status_badge'
    list_filter = [
        'day_of_week',
        'lesson_time',
        'teacher__lesson_type',
        'classroom__classroom_type'
    ]
    search_fields = [
        'teacher__fullname',
        'classroom__classroom_number'
    ]
    ordering = ['day_of_week', 'lesson_time']

    autocomplete_fields = ['teacher', 'groups', 'classroom']

    fieldsets = (
        ('Время и место', {
            'fields': ('day_of_week', 'lesson_time', 'classroom')
        }),
        ('Участники', {
            'fields': ('teacher', 'groups')
        }),
    )

    def get_day_time(self, obj):
        """Форматированное отображение дня и времени"""
        return format_html(
            '<strong>{}</strong><br/><small>{}</small>',
            obj.get_day_of_week_display(),
            obj.get_lesson_time_display()
        )

    get_day_time.short_description = 'День и время'


    # def status_badge(self, obj):
    #     """Статус занятия (совпадение типов)"""
    #     teacher_type = obj.teacher.lesson_type
    #     classroom_type = obj.classroom.classroom_type

    #     # Проверяем соответствие типов
    #     match = (
    #             (teacher_type == 'practical' and classroom_type == 'computer') or
    #             (teacher_type == 'lecture' and classroom_type == 'lecture')
    #     )
    #
    #     if match:
    #         return format_html(
    #             '<span style="color: green;">✓ Соответствует</span>'
    #         )
    #     else:
    #         return format_html(
    #             '<span style="color: red;">✗ Не соответствует</span>'
    #         )
    #
    # status_badge.short_description = 'Соответствие типов'
    #
    #
    # def save_model(self, request, obj, form, change):
    #     """Валидация при сохранении"""
    #     # Проверяем соответствие типов
    #     teacher_type = obj.teacher.lesson_type
    #     classroom_type = obj.classroom.classroom_type
    #
    #     type_match = {
    #         'practical': 'computer',
    #         'lecture': 'lecture'
    #     }
    #
    #     if type_match.get(teacher_type) != classroom_type:
    #         from django.contrib import messages
    #         messages.warning(
    #             request,
    #             f'Внимание: Тип занятия преподавателя ({teacher_type}) '
    #             f'не соответствует типу аудитории ({classroom_type})'
    #         )
    #
    #     super().save_model(request, obj, form, change)



# Настройка заголовков админ-панели
admin.site.site_header = 'Управление расписанием'
admin.site.site_title = 'Расписание'
admin.site.index_title = 'Панель управления'