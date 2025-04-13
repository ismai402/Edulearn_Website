from django.urls import path
from . import views
from .views import register, user_login, user_logout, profile
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from .views import CourseListView, CourseDetailView, CourseCreateView

app_name = 'courses'

urlpatterns = [
    # Course URLs
    # path('', views.course_list, name='course_list'),
    # path('courses/', views.course_list, name='courses'),  # ✅ Use namespace
    # path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    # path('create/', views.course_create, name='course_create'),
    path('', CourseListView.as_view(), name='course_list'),
    path('courses/', CourseListView.as_view(), name='courses'),
    path('courses/<int:course_id>/', CourseDetailView.as_view(), name='course_detail'),
    path('create/', CourseCreateView.as_view(), name='course_create'),

    path('update/<int:course_id>/', views.course_update, name='course_update'),
    path('delete/<int:course_id>/', views.course_delete, name='course_delete'),

    # Lesson URLs
    path('courses/lesson/create/', views.lesson_create, name='lesson_create'),
    path('lesson/<int:lesson_id>/update/',
         views.lesson_update, name='lesson_update'),
    path('lesson/<int:lesson_id>/delete/',
         views.lesson_delete, name='lesson_delete'),

    # 🔹 Fix: Include course_id in the URL pattern
    path('<int:course_id>/students/', views.view_students, name='view_students'),

    # Enrollment
    path('enroll/', views.enroll_student, name='enroll_student'),

    # Contact Page
    path('contact/', views.contact, name='contact'),
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Add Profile URL
    path('profile/', views.profile, name='profile'),


    # Password change view
    path('password_change/', auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    # Password reset views
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='courses/password_reset.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='courses/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='courses/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='courses/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
