from .models import Student
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Course, Lesson, Student
from .forms import CourseForm, LessonForm, CourseEnrollmentForm, UserUpdateForm
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

# Course Views


# @login_required
def course_list(request):
    courses = Course.objects.all()
    form = CourseForm()

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('courses:course_list')

    return render(request, 'courses/course_list.html', {'courses': courses, 'form': form})


@login_required
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)
#     lessons = course.lessons.all()
#     return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    student = request.user.student
    total = lessons.count()
    completed = student.completed_lessons.filter(course=course).count()
    percent = int((completed / total) * 100) if total > 0 else 0
    context = {
        'course': course,
        'lessons': lessons,
        'student': student,
        'progress_percent': percent,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('courses:course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('courses:course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})


@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('courses:course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

# Lesson Views


@login_required
def lesson_create(request):
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('courses:course_list')
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form})


@login_required
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('courses:course_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form})


@login_required
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('courses:course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

# Enrollment Views


@login_required
def enroll_student(request):
    if request.method == "POST":
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            student_name = form.cleaned_data['student_name']
            student_email = form.cleaned_data['student_email']
            course = form.cleaned_data['course']
            student, created = Student.objects.get_or_create(email=student_email)
            student.name = student_name
            student.save()
            student.enrolled_courses.add(course)
            return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
    else:
        form = CourseEnrollmentForm()
    return render(request, 'courses/enroll_student.html', {'form': form})


@login_required
def view_students(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()
    return render(request, 'courses/view_students.html', {'course_id': course_id, 'students': students, 'course': course})

# Authentication Views


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('courses:login')
        else:
            messages.error(
                request, 'There was an error with your registration. Please check the form.')
    else:
        form = UserCreationForm()
    return render(request, 'courses/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'courses/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')

# Profile View


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('courses:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'courses/profile.html', {'form': form})

# Miscellaneous Views


def contact(request):
    return render(request, 'courses/contact.html')


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

    def form_valid(self, form):
        messages.success(
            self.request, 'Your password was successfully updated!')
        return super().form_valid(form)
