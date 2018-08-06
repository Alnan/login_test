"""PerfectCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path,re_path
from crm import views


urlpatterns = [
    # 首页
    re_path(r'^$', views.dashboard, name="sales_dashboard"),
    # 销售
    re_path(r'^stu_enrollment/$', views.stu_enrollment,name="stu_enrollment"),
    re_path(r'^enrollment/(\d+)/$', views.enrollment,name="enrollment"),
    re_path(r'^enrollment/(\d+)/fileupload/$', views.enrollment_fileupload, name="enrollment_fileupload"),
    re_path(r'^enrollment/(\d+)/delete/$', views.enrollment_delete, name="enrollment_delete"),
    re_path(r'^stu_enrollment/(\d+)/contract_audit/$', views.contract_audit, name="contract_audit"),
    re_path(r'^stu_Payment/(\d+)/$', views.stu_Payment, name="stu_Payment"),
    re_path(r'^stu_enrollment_list/$', views.stu_enrollment_list,name="stu_enrollment_list"),

    # teachers
    re_path(r'^teachers/class_manage/$', views.class_manage,name="class_manage"),
    re_path(r'^teachers/course_record/(\d+)/$', views.course_record,name="course_record"),
    re_path(r'^teachers/course_record/(\d+)/change/$', views.course_record_change,name="course_record_change"),
    re_path(r'^teachers/course_record/(\d+)/delete/$', views.course_record_delete,name="course_record_delete"),
    re_path(r'^teachers/course_record/add/$', views.course_record_add,name="course_record_add"),

    re_path(r'^teachers/bulk_create_StudyRecord/(\d+)/$', views.bulk_create_StudyRecord,name="bulk_create_StudyRecord"),
    re_path(r'^teachers/bulk_delete_studyrecord/(\d+)/$', views.bulk_delete_studyrecord,name="bulk_delete_studyrecord"),
    re_path(r'^teachers/study_record/(\d+)/change/$', views.study_record_change,name="study_record_change"),
    re_path(r'^teachers/study_record/(\d+)/delete/$', views.study_record_delete,name="study_record_delete"),

    re_path(r'^teachers/homework_manage/(\d+)/$', views.homework_manage,name="homework_manage"),
    re_path(r'^teachers/homework_manage_details/(\d+)/$', views.homework_manage_details,name="homework_manage_details"),





    # re_path(r'^stu_list/$', views.stu_list,name="stu_list"),
]
