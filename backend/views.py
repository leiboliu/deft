import math

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils.safestring import mark_safe
from django.views.generic import View

from backend.models import Project, DataSet, DataFile, TaggedEntity, Tag, PretrainedModel
from utils.automated_annotation import auto_annotate
from utils.data_backend import LocalFileSystemBackend, convert_tags_to_html
from utils.file_conversion import write_results, export_deid_text


class AjaxGetEntities(LoginRequiredMixin,View):
    def get(self, request):
        user = request.user
        doc_id = request.GET.get('doc_id')

        if doc_id == "":
            entity_list = []
        else:
            # entities = TaggedEntity.objects.filter(doc__id=doc_id, annotator=user.username)
            data_file = DataFile.objects.get(id=doc_id)
            with open(data_file.get_path(), 'r', encoding="utf-8") as f:
                # get raw content
                doc_content = f.read()

            entities = TaggedEntity.objects.filter(doc__id=doc_id)
            for entity in entities:
                entity.text = doc_content[entity.start_index : entity.end_index]
            entity_list = [entity.to_list() for entity in entities]

        return JsonResponse({'data': entity_list})


class AjaxGetLists(LoginRequiredMixin, View):

    def get(self, request):

        usr = request.user

        t = request.GET.get('list_type')

        if t == 'p':
            project_list = []

            if usr.is_superuser:
                pl = Project.objects.all()
            else:
                pl = Project.objects.filter(assigned_member__member_id=usr.id)
            # pl = Project.objects.all()

            for p in pl:
                project = p.to_list()
                # status_by_user = ProjectStatus.objects.filter(project_id=project['id'], annotator=usr.id)
                # if len(status_by_user) != 0:
                #     project['status'] = status_by_user[0].get_status_display()

                project_list.append(project)

            # project_list = [p.to_list() for p in pl]

            return JsonResponse({'data': project_list})
        elif t == 'd':
            data_list = []

            pid = request.GET.get('pid')
            if usr.is_superuser:
                dl = DataSet.objects.filter(project_id=pid)
            else:
                dl = DataSet.objects.filter(project__id=pid, type='ANNO').filter(project__assigned_member__member_id=usr.id)
            # dl = DataSet.objects.all()

            for d in dl:
                dataset = d.to_list()
                # status_by_user = DataSetStatus.objects.filter(dataset_id=dataset['id'], annotator=usr.id)
                # if len(status_by_user) != 0:
                #     dataset['status'] = status_by_user[0].get_status_display()

                datafiles = DataFile.objects.filter(dataset=d)
                num_n = 0
                num_w = 0
                num_c = 0
                for file in datafiles:
                    # try:
                    #     datafile_status_by_user = DocumentStatus.objects.get(doc_id=file.id, annotator=usr.id)
                    #     file.status = datafile_status_by_user.status
                    #     if file.status == 'WIP':
                    #         num_w += 1
                    #     elif file.status == 'C':
                    #         num_c += 1
                    #     else:
                    #         num_n += 1
                    # except DocumentStatus.DoesNotExist:
                    #     num_n += 1
                    if file.status == 'WIP':
                        num_w += 1
                    elif file.status == 'C':
                        num_c += 1
                    else:
                        num_n += 1

                dataset['num_na'] = num_n
                dataset['num_wip'] = num_w
                dataset['num_complete'] = num_c

                data_list.append(dataset)

            return JsonResponse({'data': data_list})
        elif t == 'df':
            doc_list = []
            filter_completed = request.GET.get('filter_completed')
            d = request.GET.get('d')
            # if filter_completed == 'true':
            #     dl = DataFile.objects.filter(dataset__id=d, status__in=['NA', 'WIP'])
            # else:
            #     dl = DataFile.objects.filter(dataset__id=d)
            dl = DataFile.objects.filter(dataset__id=d)
            # total = dl.count()

            # document_status_list_by_user = DocumentStatus.objects.filter(annotator=usr.id)
            for d in dl:
                doc = d.to_list()
                # status_by_user = DocumentStatus.objects.filter(doc_id=doc['id'], annotator=usr.id)
                # for status_by_user in document_status_list_by_user:
                #     if status_by_user.doc_id == doc['id']:
                #         doc['status'] = status_by_user.get_status_display()
                #         doc['status_code'] = status_by_user.status
                # if len(status_by_user) != 0:
                #     doc['status'] = status_by_user[0].get_status_display()
                #     doc['status_code'] = status_by_user[0].status
                if filter_completed == 'true' and doc['status_code'] == 'C':
                    continue

                doc_list.append(doc)
            total = len(doc_list)

            _start = request.GET.get('start')
            _length = request.GET.get('length')

            if _start and _length:
                start = int(_start)
                length = int(_length)
                page = math.ceil(start / length) + 1
                per_page = length

                doc_list = doc_list[start:start + length]



            # data = [df.to_list() for df in dl]

            return JsonResponse({
                'data': doc_list,
                'page': page,
                'per_page': per_page,
                'recordsTotal': total,
                'recordsFiltered': total,
            })

