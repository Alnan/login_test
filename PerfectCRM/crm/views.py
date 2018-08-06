from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from crm import models
from django.db.utils import IntegrityError
from crm import forms
import datetime
import json,os,time
from django.views.decorators.csrf import csrf_exempt
from django import conf



# Create your views here.
@login_required()
def dashboard(request):
    """crm下的首页"""
    return render(request,"crm/dashboard.html")



# 销售部分
@login_required
def stu_enrollment(request):
    """学员报名"""

    customers = models.CustomerInfo.objects.all()
    class_lists = models.ClassList.objects.all()
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        class_grade_id = request.POST.get("class_grade_id")
        # enrollment_obj = models.StudentEnrollment.objects.create(
        #     customer_id=customer_id,
        #     class_grade_id=class_grade_id,
        #     consultant_id=request.user.userprofile.id,  # 当前顾问
        #
        # )
        try:
            enrollment_obj = models.StudentEnrollment.objects.create(
                customer_id=customer_id,
                class_grade_id=class_grade_id,
                consultant_id=request.user.userprofile.id,#当前顾问

            )

        except IntegrityError as e:  # unique错误，报错则表示已经生成过报名表
            enrollment_obj = models.StudentEnrollment.objects.get(customer_id=customer_id,
                                                                  class_grade_id=class_grade_id, )
            if enrollment_obj.contract_agreed:
                return redirect("/crm/stu_enrollment/%s/contract_audit/" % enrollment_obj.id)

        enrollment_link = "http://localhost:8000/crm/enrollment/%s/" % enrollment_obj.id

    return render(request, 'crm/stu_enrollment.html', locals())


def get_uploaded_fileinfo(file_dicts, enrollment_upload_dir):
    """获取上传文件的信息"""
    for file_name in os.listdir(enrollment_upload_dir):
        file_path = "%s/%s" % (enrollment_upload_dir, file_name)
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(file_path).st_mtime))

        file_dicts['file'][file_name] = {'size': os.path.getsize(file_path) / 1000,
                                          'ctime': modify_time}


def enrollment(request,enrollment_id):
    """学员在线报名表地址"""

    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)

    if enrollment_obj.contract_approved:
        return HttpResponse("报名合同已通过审核，欢迎您加入 xxx IT教育！")


    if enrollment_obj.contract_agreed:
        return HttpResponse("报名合同正在审核中....")

    if request.method == "POST":
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer, data=request.POST)
        if customer_form.is_valid():  # 审核通过
            # print(customer_form.cleaned_data)
            customer_form.save()
            enrollment_obj.contract_agreed = True
            enrollment_obj.contract_signed_date = datetime.datetime.now()
            enrollment_obj.save()

        return HttpResponse("您已成功提交报名信息,请等待审核通过.....")

    else:
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)

    # 列出已上传文件
    file_dicts = {'file': {}}
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_id)
    if os.path.isdir(enrollment_upload_dir):
        get_uploaded_fileinfo(file_dicts, enrollment_upload_dir)

    return render(request, "crm/enrollment.html",locals())

def enrollment_delete(request,enrollment_id):
    """ajax动态删除上传的文件"""
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
    response = {}
    if request.method == "POST":
        enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_id)

        filename = request.POST.get('filename')
        file_abs = "%s/%s" % (enrollment_upload_dir, filename.strip())
        if os.path.isfile(file_abs):
            os.remove(file_abs)
            response['msg'] = "file '%s' got deleted " % filename
        else:
            response["error"] = "file '%s' does not exist on server" % filename
    else:
        response['error'] = "only supoort POST method..."
    return HttpResponse(json.dumps(response))


@csrf_exempt
def enrollment_fileupload(request, enrollment_id):
    """学员报名时上传证件"""
    file_dicts = {'file': {}}
    enrollment_upload_dir = os.path.join(conf.settings.CRM_FILE_UPLOAD_DIR, enrollment_id)
    if not os.path.isdir(enrollment_upload_dir):  # 是否存在该文件夹，存在直接写入文件夹中，不存在则创建，
        os.mkdir(enrollment_upload_dir)

    file_obj = request.FILES.get('file')
    if request.method == "POST":
        if file_obj:
            if len(os.listdir(enrollment_upload_dir)) < 3:  # 上传文件最多3个，第一次上传时已有文件数量为0，以此类推
                with open(os.path.join(enrollment_upload_dir, file_obj.name), "wb") as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)

            else:
                file_dicts['error'] = "至多只能上传3个文件"

            get_uploaded_fileinfo(file_dicts, enrollment_upload_dir)
            return HttpResponse(json.dumps(file_dicts))
    return HttpResponse(json.dumps(file_dicts))




