
from django.urls import path

from utils.ajax_api import dtable_project_list
from .views import AjaxGetLists, \
    AjaxOpsView, AjaxSaveView, AjaxExportView, AjaxImportView, AjaxGetFile, AjaxEditComplete, AjaxGetEntities, \
    AjaxExportDeidView

urlpatterns = [
    path('dt_project_list/', dtable_project_list, name='dt_project_list'),
    path('get_list/', AjaxGetLists.as_view(), name='get_list_view'),
    path('get_entities_by_doc/', AjaxGetEntities.as_view(), name='get_entities_by_doc_view'),
    path('ajax_ops', AjaxOpsView.as_view(), name='ajax_ops_view'),
    path('ajax_save', AjaxSaveView.as_view(), name='ajax_save_view'),
    path('ajax_export', AjaxExportView.as_view(), name='ajax_export_view'),
    path('ajax_export_deid', AjaxExportDeidView.as_view(), name='ajax_export_deid_view'),
    path('ajax_import', AjaxImportView.as_view(), name='ajax_import_view'),
    path('ajax_get_file', AjaxGetFile.as_view(), name='ajax_get_file_view'),

    path('ajax_edit_complete', AjaxEditComplete.as_view(), name='ajax_edit_complete_view'),

]