class AjaxGetFile(LoginRequiredMixin, View):
    def get(self, request):
        # project_id = request.GET.get('project_id')
        # dataset_id = request.GET.get('dataset_id')
        doc_id = request.GET.get('file_id')
        usr = request.user

        file = DataFile.objects.filter(id=doc_id)[0]
        project_id = file.dataset.project.id

        # get file status by user
        # file_status_by_user = DocumentStatus.objects.filter(doc_id=doc_id, annotator=usr.id)
        # if len(file_status_by_user) != 0:
        #     file.status = file_status_by_user[0].status

        with open(file.get_path(), 'r', encoding="utf-8") as f:
            # get raw content
            doc_content = f.read()

            if file.status == 'NA':
                tags = auto_annotate(project_id, doc_id, doc_content)
            else:
                tags = TaggedEntity.objects.filter(doc__id=doc_id).order_by('start_index')
                # tags = TaggedEntity.objects.filter(doc__id=doc_id, annotator=usr.username).order_by('start_index')


            doc_content = convert_tags_to_html(doc_content, tags);

            doc = mark_safe(doc_content)

        return JsonResponse({
            'id': doc_id,
            'doc': doc,
            'status': file.status,
        })


class AjaxEditComplete(LoginRequiredMixin, View):
    def get(self, request):
        usr = request.user

        file_id = request.GET.get('file_id')
        check_status = request.GET.get('check_status')

        doc = DataFile.objects.filter(id=file_id)[0]
        # get file status by user
        # file_status_by_user = DocumentStatus.objects.filter(doc_id=file_id, annotator=usr.id)
        # if len(file_status_by_user) != 0:
        #     file_status_by_user = file_status_by_user[0]
        #     doc.status = file_status_by_user.status
        # else:
        #     file_status_by_user = DocumentStatus(doc_id=file_id, annotator=usr.id, status=doc.status)

        if check_status == 'true':
            # file_status_by_user.status = 'WIP'
            doc.status = 'WIP'
        else:
            # if doc.status == 'NA':
            #     # save the model trained results for current user
            #     curent_model = PretrainedModel.objects.filter(project__id=doc.dataset.project.id, status='C')
            #     tagged_entity_by_model = []
            #     if len(curent_model) != 0:
            #         curent_model = curent_model[0]
            #         tagged_entity_by_model = TaggedEntity.objects.filter(doc__id=doc.id, annotator=curent_model.name)
            #
            #     if len(tagged_entity_by_model) != 0:
            #         # copy predited entities to current users.
            #         for tagged_entity in tagged_entity_by_model:
            #             tagged_entity.pk = None
            #             tagged_entity.annotator = usr.username
            #             tagged_entity.save()
            # set status as complete
            # file_status_by_user.status = 'C'
            doc.status = 'C'


        # file_status_by_user.save()
        doc.save()

        dataset = doc.dataset

        d_new_stat = 'C'

        dl = DataFile.objects.filter(dataset=dataset)

        for df in dl:
            # file_status_by_user = DocumentStatus.objects.filter(doc_id=df.id, annotator=usr.id)
            # if len(file_status_by_user) != 0:
            #     df.status = file_status_by_user[0].status

            if df.status != 'C':
                d_new_stat = 'WIP'
                break

        if dataset.status != d_new_stat:
            dataset.status = d_new_stat
            dataset.save()


        # dataset_status_by_user = DataSetStatus.objects.filter(dataset_id=dataset.id, annotator=usr.id)
        # if len(dataset_status_by_user) != 0:
        #     dataset_status_by_user = dataset_status_by_user[0]
        #     dataset.status = dataset_status_by_user.status
        # else:
        #     dataset_status_by_user = DataSetStatus(dataset_id=dataset.id, annotator=usr.id, status=dataset.status)
        #     dataset_status_by_user.save()


        # if dataset.status != d_new_stat:
        #     dataset_status_by_user.status = d_new_stat
        #     dataset_status_by_user.save(update_fields=['status'])

        if dataset.status == 'C':

            project = dataset.project

            dsl = DataSet.objects.filter(project=project)

            p_new_stat = 'C'

            for ds in dsl:
                # dataset_status_by_user = DataSetStatus.objects.filter(dataset_id=ds.id, annotator=usr.id)
                # if len(dataset_status_by_user) != 0:
                #     ds.status = dataset_status_by_user[0].status

                if ds.status != 'C':
                    p_new_stat = 'WIP'
                    break

            if project.status != p_new_stat:
                project.status = p_new_stat
                project.save()

            # project_status_by_user = ProjectStatus.objects.filter(project_id=doc.dataset.project.id, annotator=usr.id)
            # if len(project_status_by_user) != 0:
            #     project_status_by_user = project_status_by_user[0]
            #     project.status = project_status_by_user.status
            # else:
            #     project_status_by_user = ProjectStatus(project_id=doc.dataset.project.id, annotator=usr.id, status=project.status)
            #     project_status_by_user.save()

            # if project.status != p_new_stat:
            #     project_status_by_user.status = p_new_stat
            #     project_status_by_user.save(update_fields=['status'])

        return JsonResponse(
            doc.to_list()
        )


