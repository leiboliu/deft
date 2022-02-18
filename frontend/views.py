from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

# Create your views here.
from backend.models import DataSet, Project, DataFile
from utils.automated_annotation import auto_annotate


class LoginView(View):
    template_name = "frontend/login.html"

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        uname = request.POST.get('username')
        pwd = request.POST.get('password')

        user = authenticate(request, username=uname, password=pwd)

        next = request.GET.get('next') if request.GET.get('next') != None else 'dashboard_view'

        if user:
            login(request, user)
            return redirect(next)
        print("Wrong login credentials")
        raise PermissionDenied


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        usr = request.user
        print(dir(usr))

        if usr and not usr.is_anonymous:
            logout(request)
        return redirect('frontend_view')


class DashboardView(LoginRequiredMixin, View):
    template_name = 'frontend/dashboard.html'

    def get(self, request):
        # if not request.user.is_authenticated:
        #     return redirect('frontend_view')
        return render(request, self.template_name, {})

class DatasetView(LoginRequiredMixin, View):
    template_name = 'frontend/datasets.html'

    def get(self, request, project_id):

        if (  # request.user.is_authenticated and  # request.user.is_annotator and
                Project.objects.filter(
                    id=project_id,
                    # datasets__assigned_staff__staff_id=request.user.id
                ).exists()):
            return render(request, self.template_name, {'pid': project_id})

        return HttpResponse(
            'You are not authorised to access this page',
            status=403
        )

class AnnotationView(LoginRequiredMixin, View):

    template_name = 'frontend/annotation.html'

    def get(self, request, project_id, dataset_id):

        project = Project.objects.filter(id=project_id)
        # first_dataset_file = DataFile.objects.filter(dataset__id=dataset_id).first()
        tags_list = []
        # doc = None

        if project:
            tl = project[0].tags.all()

            for k in tl:
                tags_list.append(k.to_display())

        # if first_dataset_file:
        #     doc_id = first_dataset_file.id
        #     with open(first_dataset_file.get_path(), 'r') as f:
        #         doc_content = f.read()
        #
        #         if first_dataset_file.status == 'NA':
        #             doc_content = auto_annotate(doc_content)
        #
        #         doc = mark_safe(doc_content)

        return render(
            request, self.template_name,
            {
                # 'doc_id': doc_id,
                'tags': tags_list,
                # 'doc': doc,
                'pid': project_id, 'dataset_id': dataset_id,
            }
        )



