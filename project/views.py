from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, ProtectedError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View

from accounts.decorators import require_user_access_rights
from accounts.mixins import ProjectsRequiredMixin
from accounts.models import User, Role, CompanyClient
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from project.forms import ProjectForm, ProjectFileForm, ProjectFileFormSet, ProjectEditForm
from project.models import ProjectFile, Project
from tasks.models import Task, Board, Card


def get_project_custom_id(request):
    previous_project_code = Project.objects.filter(company=get_company_object_from_user(request.user.id)).last()
    if previous_project_code == None:
        p_code = 'PRO-0001'
    else:
        p_p_c = previous_project_code.code
        pro_code_str = p_p_c[4:]
        pro_code_count = int(pro_code_str) + 1
        if pro_code_count < 10:
            p_code = 'PRO-000' + str(pro_code_count)
        elif pro_code_count < 100:
            p_code = 'PRO-00' + str(pro_code_count)
        elif pro_code_count < 1000:
            p_code = 'PRO-0' + str(pro_code_count)
        else:
            p_code = 'PRO-' + str(pro_code_count)
    return p_code


class ProjectsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        p_code = get_project_custom_id(request)
        form_class = ProjectForm(request, initial={'code': p_code})
        form_class1 = ProjectFileForm()
        project_all = Project.objects.filter(company=company)
        if request.user.user_type == User.CLIENT:
            clients = CompanyClient.objects.filter(company=company, email=request.user.email)
            client = CompanyClient.objects.filter(company=company, email=request.user.email)
            user_client = get_object_or_404_template_default(CompanyClient, email=request.user.email)
            projects = project_all.filter(client=user_client)

        else:
            clients = CompanyClient.objects.filter(company=company)
            client = CompanyClient.objects.filter(company=company, user=request.user).first()
            projects = project_all.filter(Q(team=request.user) | Q(lead_by=request.user)).distinct()
            for r in request.user.role.all():
                if r.name == 'Owner':
                    projects = Project.objects.filter(company=company)
        clients_count = CompanyClient.objects.filter(company=company).count()
        users = User.objects.filter(company=company, user_type='employee', report_to=request.user)
        roles = Role.objects.filter(company=company)
        leads_in = Project.objects.filter(company=company).values('lead_by').distinct()
        leads = User.objects.filter(id__in=leads_in)
        context = {'form': form_class, 'fileform': form_class1, 'projects': projects, 'search_projects':projects,
                   'clients': clients, 'roles': roles, 'users': users, 'clients_count': clients_count, 'leads': leads,
                   'client': client}
        if kwargs.get('list') == 'list':
            return render(request, 'project-list.html', context)
        return render(request, 'projects.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        form_class = ProjectForm(request, request.POST)
        form_class1 = ProjectFileForm(request.POST.get('file'), request.FILES)
        if form_class.is_valid():
            project = form_class.save(commit=False)
            project.created_by = request.user
            project.company = company
            project.save()
            form_class._save_m2m()
            if form_class1.is_valid():
                for f in request.FILES.getlist('file'):
                    file_type = f.content_type
                    type = f.content_type.split('/')[0]
                    if type == 'image' or type == 'audio' or type == 'video':
                        file_type = f.content_type.split('/')[0]
                    instance = ProjectFile(project=project, file=f, uploaded_by=request.user, type=file_type, company=company)
                    instance.save()
            messages.success(request, 'Project Added ')
            if kwargs.get('list') == 'list':
                return redirect('project_list', kwargs.get('list'))
            return redirect('projects')
        else:
            messages.error(request, form_class.errors)
            messages.error(request, form_class1.errors)
            if kwargs.get('list') == 'list':
                return redirect('project_list', list=kwargs.get('list'))
            return redirect('projects')


@require_user_access_rights(['owner', 'projects'])
@login_required
def get_project_edit_form(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(id=kwargs.get('pk'), company=company)
    file = ProjectFile.objects.filter(project=project, company=company).all()
    id = kwargs.get('pk')
    if request.method == 'POST':
        form = ProjectEditForm(request, request.POST, instance=project)
        fileformset = ProjectFileFormSet(request.POST, request.FILES, instance=project, queryset=file)
        if form.is_valid():
            form.save()
            if fileformset.is_valid():
                forms1 = fileformset.save(commit=False)
                for f in forms1:
                    f.company = company
                    f.uploaded_by = request.user
                    f.save()
            messages.success(request, 'Project Update Successful!')
            if kwargs.get('type') == 'list':
                return redirect('/projects/list')
            elif kwargs.get('type') == 'alist':
                return redirect('project', id)
            elif kwargs.get('type') == 'dashboard':
                return redirect('index')
            return redirect('projects')
        else:
            messages.error(request, form.errors)
            messages.error(request, fileformset.errors)
            if kwargs.get('type') == 'list':
                return redirect('/projects/list')
            elif kwargs.get('type') == 'alist':
                return redirect('project', id)
            elif kwargs.get('type') == 'dashboard':
                return redirect('index')
            return redirect('projects')
    if request.is_ajax and request.method == 'GET':
        form = ProjectEditForm(request, instance=project)
        fileformset = ProjectFileFormSet(instance=project, queryset=file)
        form_string = render_to_string('project-edit-form.html', {'form': form, 'fileformset': fileformset, 'project_id': project.id, 'type': kwargs.get('type')}, request)
        return JsonResponse({'project_edit_form': form_string}, status=200)
    messages.error(request, 'Processing Error!. Try Again')
    return redirect('projects')


@require_user_access_rights(['owner', 'projects'])
@login_required
def assign_member(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(id=kwargs.get('project'), company=company)
    user = User.objects.get(id=kwargs.get('user'), company=company)
    project.team.add(user)
    project.save()
    pk = project.id
    return redirect('project', pk)

@require_user_access_rights(['owner', 'projects'])
@login_required
def assign_lead(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(id=kwargs.get('project'), company=company)
    user = User.objects.get(id=kwargs.get('user'), company=company)
    project.lead_by= user
    project.save()
    pk = project.id
    return redirect('project', pk)

@require_user_access_rights(['owner', 'projects'])
@login_required
def update_project_priority(request, pk, priority, type):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(id=pk, company=company)
    if priority == 'High':
        if project.priority == 'High':
            messages.success(request, 'Project is already at ' + priority)
            return redirect('/projects/list/')
        project.priority = Project.High
    if priority == 'Medium':
        if project.priority == 'Medium':
            messages.success(request, 'Project is already at ' + priority)
            return redirect('/projects/list/')
        project.priority = Project.Medium
    if priority == 'Low':
        if project.priority == 'Low':
            messages.success(request, 'Project is already at ' + priority)
            return redirect('/projects/list/')
        project.priority = Project.Low
    project.save()
    messages.success(request, 'Project has been updated to ' + project.priority)
    if type == 'list':
        return redirect('/projects/list/')
    return redirect('project', pk)

@require_user_access_rights(['owner', 'projects'])
@login_required
def update_project_state(request, pk, state):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(id=pk, company=company)
    if state == 'active':
        if project.Project_state == True:
            messages.success(request, 'Project is already ' + state)
            return redirect('/projects/list/')
        project.Project_state = True
    elif state == 'inactive':
        if project.Project_state == False:
            messages.success(request, 'Project is already ' + state)
            return redirect('/projects/list/')
        project.Project_state = False
    project.save()
    messages.success(request, 'Project has been updated to ' + state)
    return redirect('/projects/list/')


@require_user_access_rights(['owner', 'projects'])
@login_required
def delete_project(request, pk, *args, **kwargs):
    project = None
    company = get_company_object_from_user(request.user.id)
    if Project.objects.filter(company=company, id=pk).exists():
        project = Project.objects.get(company=company, id=pk)
    if project is not None:
        try:
            project.delete()
            messages.success(request, 'Project has been deleted')
        except ProtectedError as e:
            messages.error(request,
                           project.name + "Some Thing Went Wrong.Reload The Page")
    else:
        messages.error(request, "Project is already deleted")
    if kwargs.get('list'):
        return redirect('/projects/list/')
    return redirect('projects')


@require_user_access_rights(['owner', 'projects'])
@login_required
def delete_project_list(request, pk, *args, **kwargs):
    project = None
    company = get_company_object_from_user(request.user.id)
    if Project.objects.filter(company=company, id=pk).exists():
        project = Project.objects.get(company=company, id=pk)
    if project is not None:
        try:
            project.delete()
            messages.success(request, 'Project has been deleted')
        except ProtectedError as e:
            messages.error(request,  "Some Thing Went Wrong.Reload The Page")
    else:
        messages.success(request, 'Project is already deleted')
    return redirect('/projects/list/')


@require_user_access_rights(['owner', 'projects'])
@login_required
def delete_file(request, pk, *args, **kwargs):
    project_file = None
    company = get_company_object_from_user(request.user.id)
    if ProjectFile.objects.filter(company=company, id=pk).exists():
        project_file = ProjectFile.objects.get(company=company, id=pk)
    if project_file is not None:
        try:
            project_file.delete()
            messages.success(request, 'Project has been deleted')
        except ProtectedError as e:
            messages.error(request, "Some Thing Went Wrong.Reload The Page")
    else:
        messages.error(request, "Project already deleted")
    id = project_file.project.id
    return redirect('project', id)


@login_required
def project_search(request, **kwargs):
    search_form = request.POST
    projects = None

    company = get_company_object_from_user(request.user.id)
    projects = Project.objects.filter(company=company)
    k_search = {}
    if request.POST.get('client_id'):
        k_search['client'] = search_form.get('client_id')

    if request.POST.get('user_id'):
        k_search['team'] = search_form.get('user_id')

    if request.POST.get('lead'):
        k_search['lead_by'] = search_form.get('lead')

    # if request.POST.get('client_id'):
    #     user_client = get_object_or_404_template_default(CompanyClient, email=request.user.email)
    #     projects = Project.objects.filter(id__in=projects, client=request.POST.get('client_id'), company=company)
    #     if request.POST.get('user_id'):
    #         projects = Project.objects.filter(id__in=projects, team=request.POST.get('user_id'), company=company)
    #         if request.POST.get('lead'):
    #             projects = Project.objects.filter(id__in=projects, client=request.POST.get('lead'), company=company)
    # elif request.POST.get('user_id'):
    #     projects = Project.objects.filter(id__in=projects, team=request.POST.get('user_id'), company=company)
    #     if request.POST.get('lead'):
    #         projects = Project.objects.filter(id__in=projects, lead_by=request.POST.get('lead'), company=company)
    #
    # elif request.POST.get('lead'):
    #       projects = Project.objects.filter(id__in=projects, lead_by=request.POST.get('lead'), company=company)

    projects = Project.objects.filter(id__in=projects, **k_search, company=company)
    form_class = ProjectForm(request)
    form_class1 = ProjectFileForm()
    clients = CompanyClient.objects.filter(company=company)
    users = User.objects.filter(company=company, user_type='employee', report_to=request.user)
    search_projects = Project.objects.filter(company=company)
    leads_in = Project.objects.filter(company=company).values('lead_by').distinct()
    leads = User.objects.filter(id__in=leads_in, company=company)
    context = {'form': form_class, 'fileform': form_class1, 'projects': projects, 'search_projects': search_projects,'clients': clients, 'leads':leads,
               'users': users}
    if kwargs.get('type') == 'list':
        return render(request, 'project-list.html', context)
    return render(request, 'projects.html', context)


@require_user_access_rights(['owner', 'projects'])
@login_required
def update_project_progress(request, pk, progress):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(company=company, id=pk)

    if project.progress == progress:
        messages.success(request, 'Project is already at ' + progress)
        return redirect('project', pk)
    project.progress = progress
    project.save()
    messages.success(request, 'Project has been updated to ' + project.progress)
    return redirect('project', pk)


class ProjectView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        project = get_object_or_404_template_default(Project, id=kwargs.get('pk'), company=company)
        board = Board.objects.filter(project=project, company=company).prefetch_related('board_cards')
        open_task = Card.objects.filter(board__in=board, status=Task.IN_PROGRESS, company=company).count()
        completed_task = Card.objects.filter(board__in=board, status=Task.FINISHED, company=company).count()
        members = User.objects.filter(company=company, report_to=request.user).exclude(id__in=project.team.all())
        membersLead = User.objects.filter(company=company, report_to=request.user).exclude(id=project.lead_by.id)
        all_tasks = Card.objects.filter(board__in=board, company=company).all()

        context = {'project': project, 'members': members, 'open_task': open_task, 'completed_task': completed_task,
                   'membersLead': membersLead, 'all_tasks': all_tasks}
        return render(request, 'project-view.html', context)
