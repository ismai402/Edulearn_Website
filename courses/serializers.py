from rest_framework import serializers
from .models import Course, Lesson, Student

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_url', 'completion_status']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'enrolled_courses']
        extra_kwargs = {
            'enrolled_courses': {'read_only': True}
        }

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    students = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'duration', 'thumbnail', 'created_at', 'lessons', 'students']

    def get_students(self, obj):
        return StudentSerializer(obj.students.all(), many=True).data

class EnrollmentSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    course_id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False, allow_blank=True)  # Add this line

    def validate_course_id(self, value):
        if not Course.objects.filter(id=value).exists():
            raise serializers.ValidationError("Course does not exist")
        return value