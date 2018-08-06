from kingadmin.sites import site
from students import models
from kingadmin.admin_base import BaseKingAdmin
print('students kingadmin ............')

class TestAdmin(BaseKingAdmin):
    list_display = ['name']

site.register(models.Test,TestAdmin)