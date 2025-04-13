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
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer, EnrollmentSerializer, StudentSerializer

# Course Views


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CourseForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('courses:course_list')
        # If form is invalid, return context with errors
        context = self.get_context_data()
        context['form'] = form
        return render(request, self.template_name, context)

class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        lessons = course.lessons.all()

        enrolled_students = Student.objects.filter(
            user=self.request.user,
            enrolled_courses=course
        )
        student = enrolled_students.first()
        total = lessons.count()
        completed = student.completed_lessons.filter(
            course=course).count() if student else 0
        progress = int((completed / total) * 100) if total > 0 else 0

        context.update({
            'lessons': lessons,
            'student': student,
            'progress': progress,
        })
        return context

class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
        

@method_decorator(login_required, name='dispatch')
class CourseCreateView(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('courses:course_list')

    def form_valid(self, form):
        messages.success(self.request, "Course created successfully!")
        return super().form_valid(form)


# @login_required
# def course_list(request):
#     courses = Course.objects.all()
#     form = CourseForm()

#     if request.method == "POST":
#         form = CourseForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Course created successfully!")
#             return redirect('courses:course_list')

#     return render(request, 'courses/course_list.html', {'courses': courses, 'form': form})


# @login_required
# # def course_detail(request, course_id):
# #     course = get_object_or_404(Course, id=course_id)
# #     lessons = course.lessons.all()
# #     return render(request, 'courses/course_detail.html', {'course': course, 'lessons': lessons})
# def course_detail(request, course_id):
#     course = get_object_or_404(Course, id=course_id)

#     # Get all students enrolled in this course by this user
#     enrolled_students = Student.objects.filter(
#         user=request.user, enrolled_courses=course)

#     # Safely get the current student for this user and course
#     # Use first() to avoid MultipleObjectsReturned
#     student = enrolled_students.first()

#     # Get all lessons for this course
#     lessons = course.lessons.all()

#     # Calculate progress
#     total = lessons.count()
#     completed = student.completed_lessons.filter(
#         course=course).count() if student else 0
#     progress = int((completed / total) * 100) if total > 0 else 0

#     return render(request, 'courses/course_detail.html', {
#         'course': course,
#         'lessons': lessons,
#         'student': student,
#         'progress': progress,
#     })


# @login_required
# def course_create(request):
#     if request.method == "POST":
#         form = CourseForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Course created successfully!")
#             return redirect('courses:course_list')
#     else:
#         form = CourseForm()
#     return render(request, 'courses/course_form.html', {'form': form})


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

            # Get or create student for current user
            student, created = Student.objects.get_or_create(
                user=request.user,
                email=student_email,
                defaults={'name': student_name}
            )

            # Update name if needed
            if student.name != student_name:
                student.name = student_name
                student.save()

            # ✅ Enroll only if not already enrolled
            if course not in student.enrolled_courses.all():
                student.enrolled_courses.add(course)

            return render(request, 'courses/enrollment_success.html', {
                'student': student,
                'course': course
            })
    else:
        form = CourseEnrollmentForm()

    return render(request, 'courses/enroll_student.html', {'form': form})

class EnrollStudentAPI(APIView):
    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        course_id = serializer.validated_data['course_id']
        student_email = serializer.validated_data['email']
        custom_name = serializer.validated_data.get('name')  # Get the custom name if provided

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {"error": "Course not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Determine the name to use
        name_to_use = custom_name or request.user.get_full_name() or request.user.username

        # Get or create student with user association
        student, created = Student.objects.get_or_create(
            user=request.user,
            email=student_email,
            defaults={'name': name_to_use}  # Use the determined name
        )

        # Update name if custom name was provided and different from existing
        if custom_name and student.name != custom_name:
            student.name = custom_name
            student.save()

        # Check if already enrolled
        if student.enrolled_courses.filter(id=course.id).exists():
            return Response(
                {"message": f"{student_email} is already enrolled in this course"},
                status=status.HTTP_200_OK
            )

        # Enroll the student
        student.enrolled_courses.add(course)
        
        return Response(
            {
                'message': 'Enrollment successful',
                'student': StudentSerializer(student).data,
                'course': CourseSerializer(course).data
            },
            status=status.HTTP_201_CREATED
        )

# def enroll_student(request):
#     if request.method == "POST":
#         form = CourseEnrollmentForm(request.POST)
#         if form.is_valid():
#             student_name = form.cleaned_data['student_name']
#             student_email = form.cleaned_data['student_email']
#             course = form.cleaned_data['course']

#             # Try to find an existing student for this user
#             student_qs = Student.objects.filter(user=request.user)

#             if student_qs.exists():
#                 # If multiple exist, pick the latest or first
#                 student = student_qs.first()  # or use .last() or filter by email
#                 # Update student details
#                 student.name = student_name
#                 student.email = student_email
#                 student.save()
#             else:
#                 # Create a new student record
#                 student = Student.objects.create(
#                     user=request.user,
#                     name=student_name,
#                     email=student_email
#                 )

#             # Enroll student in course
#             student.enrolled_courses.add(course)

#             return render(request, 'courses/enrollment_success.html', {
#                 'student': student,
#                 'course': course
#             })
#     else:
#         form = CourseEnrollmentForm()

#     return render(request, 'courses/enroll_student.html', {'form': form})


# def enroll_student(request):
#     if request.method == "POST":
#         form = CourseEnrollmentForm(request.POST)
#         if form.is_valid():
#             student_name = form.cleaned_data['student_name']
#             student_email = form.cleaned_data['student_email']
#             course = form.cleaned_data['course']

#             # ✅ Get or create student by email
#             student, created = Student.objects.get_or_create(email=student_email)

#             # ✅ If student already enrolled in any course, show error
#             if student.enrolled_courses.exists():
#                 messages.error(request, "This email is already enrolled in a course.")
#                 return redirect('course_list')

#             # ✅ Set student name (if new or updating)
#             student.name = student_name
#             student.save()

#             # ✅ Add selected course
#             student.enrolled_courses.add(course)
#             # ✅ Success message & show confirmation page
#             messages.success(request, "You have successfully enrolled in {course.title}")
#             return render(request, 'courses/enrollment_success.html', {'student': student, 'course': course})
#     else:
#         form = CourseEnrollmentForm()

#     return render(request, 'courses/enroll_student.html', {'form': form})


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
