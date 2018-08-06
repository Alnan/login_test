"""
    动态生成form表单，动态展示各表中单个角色内的详细表单信息
"""


from django.forms import ModelForm


def create_dynamic_model_form(admin_class,form_add=False):
    """
    根据传入admin_class，获取不同表信息，动态生成对应的modelform表单
    form_add: False 默认是修改的表单,True时为添加
    """

    class Meta:
        model = admin_class.model
        #所有字段都展示
        fields = "__all__"
        if not form_add:#change，如果是修改操作，不能修改的信息应该设置成只读项
            exclude = admin_class.readonly_fields
            admin_class.form_add = False #这是因为自始至终admin_class实例都是同一个,
            # 这里修改属性为True是为了避免上一次添加调用将其改为了True
        else: #add，如果是添加操作，没有只读项这回事
            admin_class.form_add = True#返回给前端，判断是修改数据还是新增数据


    def __new__(cls,*args,**kwargs):
        """
        Django中ModelForm表单生成都是在ModelForm的__new__方法中生成
        要给通过ModelForm生成的表单添加自定义标签样式，需要在此方法中处理
        base_fields----: 表单中所有信息，（[('名称'，对象)，('名称'，对象)...]）OrderedDict([('name', <django.forms.fields.CharField object at 0x0000000004ACA4A8>), ('contact_type', <django.forms.fields.TypedChoiceField object at 0x0000000004ACA5C0>)....
        """
        for field_name in cls.base_fields: #获得每个字段的名称
            # print('base_fields----:',cls.base_fields)
            field_obj =cls.base_fields[field_name] #获取该字段名对应的对象
            # 给该字段对象更新/增加class属性
            field_obj.widget.attrs.update({'class':'form-control'})

        # 最后务必调用父类__new__方法
        return ModelForm.__new__(cls)



    dynamic_form = type("DynamicModelForm",(ModelForm,),{'Meta':Meta,'__new__':__new__})
    """
    type("DynamicModelForm",(ModelForm,)
    DynamicModelForm:类名
    ModelForm：继承的类
    {'Meta':Meta}:DynamicModelForm类的成员，可以是类、方法或其他
    """
    return dynamic_form #dynamic_form：是类，返回dynamic_form类  <class 'django.forms.widgets.DynamicModelForm'>