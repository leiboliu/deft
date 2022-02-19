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
from utils.file_conversion import write_results


class AjaxGetEntities(LoginRequiredMixin,View):
    def get(self, request):
        user = request.user
        doc_id = request.GET.get('doc_id')

        if doc_id == "":
            entity_list = []
        else:
            entities = TaggedEntity.objects.filter(doc__id=doc_id, annotator=user.username)
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
                project_list.append(p.to_list())

            project_list = [p.to_list() for p in pl]

            return JsonResponse({'data': project_list})
        elif t == 'd':
            data_list = []

            pid = request.GET.get('pid')
            if usr.is_superuser:
                dl = DataSet.objects.all()
            else:
                dl = DataSet.objects.filter(project__id=pid).filter(project__assigned_member__member_id=usr.id)
            # dl = DataSet.objects.all()

            for d in dl:
                data_list.append(d.to_list())

            return JsonResponse({'data': data_list})
        elif t == 'df':
            # doc_list = []
            filter_completed = request.GET.get('filter_completed')
            d = request.GET.get('d')
            if filter_completed == 'true':
                dl = DataFile.objects.filter(dataset__id=d, status__in=['NA', 'WIP'])
            else:
                dl = DataFile.objects.filter(dataset__id=d)
            total = dl.count()

            _start = request.GET.get('start')
            _length = request.GET.get('length')

            if _start and _length:
                start = int(_start)
                length = int(_length)
                page = math.ceil(start / length) + 1
                per_page = length

                dl = dl[start:start + length]

            # for d in dl:
            #     doc_list.append(d.to_list())
            data = [df.to_list() for df in dl]


            return JsonResponse({
                'data': data,
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

        with open(file.get_path(), 'r') as f:
            # get raw content
            doc_content = f.read()

            if file.status == 'NA':
                tags = auto_annotate(project_id, doc_id, doc_content)
            else:
                tags = TaggedEntity.objects.filter(doc__id=doc_id, annotator=usr.username).order_by('start_index')


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

        if check_status == 'true':
            doc.status = 'WIP'
        else:
            if doc.status == 'NA':
                # save the model trained results for current user
                curent_model = PretrainedModel.objects.filter(project__id=doc.dataset.project.id, status='C')
                tagged_entity_by_model = []
                if len(curent_model) != 0:
                    curent_model = curent_model[0]
                    tagged_entity_by_model = TaggedEntity.objects.filter(doc__id=doc.id, annotator=curent_model.name)

                if len(tagged_entity_by_model) != 0:
                    # copy predited entities to current users.
                    for tagged_entity in tagged_entity_by_model:
                        tagged_entity.pk = None
                        tagged_entity.annotator = usr.username
                        tagged_entity.save()
            # set status as complete
            doc.status = 'C'


        doc.save()

        dataset = doc.dataset

        d_new_stat = 'C'

        dl = DataFile.objects.filter(dataset=dataset)

        for df in dl:
            if df.status != 'C':
                d_new_stat = 'WIP'

        if dataset.status != d_new_stat:
            dataset.status = d_new_stat
            dataset.save(update_fields=['status'])

        if dataset.status == 'C':

            project = dataset.project

            dsl = DataSet.objects.filter(project=project)

            p_new_stat = 'C'

            for ds in dsl:
                if ds.status != 'C':
                    p_new_stat = project.status

            if project.status != p_new_stat:
                project.status = p_new_stat
                project.save(update_fields=['status'])

        return JsonResponse(
            doc.to_list()
        )


class AjaxSaveView(LoginRequiredMixin, View):

    def post(self, request):

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
        text = request.POST.get('ops_entity[text]')
        annotator = request.POST.get('ops_entity[annotator]')

        action = request.POST.get('action')
        d_status = doc.status

        if d_status == 'NA':
            # copy machine predicted entities for current users for this doc
            curent_model = PretrainedModel.objects.filter(project__id=doc.dataset.project.id, status='C')
            tagged_entity_by_model = []
            if len(curent_model) != 0:
                curent_model = curent_model[0]
                tagged_entity_by_model = TaggedEntity.objects.filter(doc__id=doc_id, annotator=curent_model.name)

            if len(tagged_entity_by_model) != 0:
                # copy predited entities to current users.
                for tagged_entity in tagged_entity_by_model:
                    tagged_entity.pk = None
                    tagged_entity.annotator = annotator
                    tagged_entity.save()


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
            TaggedEntity.objects.filter(doc=doc,
                                        start_index=start_index,
                                        end_index=end_index, annotator=annotator).delete()


        # d_path = doc.get_path(w=True)
        # d_status = doc.status

        # with open(d_path, 'w') as f:
        #     f.write(request.POST.get('new_data'))

        if d_status == 'NA':
            doc.status = 'WIP'

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

