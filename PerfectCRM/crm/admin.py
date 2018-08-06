
from django.shortcuts import render,redirect,HttpResponse
from crm import models

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from crm.models import UserProfile


class UserCreationForm(forms.ModelForm):
    """
    创建用户时调用
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = UserProfile
        fields = ('email', 'name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"]) #把明文 根据算法改成密文
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    修改/更新用户信息表单
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = UserProfile
        fields = ('email', 'password', 'name', 'is_active', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserProfileAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'name', 'is_superuser')
    list_filter = ('is_superuser',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name','stu_account')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','role','user_permissions','groups')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ("role",'user_permissions','groups')#manytomany，多选select框







class CourseRecordAdmin(admin.ModelAdmin):
    list_display = ['class_grade','day_num','teacher','title','has_homework','date']
    list_filter = ['class_grade', 'teacher','day_num','has_homework']

    """
    def initialize_studyrecords(self, request, queryset):#方式一，无事务特性，不回滚
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")

        for student_obj in queryset[0].class_grade.student_set.all():
            models.StudyRecord.objects.get_or_create( # 自定义批量删除，无事务特性，不回滚
                students = student_obj,
                course_record = queryset[0] ,

            )

        return redirect("/admin/crm/studyrecord/?course_record__id__exact=%s"%queryset[0].id )
    """
    def initialize_studyrecords(self, request, queryset):#方式二，批量生成学习记录。具有事务特性，错误则回滚数据
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")

        new_obj_list = []
        for student_obj in queryset[0].class_grade.student_set.all():
            # print("student_obj:",student_obj)
            new_obj_list.append(models.StudyRecord(
                student = student_obj,
                course_record = queryset[0] ,
            ))

        try:

            models.StudyRecord.objects.bulk_create(new_obj_list) # bulk_create:Django提供批量处理，具事务特性，错误则回滚

        except Exception as e:#studyrecord设置了联合唯一，创建同样数据会报错
            return HttpResponse("批量初始化学习记录失败，请检查该节课是否已经有对应的学习记录")
        return redirect("/admin/crm/studyrecord/?course_record__id__exact=%s"%queryset[0].id )

    initialize_studyrecords.short_description = "初始化本节所有学员的上课记录"

    def bulk_delete_studyrecords(self, request, queryset):#批量删除学生学习记录，不具事务特性
        if len(queryset) > 1:
            return HttpResponse("只能选择一个班级")
        for student_obj in queryset[0].class_grade.student_set.all():
            study_obj = models.StudyRecord.objects.filter(student=student_obj,course_record=queryset[0])
            study_obj.delete()


        return redirect("/admin/crm/studyrecord/" )

    bulk_delete_studyrecords.short_description = "批量删除本节所有学员的上课记录"

    actions = ['initialize_studyrecords','bulk_delete_studyrecords']



class StudyRecorddAdmin(admin.ModelAdmin):
    list_display = ['course_record','student','show_status','score','date']
    list_filter = ['course_record', 'student', 'score']
    # list_editable = ['show_status','score']



admin.site.register(models.CustomerInfo)
admin.site.register(models.CustomerFollowUp)
admin.site.register(models.ClassList)
admin.site.register(models.Course)
admin.site.register(models.Role)
admin.site.register(models.Menus)
admin.site.register(models.CourseRecord,CourseRecordAdmin)
admin.site.register(models.StudyRecord,StudyRecorddAdmin)
admin.site.register(models.Student)
admin.site.register(models.UserProfile,UserProfileAdmin)
admin.site.register(models.Branch)
admin.site.register(models.ContractTemplate)
admin.site.register(models.StudentEnrollment)
admin.site.register(models.PaymentRecord)