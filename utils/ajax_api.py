from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse


# @login_required
def dtable_project_list(request):

    _ = request

    project_list = [
        [10, 'Archived', '1st Project', 'This is a sample project.'],
        [20, 'Active', '2nd Project', 'This is another sample project.'],
    ]

    return JsonResponse({'data': project_list})
