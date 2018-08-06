from django.shortcuts import render
# import json


class BaseKingAdmin(object):
    def __init__(self):

        if self.actions:
            self.actions.extend(self.default_actions)
        else:
            self.actions = self.default_actions



    list_display = []
    list_filter = []
    search_fields = []
    list_per_page = 8
    readonly_fields = []
    filter_horizontal = []

    default_actions = ['delete_selected_objs']
    actions = []

    def delete_selected_objs(self, request, querysets):
        warning_action = "action：这是删除操作，请谨慎处理！"
        # print("action：这是删除操作，请谨慎处理！")
        status_action = 1

        return render(request, 'kingadmin/table_obj_delete.html', {'admin_class': self,
                                                                   'objs': querysets,
                                                                   'warning_action': warning_action,
                                                                   'status_action': status_action
                                                                   })
        # print("action：这是删除操作，请谨慎处理！")

        # querysets_ids = json.dumps([i.id for i in querysets])
        # return render(request, 'kingadmin/table_obj_delete.html', {'admin_class': self,
        #                                                            'objs': querysets,
        #                                                            'querysets_ids': querysets_ids
        #                                                            })