@login_required
def contract_audit(request,enrollment_id):
    """
    倒数第二步，审核
    """
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)
    audit_status = {'status':"false"}
    if request.GET.get('status'):# ajax操作，获取前端数据，再返回数据给前端
        audit_status['status'] = "true"
        # print("11111111111")
        enrollment_obj.contract_agreed = False #审核驳回，设置contract_agreed为false，返回链接再发给学员重新填写
        enrollment_obj.save()
        return HttpResponse(json.dumps(audit_status))
    if request.method == "POST": # 表单提交
        # print(request.POST)
        enrollment_form = forms.EnrollmentForm(instance=enrollment_obj,data=request.POST)
        if enrollment_form.is_valid():
            enrollment_form.save()
            # stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]
            # stu_obj.class_grades.add(enrollment_obj.class_grade_id)
            # stu_obj.save()
            # enrollment_obj.customer.status = 1
            # enrollment_obj.customer.save()
            enrollment_obj.contract_approved_date = datetime.datetime.now()
            enrollment_obj.contract_approved = True
            enrollment_obj.save()
            return redirect("/crm/stu_Payment/%s"%enrollment_obj.id)
    else:
        customer_form = forms.CustomerForm(instance=enrollment_obj.customer)
        enrollment_form = forms.EnrollmentForm(instance=enrollment_obj)
    return render(request,"crm/contract_audit.html", locals())



@login_required
def stu_Payment(request,enrollment_id):
    """最后一步，学员报名缴费"""
    enrollment_obj = models.StudentEnrollment.objects.get(id=enrollment_id)

    if request.method == "POST":
        # enrollment = request.POST.get('enrollment')
        # consultant = request.POST.get('consultant')
        payment_type = request.POST.get('payment_type')
        amount = request.POST.get('amount')
        # print('POST:',enrollment,consultant,payment_type,amount)
        if int(amount) < 500:
            error_msg = "缴费金额不能低于500元"
            payment_form = forms.PaymentRecordForm()
            return render(request, "crm/stu_payment.html", locals())

        payment_obj = models.PaymentRecord.objects.create( # 生成缴费记录
                                            enrollment = enrollment_obj,
                                            consultant = enrollment_obj.consultant,
                                            payment_type = payment_type,
                                            amount = amount,
                                            )
        # 报名成功，在学员表中生成学员数据
        stu_obj = models.Student.objects.get_or_create(customer=enrollment_obj.customer)[0]
        stu_obj.class_grades.add(enrollment_obj.class_grade_id)
        stu_obj.save()
        enrollment_obj.customer.status = 1
        enrollment_obj.customer.save()
        return redirect("/crm/stu_enrollment_list/")
        # return HttpResponse("ok")

    payment_form = forms.PaymentRecordForm() # get方法
    return render(request, "crm/stu_payment.html", locals())










@login_required
def stu_enrollment_list(request):
    """学员报名记录表"""
    stu_enrollment_list = models.StudentEnrollment.objects.all().order_by('-id')

    return render(request,'crm/stu_enrollment_list.html',{"stu_enrollment_list":stu_enrollment_list})

# @login_required
# def stu_list(request):
#     """已报名学员记录"""
#     stu_lists = models.Student.objects.all().order_by('-id')
#     return render(request,'crm/stu_list.html',{"stu_lists":stu_lists})



# 讲师部分
@login_required
def class_manage(request):
    """班级管理"""
    teacher_id = request.user.id
    # print("id:",teacher_id)
    cls_objs = models.ClassList.objects.filter(teachers=teacher_id)
    # print("cls_objs:",cls_objs)

    return render(request, "crm/teachers/class_manage.html", {"cls_objs":cls_objs})

@login_required
def course_record(request,cls_id):
    """各班级上课记录表"""
    cls_obj = models.ClassList.objects.filter(id = cls_id)[0]#班级
    # course_record_obj = cls_obj.courserecord_set.all().first() #对应单条上课记录,
    # course_record_form = forms.CourseRecordForm(instance=course_record_obj)
    course_record_objs = cls_obj.courserecord_set.all() #反向查找对应上课记录，querySet集合

    return render(request, "crm/teachers/course_record.html", locals())

@login_required
def course_record_change(request,course_record_id):
    """查看/修改某节课记录数据"""
    course_record_obj = models.CourseRecord.objects.get(id = course_record_id)
    # print("course_record_obj_type:",type(course_record_obj))
    # print("course_record_obj:",course_record_obj)

    if request.method == "POST":
        course_record_form = forms.CourseRecordForm(instance=course_record_obj,data=request.POST)
        if course_record_form.is_valid():
            course_record_form.save()
            return redirect("/crm/teachers/course_record/%s"%course_record_obj.class_grade_id)
    course_record_form = forms.CourseRecordForm(instance=course_record_obj)

    return render(request,"crm/teachers/course_record_change.html",locals())


@login_required
def course_record_delete(request,course_record_id):
    """删除当前课程记录"""
    course_record_obj = models.CourseRecord.objects.get(id=course_record_id)
    if request.method == "POST":
        course_record_obj.delete()
        return redirect("/crm/teachers/course_record/%s"%course_record_obj.class_grade_id)

    return render(request,"crm/teachers/course_record_delete.html",locals())


