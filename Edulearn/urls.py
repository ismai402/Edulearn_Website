from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from courses.views import enroll_student  # ✅ Import view_students

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('courses.urls')),
    # ✅ Add course_id to enroll
    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
