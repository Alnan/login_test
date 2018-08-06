from django.template import Library
from django.utils.safestring import mark_safe




register = Library()

@register.simple_tag
def get_obj_field_val(study_record_obj,field):
    ele = ""
    column_data = getattr(study_record_obj, "get_%s_display" % field)()
    # column_data = getattr(study_record_obj, field)
    td_ele = "<td>%s</td>" % column_data
    ele += td_ele
    return mark_safe(ele)



