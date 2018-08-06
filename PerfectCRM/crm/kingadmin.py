from kingadmin.sites import site
from crm import models
from kingadmin.admin_base import BaseKingAdmin
from django.shortcuts import render,redirect,HttpResponse


print("crm kingadmin ...........")

class CustomerAdmin(BaseKingAdmin):
    list_display = ['id','name','source','contact_type','contact','consultant','consult_content','status','date']
    list_filter = ['source','consultant','status','date']
    search_fields = ['contact','consultant__name']

    readonly_fields = [ 'consultant','id_num']
    filter_horizontal = ['consult_courses', ]

    actions = ['change_status', ]

    def change_status(self, request, querysets):
        # print("kingadmin action: TEST……", self, request, querysets)
        print("kingadmin action: 更改选中数据状态！")
        # querysets.update(status=1)


class StudentEnrollmentAdmin(BaseKingAdmin):
    list_display = ['id','customer','source','contact_type','contact','consultant','consult_content','status','date']

class CourseRecordAdmin(BaseKingAdmin):
    list_display = ['class_grade','day_num','teacher','title','has_homework','date']
    list_filter = ['class_grade', 'teacher',]


    def initialize_studyrecords(self, request, queryset):#方式二，具有事务特性，错误则回滚数据
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")

        new_obj_list = []
        for student_obj in queryset[0].class_grade.student_set.all():
            new_obj_list.append(models.StudyRecord(
                student = student_obj,
                course_record = queryset[0],
            ))

        try:
            models.StudyRecord.objects.bulk_create(new_obj_list) # bulk_create:Django提供批量处理，具事务特性，错误则回滚

        except Exception as e:#studyrecord设置了联合唯一，创建同样数据会报错
            return HttpResponse("批量初始化学习记录失败，请检查该节课是否已经有对应的学习记录")
        return redirect("/kingadmin/crm/studyrecord/?course_record__id__exact=%s"%queryset[0].id )

    initialize_studyrecords.display_name = "初始化本节所有学员的上课记录"

    def bulk_delete_studyrecords(self, request, queryset):#批量删除学生学习记录，不具事务特性
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")
        for student_obj in queryset[0].class_grade.student_set.all():
            study_obj = models.StudyRecord.objects.filter(student=student_obj,course_record=queryset[0])
            study_obj.delete()

        return redirect("/admin/crm/studyrecord/" )

    actions = ['initialize_studyrecords','bulk_delete_studyrecords' ]



class StudyRecordAdmin(BaseKingAdmin):
    list_display = ['course_record','student','score','show_status','date']
    list_filter = ['course_record','student','score']


site.register(models.CustomerInfo,CustomerAdmin)
site.register(models.Role)
site.register(models.Menus)
site.register(models.Course)
site.register(models.ClassList)
# site.register(models.CourseRecord,CourseRecordAdmin)
site.register(models.CourseRecord,CourseRecordAdmin)
site.register(models.StudyRecord,StudyRecordAdmin)
site.register(models.UserProfile)
site.register(models.StudentEnrollment)
site.register(models.PaymentRecord)
site.register(models.ContractTemplate)