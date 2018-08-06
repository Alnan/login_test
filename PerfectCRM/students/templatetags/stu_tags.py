from django.template import Library
from django.utils.safestring import mark_safe
from crm import models
from django.db.models import Sum


register = Library()


@register.simple_tag
def  get_score(student_obj,class_grade_obj):
    """获取学员关于某班级所有的学习成绩总和"""
    # study_course_objs = models.StudyRecord.objects.filter(student=student_obj) # 属于某个学生的所有课程

    study_course_objs = models.StudyRecord.objects.filter(student=student_obj,course_record__class_grade_id = class_grade_obj.id) # 某个学生报的某个班级的所有学习记录

    return study_course_objs.aggregate(Sum('score'))