class AjaxSaveView(LoginRequiredMixin, View):

    def post(self, request):
        usr = request.user
        _ = self
        doc_id = request.POST.get('doc_id')

        try:
            doc = DataFile.objects.get(id=doc_id)
        except ObjectDoesNotExist:
            return JsonResponse(
                {'status': f'error no doc found'}
            )

        entity = request.POST.get('ops_entity[entity]')
        # entity_color = request.POST.get('ops_entity[entity_color]')

        currentTag = Tag.objects.get(name=entity) #, colour=entity_color)

        start_index = request.POST.get('ops_entity[start]')
        end_index = request.POST.get('ops_entity[end]')
        # text = request.POST.get('ops_entity[text]')
        text = ''
        annotator = request.POST.get('ops_entity[annotator]')

        action = request.POST.get('action')

        # file_status_by_user = DocumentStatus.objects.filter(doc_id=doc_id, annotator=usr.id)
        # if len(file_status_by_user) != 0:
        #     doc.status = file_status_by_user[0].status
        # else:
        #     file_status_by_user = DocumentStatus(doc_id=doc_id, annotator=usr.id, status=doc.status)

        d_status = doc.status



        # if d_status == 'NA':
        #     # copy machine predicted entities for current users for this doc
        #     curent_model = PretrainedModel.objects.filter(project__id=doc.dataset.project.id, status='C')
        #     tagged_entity_by_model = []
        #     if len(curent_model) != 0:
        #         curent_model = curent_model[0]
        #         tagged_entity_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=curent_model.name)
        #
        #     if len(tagged_entity_by_model) != 0:
        #         # copy predited entities to current users.
        #         for tagged_entity in tagged_entity_by_model:
        #             tagged_entity.pk = None
        #             tagged_entity.annotator = annotator
        #             tagged_entity.save()


        if action == 'add':
            # update or create
            TaggedEntity.objects.update_or_create(doc=doc,
                                                  start_index=start_index,
                                                  end_index=end_index,
                                                  annotator=annotator,
                                                  defaults={
                                                      'tag': currentTag,
                                                      'text': text,
                                                  })
        else:
            # delete
            # TaggedEntity.objects.filter(doc=doc,
            #                             start_index=start_index,
            #                             end_index=end_index, annotator=annotator).delete()
            TaggedEntity.objects.filter(doc=doc,
                                        start_index=start_index,
                                        end_index=end_index).delete()


        # d_path = doc.get_path(w=True)
        # d_status = doc.status

        # with open(d_path, 'w') as f:
        #     f.write(request.POST.get('new_data'))

        if d_status == 'NA':
            doc.status = 'WIP'
            dataset = doc.dataset
            if dataset.status != 'WIP':
                dataset.status = 'WIP'
                dataset.save()
            project = dataset.project
            if project.status != 'WIP':
                project.status = 'WIP'
                project.save()

            # file_status_by_user.status = 'WIP'
            # file_status_by_user.save()

        # file_status_by_user.save()
        doc.save()

        return JsonResponse(
            {
                'doc': doc.to_list(),
            }
        )


