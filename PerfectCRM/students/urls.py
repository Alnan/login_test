

from django.urls import path , re_path
from students import views

urlpatterns = [

    re_path(r'^class_couser/$', views.class_couser, name="class_couser"),
    re_path(r'^study_record_view/(\d+)/$', views.study_record_view, name="study_record_view"),
    re_path(r'^study_homework_details/(\d+)/$', views.study_homework_details, name="study_homework_details"),
    re_path(r'^study_homework_details/(\d+)/delete/$', views.delete_homework_file, name="delete_homework_file"),
]
