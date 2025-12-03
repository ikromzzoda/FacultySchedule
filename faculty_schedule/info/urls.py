from django.urls import path
from . import views

urlpatterns = [
    path('teachers/create/', views.create_teacher, name='create_teacher'),
    path('teachers/edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('teachers/', views.get_teachers, name='get_teachers'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/edit/<int:group_id>/', views.edit_group, name='edit_group'),
    path('groups/', views.get_groups, name='get_groups'),
    path('subjects/add/', views.add_subject, name='add_subject'),
    path('subjects/edit/<int:subject_id>/', views.edit_subject, name='edit_subject'),
    path('subjects/', views.get_subjects, name='get_subjects'),
    path('classrooms/add/', views.add_classroom, name='add_classroom'),
    path('classrooms/edit/<int:classroom_id>/', views.edit_classroom, name='edit_classroom'),
    path('classrooms/', views.get_classrooms, name='get_classrooms'),
    path('availability/check/', views.check_availability, name='check_availability'),
    path('schedule/create/', views.create_schedule, name='create_schedule'),
    path('schedule/<int:schedule_id>/add-group/', views.add_group_to_schedule, name='add_group_to_schedule'),
]