class AjaxOpsView(LoginRequiredMixin, View):

    def get(self, request):
        pid = request.GET.get('project_id')
        t = request.GET.get('type')

        project = Project.objects.filter(id=pid).first()

        if project:
            lb = LocalFileSystemBackend()

            if t == "import" and project.status in ['ND', 'DC', 'DA']:
                lb.import_data_files(project)
                project.status = 'DA'
                project.save()
                return JsonResponse(
                    {'status': f'successfully imported data for project with id {pid}'}
                )
            elif t == 'create' and project.status in ['ND', 'DC', 'DA']:

                lb.create_project_dir(project)
                print("trying to create dataset dirs")
                lb.create_dataset_dirs(project)
                project.status = 'DC'
                project.save()

                return JsonResponse(
                    {'status': f'successfully created directory for project with id {pid}'}
                )
            return JsonResponse(
                {'status': f'no operation available for project with id {pid}'}
            )
        return JsonResponse(
            {'status': f'no project with id {pid}'}
        )


class AjaxExportView(LoginRequiredMixin, View):

    def get(self, request):
        _ = self
        t = request.GET.get('type')

        if t == 'f':
            fid = request.GET.get('id')
            f = DataFile.objects.filter(id=fid).first()
            write_results(f)

            return JsonResponse(
                {'status': f'successfully exported file with id {fid}'}
            )

        if t == 'ds':
            dsid = request.GET.get('id')

            dl = DataFile.objects.filter(dataset__id=dsid)

            for f in dl:
                write_results(f)

            return JsonResponse(
                {'status': f'successfully exported dataset with id {dsid}'}
            )

class AjaxExportDeidView(LoginRequiredMixin, View):

    def get(self, request):
        _ = self
        t = request.GET.get('type')

        if t == 'f':
            fid = request.GET.get('id')
            f = DataFile.objects.filter(id=fid).first()
            export_deid_text(f)

            return JsonResponse(
                {'status': f'successfully exported file with id {fid}'}
            )

        if t == 'ds':
            dsid = request.GET.get('id')

            dl = DataFile.objects.filter(dataset__id=dsid)

            for f in dl:
                export_deid_text(f)

            return JsonResponse(
                {'status': f'successfully exported dataset with id {dsid}'}
            )

class AjaxImportView(LoginRequiredMixin, View):

    def get(self, request):
        pid = request.GET.get('project_id')
        d_id = request.GET.get('dataset_id')

        project = Project.objects.filter(id=pid).first()
        dataset = DataSet.objects.filter(id=d_id).first()

        if project and dataset:
            lb = LocalFileSystemBackend()
            lb.import_data_files(project, [dataset])

            dataset.status = 'DA'
            dataset.save()

            if project.status in ['ND', 'DC']:
                project.status = 'DA'
                project.save()

            return JsonResponse(
                {'status': f'successfully imported dataset with id {d_id}'}
            )

        return JsonResponse(
            {'status': f'error'}
        )