@login_required
def course_record_add(request):
    """新增课程记录"""
    # course_record_obj = models.CourseRecord.objects.all()
    if request.method =="POST":
        course_record_cls_grade = request.POST.get("class_grade")# 打印结果为：3

        course_record_form = forms.CourseRecordForm(data=request.POST)
        if course_record_form.is_valid():
            course_record_form.save()
            return redirect("/crm/teachers/course_record/%s"%course_record_cls_grade)
    course_record_form = forms.CourseRecordForm()
    return render(request,"crm/teachers/course_record_add.html",locals())


@login_required
def bulk_create_StudyRecord(request,course_record_id):
    """批量生成学员学习记录数据"""
    course_record_obj = models.CourseRecord.objects.get(id = course_record_id) #课程记录表的当前对象
    cls_objs = course_record_obj.class_grade # 一对多，正向查，获取班级表中与当前课程相关的班级对象
    stu_objs = cls_objs.student_set.all() # 多对多关系，反向查(需.all（）)，获取学生表属于当前相关班级的所有成员。是个queryset集合
    for stu_obj in stu_objs: # 批量创建学习记录数据
        models.StudyRecord.objects.get_or_create( #get_or_create:获取到的是元组类型，不是对象
            #每个study_record_list都是一个元组,元组内是对象，study_record_list[0]是对象，存有所需所有数据
            #print('study_record_obj[0]:',study_record_list[0])：结果：study_record_obj[0]: python全栈开发(5)期第(1)节 李四 0
            # print("study_record_list[]", type(study_record_list[0]))：study_record_list[]: <class 'crm.models.StudyRecord'>
            course_record = course_record_obj,
            student = stu_obj
        )
    # 取出与当前上课记录相关的所有学生学习记录数据
    study_record_objs = models.StudyRecord.objects.all().filter(course_record = course_record_obj)
    list_display = ['show_status', 'score']# 用于前端自定义标签，获取choise选择中的内容值，非数字值


    return render(request,"crm/teachers/bulk_create_StudyRecord.html",locals())


@login_required
def bulk_delete_studyrecord(request,course_record_id):
    """批量删除学员学习记录数据"""
    course_record_obj = models.CourseRecord.objects.get(id=course_record_id)  # 课程记录表的当前对象
    study_record_objs = course_record_obj.studyrecord_set.all()
    if request.method == "POST":
        for study_record_obj in study_record_objs:
            study_record_obj.delete()

        return redirect("/crm/teachers/course_record/%s/"%course_record_obj.class_grade_id)

    return render(request,"crm/teachers/bulk_delete_studyrecord.html",locals())





@login_required
def study_record_change(request,study_record_id):
    """查看/修改学生学习记录表"""
    study_record_obj = models.StudyRecord.objects.get(id = study_record_id)

    if request.method == "POST":
        study_record_form = forms.StudyRecordForm(instance=study_record_obj,data=request.POST)
        if study_record_form.is_valid():
            study_record_form.save()
            return redirect("/crm/teachers/bulk_create_StudyRecord/%s"%study_record_obj.course_record.id)

    study_record_form = forms.StudyRecordForm(instance=study_record_obj)
    return render(request,'crm/teachers/study_record_change.html',locals())


@login_required
def study_record_delete(request,study_record_id):
    """删除单条学习记录"""
    study_record_obj = models.StudyRecord.objects.get(id=study_record_id)
    if request.method == "POST":
        study_record_obj.delete()
        return redirect("/crm/teachers/bulk_create_StudyRecord/%s"%study_record_obj.course_record.id)

    return render(request,"crm/teachers/study_record_delete.html",locals())




@login_required
def homework_manage(request,course_record_obj_id):
    """作业管理"""
    course_record_obj = models.CourseRecord.objects.get(id = course_record_obj_id)
    study_record_objs = models.StudyRecord.objects.filter(course_record_id=course_record_obj_id)

    return render(request,"crm/teachers/homework_manage.html",locals())


@login_required
def homework_manage_details(request,study_record_obj_id):
    """作业详情管理"""
    study_record_obj = models.StudyRecord.objects.get(id = study_record_obj_id)
    print(study_record_obj)
    homework_data_dir = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/" \
        .format(base_dir=conf.settings.CRM_FILE_HOMEWORK_DIR,
                class_id=study_record_obj.course_record.class_grade_id,
                course_record_id=study_record_obj.course_record_id,
                studyrecord_id=study_record_obj.student_id
                )
    if os.path.isdir(homework_data_dir):
        file_lists = []
        for file_name in os.listdir(homework_data_dir):
            file_path = "%s/%s" % (homework_data_dir, file_name)
            modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(file_path).st_mtime))
            file_lists.append([file_name, os.stat(file_path).st_size, modify_time])

    if request.method == "POST":

        study_record_score = request.POST.get("score")
        print('study_record_score:',study_record_score)
        study_record_note = request.POST.get("note")
        study_record_obj_update = models.StudyRecord.objects.filter(id=study_record_obj_id).update(
            score = study_record_score,
            note = study_record_note
        )
        return redirect("/crm/teachers/homework_manage/%s"%study_record_obj.course_record_id)


    return render(request,"crm/teachers/homework_manage_details.html",locals())