from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.decorators import login_required
from crm import models
from django.db.utils import IntegrityError
from crm import forms
from django import conf
import json,os,time
from django.views.decorators.csrf import csrf_exempt
from students import permissions

# Create your views here.


@login_required
def class_couser(request):
    """我的课程"""
    student_obj = request.user.stu_account #学生对象，单条记录
    class_grade_objs = student_obj.class_grades.all() # 与某学生相关的所有班级
    # study_course_objs = models.StudyRecord.objects.filter(student=student_obj) # 学习记录对象，多条记录
    # study_course_obj = study_course_objs.first()
    # course_record_obj = study_course_obj.course_record # 课程对象，单条记录
    # class_grade_obj = course_record_obj.class_grade # 班级对象，单条记录
    # print("course_record_obj:",type(course_record_obj))
    return render(request, "students/class_couser.html",locals())


@login_required
def study_record_view(request,class_grade_id):
    """单个学生下关于某课程的所有学习记录"""
    student_obj = request.user.stu_account
    study_record_objs = models.StudyRecord.objects.filter( # 某个学生报的某个班级的所有学习记录
        student=student_obj,
        course_record__class_grade_id = class_grade_id)
    # print("study_course_objs:",study_record_objs)
    # print("study_course_objs_type:",type(study_record_objs))

    return render(request,"students/study_record_view.html",locals())


@permissions.check_permission
@csrf_exempt
@login_required
def study_homework_details(request,study_record_obj_id):
    """作业详情"""
    study_record_obj = models.StudyRecord.objects.get(id = study_record_obj_id)
    file_dicts = {'file': {}}

    # 文件上传相关
    # status_dict = {"status": True, "err_msg": ""}
    homework_data_dir = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/" \
        .format(base_dir=conf.settings.CRM_FILE_HOMEWORK_DIR,
                class_id=study_record_obj.course_record.class_grade_id,
                course_record_id=study_record_obj.course_record_id,
                studyrecord_id=study_record_obj.student_id
                )

    if not os.path.isdir(homework_data_dir): # 是否存在该文件夹，存在直接写入文件夹中，不存在则创建，
        os.makedirs(homework_data_dir, exist_ok = True)



    file_obj = request.FILES.get('file')
    if request.method == "POST":
        if file_obj:
            if len(os.listdir(homework_data_dir)) < 1:
                with open(os.path.join(homework_data_dir, file_obj.name), "wb") as f:
                    for chunk in file_obj.chunks():
                        f.write(chunk)

            else:
                # return HttpResponse(json.dumps({'status': False, 'err_msg': '作业只能上传一个，请以".zip"或".rar"打包上传！'}))
                file_dicts['error'] = "只能上传一个作业，请以'.zip'或'.rar'打包后再上传！"

            for file_name in os.listdir(homework_data_dir):
                file_path = "%s/%s" % (homework_data_dir, file_name)
                modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(file_path).st_mtime))

                file_dicts['file'][file_name] = {'size': os.stat(file_path).st_size,
                                                 'ctime': modify_time}

            return HttpResponse(json.dumps(file_dicts))

    for file_name in os.listdir(homework_data_dir):
        file_path = "%s/%s" % (homework_data_dir, file_name)
        modify_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(os.stat(file_path).st_mtime))

        file_dicts['file'][file_name] = {'size': os.stat(file_path).st_size,
                                          'ctime': modify_time}

    # print("file_dicts:",file_dicts)


    # if request.method == "POST":
    #     return redirect("/students/study_record_view/%s/"%study_record_obj.course_record.class_grade_id)

    return  render(request,'students/study_homework_details.html',locals())



@login_required
def delete_homework_file(request,study_record_obj_id):
    """ajax动态删除作业"""
    study_record_obj = models.StudyRecord.objects.get(id=study_record_obj_id)
    response = {}
    if request.method == "POST":
        homework_data_dir = "{base_dir}/{class_id}/{course_record_id}/{studyrecord_id}/" \
            .format(base_dir=conf.settings.CRM_FILE_HOMEWORK_DIR,
                    class_id=study_record_obj.course_record.class_grade_id,
                    course_record_id=study_record_obj.course_record_id,
                    studyrecord_id=study_record_obj.student_id
                    )

        filename = request.POST.get('filename')
        file_abs = "%s/%s" % (homework_data_dir, filename.strip())
        if os.path.isfile(file_abs):
            os.remove(file_abs)
            response['msg'] = "file '%s' got deleted " % filename
        else:
            response["error"] = "file '%s' does not exist on server" % filename
    else:
        response['error'] = "only supoort POST method..."
    return HttpResponse(json.dumps(response))


