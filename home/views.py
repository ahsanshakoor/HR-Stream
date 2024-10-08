import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q, ProtectedError
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from accounts.decorators import require_user_access_rights
from accounts.mixins import EquipmentRequiredMixin, BookmarkRequiredMixin
from accounts.models import User, CompanyClient, Role
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from accounts.models import User, CompanyClient, Announcement
from accounts.utils import get_company_object_from_user
from attendance.models import Attendance, AttendancePolicy
from checkin.models import CheckIn
from home.forms import EquipmentForm, EquipmentFormEdit, BookmarkForm, CompanyFileForm, FileDirectoryTypeForm
from home.models import Equipment, DemoRequest, Bookmark, CompanyFile, FileDirectoryType
from leave.form import LeaveRequestForm
from leave.models import LeaveRequest, Leave, LeaveStatistics, LeavePolicy
from payroll.models import Payroll, PayrollPolicy, HealthInsurance
from project.models import Project
from tasks.models import Task, Board, Card
from todo.form import addTodoForm
from todo.models import Todo


class HomeView(LoginRequiredMixin, View):
    template_name = 'dashboard.html'

    def get(self, request,*args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        if request.user.user_type == User.CLIENT:
            return redirect('projects')
        todos = Todo.objects.filter(created_by=request.user, company=company)[:5]
        project_in = Project.objects.filter(company=company)
        completed_projects = Project.objects.filter(company=company, Project_status=Project.FINISHED).count()
        projects = Project.objects.filter(company=company).count()
        completed_project_percentage = get_task_percentage(completed_projects, projects)
        employees = User.objects.filter(company=company, user_type='employee').count()
        employees_in = User.objects.filter(company=company, user_type='employee')
        new_employees = User.objects.filter(company=company, user_type='employee', created__month=datetime.datetime.now().month).count()
        new_employees_percentage = (new_employees/employees)*100
        clients = CompanyClient.objects.filter(company=company).count()
        clients_in = CompanyClient.objects.filter(company=company)

        tasks = Task.objects.filter(project__in=project_in).count()
        completed_tasks = Task.objects.filter(project__in=project_in, status=Task.FINISHED).count()
        completed_tasks_percentage = get_task_percentage(completed_tasks, tasks)
        in_progress_tasks = Task.objects.filter(project__in=project_in,status=Task.IN_PROGRESS).count()
        in_progress_tasks_percentage = get_task_percentage(in_progress_tasks, tasks)
        pending_tasks = Task.objects.filter(project__in=project_in, status=Task.PENDING).count()
        pending_tasks_percentage = get_task_percentage(pending_tasks, tasks)
        on_hold_tasks = Task.objects.filter(project__in=project_in, status=Task.ON_HOLD).count()
        on_hold_tasks_percentage = get_task_percentage(on_hold_tasks, tasks)
        under_review_tasks = Task.objects.filter(project__in=project_in, status=Task.UNDER_REVIEW).count()
        under_review_tasks_percentage = get_task_percentage(under_review_tasks, tasks)

        leaves = LeaveRequest.objects.filter(employee__leave_policy__company=company, leave_from__gte=datetime.datetime.now().date()).count()
        today_leaves = LeaveRequest.objects.filter(employee__leave_policy__company=company, leave_from=datetime.datetime.now().date()).count()
        today_leaves_percentage = get_task_percentage(today_leaves, leaves)
        present_employee = Attendance.objects.filter(employee__in=employees_in).values_list('employee')
        absent_employees = User.objects.filter(company=company, user_type='employee').exclude(User__in=present_employee)
        today_leave_request = LeaveRequest.objects.filter(employee__in=absent_employees, leave_from=datetime.datetime.now().date(), status=LeaveRequest.Approved)
        user_total_task = Card.objects.filter(assign_to=request.user).count()
        user_pending_task = Card.objects.filter(assign_to=request.user, status=Task.PENDING).count()
        user_project_all = Project.objects.filter(company=company)
        user_project = user_project_all.filter(Q(lead_by=request.user) | Q(team=request.user)).distinct().count()
        leaves = Leave.objects.filter(leave_policy=request.user.leave_policy)
        leave_statistics = LeaveStatistics.objects.filter(leave_type__in=leaves, employee=request.user.id)
        remaining_days = LeaveStatistics.objects.filter(leave_type__in=leaves, employee=request.user.id ).aggregate(Sum('remaining_days'))
        remaining_days = remaining_days['remaining_days__sum']
        if remaining_days == None:
            remaining_days = 0
        if not leave_statistics:
            remaining_days = Leave.objects.filter(leave_policy=request.user.leave_policy).aggregate(Sum('days'))
            remaining_days = remaining_days['days__sum']
            if remaining_days is None:
                remaining_days = 0
        form_class = LeaveRequestForm(initial={'leave_type': leaves, 'requested_days': 1 })
        total_days = Leave.objects.filter(leave_policy=request.user.leave_policy).aggregate(Sum('days'))
        total_days = total_days['days__sum']
        if total_days == None:
            taken_leaves = 0
        else:
            taken_leaves = total_days - remaining_days
        overdue_tasks = Task.objects.filter(due_date__lt=datetime.datetime.now(), project__in=project_in).all()
        todo_form = addTodoForm()
        now = datetime.datetime.now().date()
        client = CompanyClient.objects.filter(user=request.user).first()
        announcements = Announcement.objects.filter(company=company).order_by('-updated_at')[:5]
        bookmarks = Bookmark.objects.filter(company=get_company_object_from_user(request.user.id), marked=True)
        context = {'projects': projects, 'employees': employees, 'clients': clients, 'tasks': tasks,
                   'new_employees_percentage': new_employees_percentage, 'new_employees': new_employees,
                   'completed_tasks': completed_tasks, 'completed_tasks_percentage': completed_tasks_percentage,
                   'in_progress_tasks': in_progress_tasks, 'in_progress_tasks_percentage': in_progress_tasks_percentage,
                   'pending_tasks': pending_tasks, 'pending_tasks_percentage': pending_tasks_percentage,
                   'on_hold_tasks': on_hold_tasks, 'on_hold_tasks_percentage': on_hold_tasks_percentage,
                   'under_review_tasks': under_review_tasks, 'under_review_tasks_percentage': under_review_tasks_percentage,
                   'client_list': clients_in, 'project_list': project_in, 'completed_projects': completed_projects,
                   'completed_project_percentage': completed_project_percentage, 'today_leaves': today_leaves, 'leaves': leaves,
                   'today_leaves_percentage': today_leaves_percentage, 'today_leave_request': today_leave_request,
                   'user_total_task': user_total_task,
                   'user_pending_task':  user_pending_task, 'user_project': user_project, 'leave_form': form_class,
                   'remaining_days': remaining_days, 'taken_leaves': taken_leaves, 'overdue_tasks': overdue_tasks,
                   'todos': todos, 'todo_form': todo_form, 'now': now, 'client': client, 'announcements': announcements,
                   'bookmarks': bookmarks
                   }
        template_name = self.template_name
        return render(request, template_name, context)


def get_task_percentage(task, total_task):
    if total_task == 0:
        return 0
    percentage = (task/total_task)*100
    return round(percentage, 2)


class UpdateHomeTodo(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        if request.method == 'GET':
            if kwargs.get('pk'):
                obj = Todo.objects.get(id=kwargs.get('pk'))
                if obj.is_read == False:
                    obj.is_read = True
                    obj.save()
                else:
                    obj.is_read = False
                    obj.save()
                return redirect(reverse('index'))


class DeleteHomeTodo(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            Todo.objects.get(id=kwargs.get('pk')).delete()
            return redirect(reverse('index'))


def baseelements(request):
    status = CheckIn.objects.filter(name=request.user).last()
    count = Task.objects.filter(status=Task.START, assign_to=request.user.id).count()
    tasks = Task.objects.filter(status=Task.START, assign_to=request.user.id)
    form1 = addTodoForm
    context = {'count': count, 'status': status, 'tasks': tasks,'formtodo': form1}
    return context


class CustomPolicyView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'custom-policy.html')

    def post(self, request, *args, **kwargs):
        # print('hello')
        assigned_users = []
        unassigned_users = []
        policy = None
        something_saved = False
        form = request.POST
        if form.get('customleave_to'):
            assigned_users = request.POST.getlist('customleave_to')
            print(assigned_users)
        if form.get('customleave_from'):
            unassigned_users = request.POST.getlist('customleave_from')
            print(unassigned_users)
        if form['policy_type'] == 'Payroll Policy':
            if form['policy']:
                policy = PayrollPolicy.objects.get(id=int(form['policy']))
            else:
                return redirect('add_custom_policy')
            for user in assigned_users:
                # print(user)
                obj = User.objects.get(id=int(user))
                # print(obj)
                obj.payroll_policy = policy
                obj.save()
                something_saved = True
            for user in unassigned_users:
                # print(user, 'before')
                obj = User.objects.get(id=int(user))
                if obj.payroll_policy == policy:
                    # print(obj, 'after')
                    obj.payroll_policy = None
                    obj.save()
                    something_saved = True
        elif form['policy_type'] == 'Attendance Policy':
            if form['policy']:
                policy = AttendancePolicy.objects.get(id=int(form['policy']))
            else:
                return redirect('add_custom_policy')
            for user in assigned_users:
                obj = User.objects.get(id=int(user))
                obj.attendance_policy = policy
                obj.save()
                something_saved = True
            for user in unassigned_users:
                obj = User.objects.get(id=int(user))
                if obj.attendance_policy == policy:
                    # print(obj.attendance_policy, 'before')
                    obj.attendance_policy = None
                    obj.save()
                    something_saved = True
        elif form['policy_type'] == 'Leave Policy':
            if form['policy']:
                policy = LeavePolicy.objects.get(id=int(form['policy']))
            else:
                return redirect('add_custom_policy')
            for user in assigned_users:
                obj = User.objects.get(id=int(user))
                obj.leave_policy = policy
                obj.save()
                something_saved = True
            for user in unassigned_users:
                obj = User.objects.get(id=int(user))
                if obj.leave_policy == policy:
                    obj.leave_policy = None
                    obj.save()
                    something_saved = True
        elif form['policy_type'] == 'Health Insurance':
            if form['policy']:
                policy = HealthInsurance.objects.get(id=int(form['policy']))
            else:
                return redirect('add_custom_policy')
            for user in assigned_users:
                obj = User.objects.get(id=int(user))
                obj.health_insurance = policy
                obj.save()
                something_saved = True
            for user in unassigned_users:
                obj = User.objects.get(id=int(user))
                if obj.health_insurance == policy:
                    obj.health_insurance = None
                    obj.save()
                    something_saved = True

        if policy and something_saved:
            messages.success(request, policy.name + ' has been updated.')
        return redirect('add_custom_policy')


# working
@login_required
def get_policy(request, pol_id=None):
    if request.is_ajax:
        company = get_company_object_from_user(request.user.id)
        policies = None
        if pol_id is not None:
            if pol_id == 'Payroll Policy':
                policies = list(PayrollPolicy.objects.filter(company=company).values_list('id', 'name'))
            elif pol_id == 'Attendance Policy':
                policies = list(AttendancePolicy.objects.filter(company=company, policy_status=True).values_list('id', 'name'))
            elif pol_id == 'Leave Policy':
                policies = list(LeavePolicy.objects.filter(company=company, is_active=True).values_list('id', 'name'))
            elif pol_id == 'Health Insurance':
                policies = list(HealthInsurance.objects.filter(company=company, active=True).values_list('id', 'name'))
            print(policies)
            return JsonResponse({'policies': policies}, status=200)

    return JsonResponse({'error': ''}, status=400)



# working
@login_required
def get_policy_user(request, pol_id=None, policy=None):
    if request.is_ajax:
        company = get_company_object_from_user(request.user.id)

        if pol_id is not None and policy is not None:
            users = None
            if policy == 'Payroll Policy':
                users = User.objects.filter(company=company, user_type=User.EMPLOYEE, payroll_policy=pol_id)
            elif policy == 'Attendance Policy':
                users = User.objects.filter(company=company, user_type=User.EMPLOYEE, attendance_policy=pol_id)
            elif policy == 'Leave Policy':
                users = User.objects.filter(company=company, user_type=User.EMPLOYEE, leave_policy=pol_id)
            elif policy == 'Health Insurance':
                users = User.objects.filter(company=company, user_type=User.EMPLOYEE, health_insurance=pol_id)

            if users:
                nusers = list(User.objects.filter(company=company, user_type=User.EMPLOYEE).exclude(id__in=users).values_list('id', 'username'))
            else:
                nusers = list(User.objects.filter(company=company, user_type=User.EMPLOYEE).values_list('id', 'username'))
            users = User.objects.filter(company=company, id__in=users, user_type=User.EMPLOYEE).values_list('id', 'username')
            users = list(users)
            return JsonResponse({'nusers': nusers, 'users': users}, status=200)

    return JsonResponse({'error': ''}, status=400)


@require_user_access_rights(['owner', 'admin_dashboard'])
@login_required
def admin_dashboard(request):
    company = get_company_object_from_user(request.user.id)
    project_in = Project.objects.filter(company=company)
    completed_projects = Project.objects.filter(company=company, Project_status=Project.FINISHED).count()
    projects = Project.objects.filter(company=company).count()
    completed_project_percentage = get_task_percentage(completed_projects, projects)
    employees = User.objects.filter(company=company, user_type='employee').count()
    employees_in = User.objects.filter(company=company, user_type='employee')
    new_employees = User.objects.filter(company=company, user_type='employee',
                                        created__month=datetime.datetime.now().month).count()
    new_employees_percentage = (new_employees / employees) * 100
    clients = CompanyClient.objects.filter(company=company).count()
    clients_in = CompanyClient.objects.filter(company=company)

    board = Board.objects.filter(project__in=project_in).all()
    tasks = Card.objects.filter(board__in=board).count()
    completed_tasks = Card.objects.filter(board__in=board, status=Card.FINISHED).count()
    completed_tasks_percentage = get_task_percentage(completed_tasks, tasks)
    in_progress_tasks = Card.objects.filter(board__in=board, status=Card.IN_PROGRESS).count()
    in_progress_tasks_percentage = get_task_percentage(in_progress_tasks, tasks)
    pending_tasks = Card.objects.filter(board__in=board, status=Card.PENDING).count()
    pending_tasks_percentage = get_task_percentage(pending_tasks, tasks)
    on_hold_tasks = Card.objects.filter(board__in=board, status=Card.ON_HOLD).count()
    on_hold_tasks_percentage = get_task_percentage(on_hold_tasks, tasks)
    under_review_tasks = Card.objects.filter(board__in=board, status=Card.UNDER_REVIEW).count()
    under_review_tasks_percentage = get_task_percentage(under_review_tasks, tasks)

    # tasks = Task.objects.filter(project__in=project_in).count()
    # completed_tasks = Task.objects.filter(project__in=project_in, status=Task.FINISHED).count()
    # completed_tasks_percentage = get_task_percentage(completed_tasks, tasks)
    # in_progress_tasks = Task.objects.filter(project__in=project_in, status=Task.IN_PROGRESS).count()
    # in_progress_tasks_percentage = get_task_percentage(in_progress_tasks, tasks)
    # pending_tasks = Task.objects.filter(project__in=project_in, status=Task.PENDING).count()
    # pending_tasks_percentage = get_task_percentage(pending_tasks, tasks)
    # on_hold_tasks = Task.objects.filter(project__in=project_in, status=Task.ON_HOLD).count()
    # on_hold_tasks_percentage = get_task_percentage(on_hold_tasks, tasks)
    # under_review_tasks = Task.objects.filter(project__in=project_in, status=Task.UNDER_REVIEW).count()
    # under_review_tasks_percentage = get_task_percentage(under_review_tasks, tasks)

    leaves = LeaveRequest.objects.filter(employee__leave_policy__company=company,
                                         leave_from__gte=datetime.datetime.now().date()).count()
    today_leaves = LeaveRequest.objects.filter(employee__leave_policy__company=company,
                                               leave_from=datetime.datetime.now().date()).count()
    today_leaves_percentage = get_task_percentage(today_leaves, leaves)
    present_employee = Attendance.objects.filter(employee__in=employees_in).values_list('employee')
    absent_employees = User.objects.filter(company=company, user_type='employee').exclude(User__in=present_employee)
    today_leave_request = LeaveRequest.objects.filter(employee__in=absent_employees,
                                                      leave_from=datetime.datetime.now().date(),
                                                      status=LeaveRequest.Approved)
    user_total_task = Task.objects.filter(assign_to=request.user).count()
    user_pending_task = Task.objects.filter(assign_to=request.user, status=Task.PENDING).count()
    user_project_all = Project.objects.filter(company=company)
    user_project = user_project_all.filter(Q(lead_by=request.user) | Q(team=request.user)).distinct().count()
    leaves = Leave.objects.filter(leave_policy=request.user.leave_policy)
    leave_statistics = LeaveStatistics.objects.filter(leave_type__in=leaves)
    remaining_days = LeaveStatistics.objects.filter(leave_type__in=leaves).aggregate(Sum('remaining_days'))
    remaining_days = remaining_days['remaining_days__sum']
    if remaining_days == None:
        remaining_days = 0
    if not leave_statistics:
        remaining_days = Leave.objects.filter(leave_policy=request.user.leave_policy).aggregate(Sum('days'))
        remaining_days = remaining_days['days__sum']
        if remaining_days is None:
            remaining_days = 0
    form_class = LeaveRequestForm(initial={'leave_type': leaves})
    total_days = Leave.objects.filter(leave_policy=request.user.leave_policy).aggregate(Sum('days'))
    total_days = total_days['days__sum']
    if total_days == None:
        taken_leaves = 0
    else:
        taken_leaves = total_days - remaining_days
    overdue_tasks = Card.objects.filter(due_date__lt=datetime.datetime.now(), board__in=board).all()
    context = {'projects': projects, 'employees': employees, 'clients': clients, 'tasks': tasks,
               'new_employees_percentage': new_employees_percentage, 'new_employees': new_employees,
               'completed_tasks': completed_tasks, 'completed_tasks_percentage': completed_tasks_percentage,
               'in_progress_tasks': in_progress_tasks, 'in_progress_tasks_percentage': in_progress_tasks_percentage,
               'pending_tasks': pending_tasks, 'pending_tasks_percentage': pending_tasks_percentage,
               'on_hold_tasks': on_hold_tasks, 'on_hold_tasks_percentage': on_hold_tasks_percentage,
               'under_review_tasks': under_review_tasks, 'under_review_tasks_percentage': under_review_tasks_percentage,
               'client_list': clients_in, 'project_list': project_in, 'completed_projects': completed_projects,
               'completed_project_percentage': completed_project_percentage, 'today_leaves': today_leaves,
               'leaves': leaves,
               'today_leaves_percentage': today_leaves_percentage, 'today_leave_request': today_leave_request,
               'user_total_task': user_total_task,
               'user_pending_task': user_pending_task, 'user_project': user_project, 'leave_form': form_class,
               'remaining_days': remaining_days, 'taken_leaves': taken_leaves, 'overdue_tasks': overdue_tasks,
               }
    return render(request, 'admin-dashboard.html', context)


def landing_page(request):
    user = False
    if request.user.is_authenticated:
        user = True
    context = {'userLogin': user}
    return render(request, 'home/rnr/index.html', context)


def contact_page(request):
    user = False
    if request.user.is_authenticated:
        user = True
    context = {'userLogin': user}
    return render(request, 'home/rnr/contact.html', context)


def features_page(request):
    user = False
    if request.user.is_authenticated:
        user = True
    context = {'userLogin': user}
    return render(request, 'home/rnr/features.html', context)


def pricing_page(request):
    user = False
    if request.user.is_authenticated:
        user = True
    context = {'userLogin': user}
    return render(request, 'home/rnr/pricing.html', context)


def graph(request):
    return render(request, 'organization-hierarchy.html')


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def organization_hirearchy(request):
    company = get_company_object_from_user(request.user.id)
    owner = User.objects.get(role__name='Owner', company=company)
    data = get_organization_hierarchy(request, owner)
    return JsonResponse(data)


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def get_organization_hierarchy(request, user):
        data = {}
        data['name'] = user.username
        data['firstname'] = user.first_name
        data['lastname'] = user.last_name
        data['imageUrl'] = ""
        if user.profile_pic:
            data['imageUrl'] = user.profile_pic.url
        data['area'] = ""
        data['profileUrl'] = ""
        if user.profile_pic:
            data['profileUrl'] = user.profile_pic.url
        data['office'] = "CTO office"
        data['tags'] = "Ceo,tag1,manager,cto"
        data['isLoggedUser'] = False
        data['user_id'] = user.id
        if user.id is request.user.id:
            data['isLoggedUser'] = True
        if user.department:
            data['unit'] = {
                "type": "department",
                "value": user.department.name
            }
        else:
            data['unit'] = {
                "type": "business",
                "value": "Business"
            }
        if user.designation:
            data['positionName'] = user.designation.name
        else:
            data['positionName'] = "CEO"
        list = []
        reporting_employees = User.objects.filter(report_to=user, company=get_company_object_from_user(user.id))
        if reporting_employees:
            for employee in reporting_employees:
                list.append(get_organization_hierarchy(request, employee))
            data['children'] = list
        return data


class EquipmentView(LoginRequiredMixin, EquipmentRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        equipments = Equipment.objects.filter(company=company)

        users = User.objects.filter(company=company)
        equipmentForm = EquipmentForm(company_name=company.name, initial={'equipment_code': get_equipment_custom_id(request)})
        context = {'users': users,'equipments': equipments, 'equipmentForm': equipmentForm}
        return render(request, template_name='equipments.html', context=context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        equipmentForm = EquipmentForm(request.POST, company_name=company.name)
        if equipmentForm.is_valid():
            equipment = equipmentForm.save(commit=False)
            equipment.company =company
            equipment.save()
            messages.success(request, 'Equipment Added Successfully')
            return redirect('equipments')
        else:
            messages.error(request, 'Something Went Wrong. Please Try Again')
            return redirect('equipments')


@require_user_access_rights(['owner', 'equipment'])
@login_required
def equipment_delete(request, *args, **kwargs):
    try:
        if kwargs.get('pk'):
            Equipment.objects.get(id=kwargs.get('pk')).delete()
            messages.success(request, 'Equipment Deleted')
        return JsonResponse({'message': 'Equipment Deleted', 'pk': kwargs.get('pk')}, status=200)
    except:
        messages.error(request, 'Already Deleted')
        return JsonResponse({'message': 'Already Deleted'}, status=400)


@require_user_access_rights(['owner', 'equipment'])
@login_required
def get_equipment_custom_id(request):
    pEquipment = Equipment.objects.filter(company=get_company_object_from_user(request.user.id)).last()
    if pEquipment is None:
        equipment_code = 'EQP-0001'
    else:
        equipment_code = pEquipment.equipment_code
        if equipment_code in ('', None):
            equipment_code = 'EQP-0001'
            pEquipment.equipment_code = equipment_code
            pEquipment.save()
        # print(equipment_code)
        equipment_code_str = equipment_code[4:]
        equipment_code = 'EQP-{0:04d}'.format(int(equipment_code_str) + 1)
    return equipment_code


@require_user_access_rights(['owner', 'equipment'])
@login_required
def equipment_status(request, equipment_id, name):
    company = get_company_object_from_user(request.user.id)
    try:
        equipment = Equipment.objects.get(id=equipment_id, company=company)
        if equipment.status == name:
            messages.success(request, 'Status already set to ' + name)
        else:
            equipment.status = name
            messages.success(request, 'Status is updated to ' + name)
            equipment.save()
        return redirect('equipments')
    except:
        messages.warning(request, 'Equipment is deleted by employee')
        return redirect('equipments')


@require_user_access_rights(['owner', 'equipment'])
@login_required
def equipment_edit(request, pk=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'GET':
        equipment = get_object_or_404_template_default(Equipment, company=company, id=pk)
        equipmentForm = EquipmentFormEdit(instance=equipment)
        form_string = render_to_string('equipment_edit_form.html', {'equipmentForm': equipmentForm, 'equipment_id': equipment.id}, request)
        return JsonResponse({'equipment_edit_form': form_string}, status=200)
    else:
        return JsonResponse({'error': 'can not edit'}, status=400)


@require_user_access_rights(['owner', 'equipment'])
@login_required
def equipment_form_edit(request, pk):
    company = get_company_object_from_user(request.user.id)
    equipment = Equipment.objects.filter(company=company, id=pk).first()
    equipmentForm = EquipmentFormEdit(request.POST, instance=equipment)
    if equipmentForm.is_valid():
        equipmentForm.save()
        messages.success(request, 'Equipment Updated Successfully')
        return redirect('equipments')
    else:
        messages.error(request, 'Something Went Wrong. Please Try Again')
        return redirect('equipments')


@require_user_access_rights(['owner', 'equipment'])
@login_required
def equipment_search(request):
    user_id = request.POST.get('user_id')
    status = request.POST.get('status')
    name = request.POST.get('equipment_name')
    company = get_company_object_from_user(request.user.id)
    equipments = Equipment.objects.filter(company=company)
    user_object = None
    if user_id and user_id != 'None':
        user_object = User.objects.get(id=user_id, company=company)
        equipments = equipments.filter(Q(assign_to=user_object) | Q(status=status) | Q(name=name)).values()
    elif user_id == 'None':
        equipments = equipments.filter(Q(assign_to=user_object) | Q(status=status) | Q(name=name)).values()
    else:
        equipments = equipments.filter(Q(status=status) | Q(name=name)).values()
    list = []
    for equipment in equipments:
        if equipment['assign_to_id'] is not None:
            users = User.objects.filter(company=company)
            user_object = users.filter(id=equipment['assign_to_id']).values().first()
        dict = {
            'equipment': equipment,
            'user_object': user_object
        }
        list.append(dict)
    # equipments = list(equipments)
    # users = User.objects.filter(company=company)  # , report_to=user
    # equipmentForm = EquipmentForm(company_name=company.name,
    #                               initial={'equipment_code': get_equipment_custom_id(request)})
    # context = {'users': users, 'equipmentForm': equipmentForm, 'equipments': equipments}
    # return render(request, 'equipments.html', context=context)
    return JsonResponse({'equipments': list}, status=200)


def demo_request(request, *args, **kwargs):
    name = request.POST.get('fname')
    email = request.POST.get('email')
    number = request.POST.get('number')
    message = request.POST.get('message')
    demoRequest = DemoRequest.objects.create(name=name, number=number, email=email, message=message)
    response_data = {}
    response_data['response_date_tag'] = 'demoRequest'
    response_data['response_date_name'] = demoRequest.name
    response_data['response_date_email'] = demoRequest.email
    response_data['response_date_number'] = demoRequest.number
    return JsonResponse(response_data)


class BookmarkView(LoginRequiredMixin, BookmarkRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        bookmarks = Bookmark.objects.filter(company=get_company_object_from_user(request.user.id))
        bookmarkForm = BookmarkForm()
        context = {'bookmarks': bookmarks, 'bookmarkForm': bookmarkForm }
        return render(request, 'bookmarks.html', context)

    def post(self, request, *args, **kwargs):
        bookmarkForm = BookmarkForm(request.POST, request.FILES)
        if bookmarkForm.is_valid():
            form = bookmarkForm.save(commit=False)
            form.company = get_company_object_from_user(request.user.id)
            form.save()
            messages.success(request, 'Bookmark added Successfully')
            return redirect('bookmarks')


@require_user_access_rights(['owner', 'bookmark'])
@login_required
def bookmark_delete(request, *args, **kwargs):
    try:
        if kwargs.get('pk'):
            Bookmark.objects.get(id=kwargs.get('pk')).delete()
            messages.success(request, 'Bookmark Deleted')
        return redirect('bookmarks')
    except:
        messages.error(request, 'Already Deleted')
        return redirect('bookmarks')


@require_user_access_rights(['owner', 'bookmark'])
@login_required
def bookmark_edit(request, pk=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'GET':
        bookmark = get_object_or_404_template_default(Bookmark, company=company, id=pk)
        bookmarkForm = BookmarkForm(instance=bookmark)
        form_string = render_to_string('bookmark_edit_form.html', {'bookmarkForm': bookmarkForm, 'bookmark_id': bookmark.id}, request)
        return JsonResponse({'bookmark_edit_form': form_string}, status=200)
    else:
        return JsonResponse({'error': 'can not edit'}, status=400)


@require_user_access_rights(['owner', 'bookmark'])
@login_required
def bookmark_form_edit(request, pk):
    company = get_company_object_from_user(request.user.id)
    bookmark = Bookmark.objects.filter(company=company, id=pk).first()
    bookmarkForm = BookmarkForm(request.POST, request.FILES, instance=bookmark)
    if bookmarkForm.is_valid():
        bookmarkForm.save()
        messages.success(request, 'Bookmark Updated Successfully')
        return redirect('bookmarks')
    else:
        messages.error(request, 'Something Went Wrong. Please Try Again')
        return redirect('bookmarks')


class BookmarkEmployeeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        bookmarks = Bookmark.objects.filter(company=get_company_object_from_user(request.user.id), marked=True)
        context = {'bookmarks': bookmarks}
        return render(request, 'employee-bookmarks.html', context)


class FileManagerView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        file_form = CompanyFileForm(company_name=company)
        file_directories = FileDirectoryType.objects.filter(company=company)
        project_all = Project.objects.filter(company=company)
        if request.user.user_type == User.CLIENT:
            user_client = get_object_or_404_template_default(CompanyClient, email=request.user.email)
            projects = project_all.filter(client=user_client)
        else:
            projects = project_all.filter(Q(team=request.user) | Q(lead_by=request.user)).distinct()
            for r in request.user.role.all():
                if r.name == 'Owner':
                    projects = Project.objects.filter(company=company)
        context = {'projects': projects, 'file_directories': file_directories, 'file_form': file_form}
        return render(request, 'file-manager.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        form_class1 = CompanyFileForm(request.POST, request.FILES, company_name=company)
        if form_class1.is_valid():
            directory_id = request.POST.get('directory')
            title = request.POST.get('title')
            directory = get_object_or_404_template_default(FileDirectoryType, id=directory_id, company=company)
            for f in request.FILES.getlist('file'):
                file_type = f.content_type
                type = f.content_type.split('/')[0]
                if type == 'image' or type == 'audio' or type == 'video':
                    file_type = f.content_type.split('/')[0]
                instance = CompanyFile(file=f, uploaded_by=request.user, type=file_type, title=title,
                                       directory=directory, company=company)
                instance.save()
            messages.success(request, 'File Added ')
            return redirect('file_manager')
        else:
            messages.error(request, form_class1.errors)
            return redirect('file_manager')


@login_required
def delete_file_manager_file(request, pk, *args, **kwargs):
    company_file = None
    company = get_company_object_from_user(request.user.id)
    if CompanyFile.objects.filter(company=company, id=pk).exists():
        company_file = CompanyFile.objects.get(company=company, id=pk)
    if company_file is not None:
        try:
            company_file.delete()
            messages.success(request, 'File has been deleted')
        except ProtectedError as e:
            messages.error(request, "Some Thing Went Wrong.Reload The Page")
    return redirect('file_manager')


@require_user_access_rights(['owner', 'file_manager'])
@login_required
def company_file_directory_type(request):
    company = get_company_object_from_user(request.user.id)
    file_directory_types = FileDirectoryType.objects.filter(company=company).all()
    return render(request, 'file_directory_type.html', {'file_directory_types': file_directory_types})


@require_user_access_rights(['owner', 'file_manager'])
@login_required
def create_n_edit_file_directory_type(request, file_directory_type_id=None, type=None):
    if request.method == "POST":
        file_directory_type_name = request.POST['name'].strip()
        if file_directory_type_name not in (None, ''):
            if file_directory_type_id:
                file_directory_type = get_object_or_404_template_default(FileDirectoryType, id=file_directory_type_id)
                file_directory_type.name = file_directory_type_name
                file_directory_type.save()
                messages.success(request, 'FileDirectoryType Name Update Successful!')
            else:
                file_directory_type = FileDirectoryType.objects.create(name=file_directory_type_name,
                                                      company=get_company_object_from_user(request.user.id))
                file_directory_type.save()
                messages.success(request, 'FileDirectoryType Addition Successful!')
        else:
            messages.error(request, 'FileDirectoryType name is empty')
    if request.is_ajax and request.method == 'GET':
        file_directory_type = get_object_or_404_template_default(FileDirectoryType, id=file_directory_type_id)
        form = FileDirectoryTypeForm(instance=file_directory_type)
        form_string = render_to_string('file_directory_type_form.html', {'form': form, 'file_directory_type': file_directory_type}, request)
        return JsonResponse({'file_directory_form': form_string}, status=200)
    if type == 'directory':
        return redirect('showFileDirectoryType')
    return redirect('file_manager')


@require_user_access_rights(['owner', 'file_manager'])
@login_required
def delete_file_directory_type(request, file_directory_type_id=None):
    if file_directory_type_id is not None:
        try:
            file_directory_type = get_object_or_404_template_default(FileDirectoryType, id=file_directory_type_id)
            file_directory_type.delete()
        except ProtectedError:
            m = 'Deleting {0} will also delete its designations. Please make sure that all designations under {0} are not assigned to any employee.'.format(
                file_directory_type.name)
            messages.error(request, m)
            return redirect('showFileDirectoryType')

        messages.success(request, 'FileDirectoryType Deleted Successful!')
    return redirect('showFileDirectoryType')


@login_required
def share_file(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    file = CompanyFile.objects.get(id=kwargs.get('file'), company=company)
    users = request.POST.getlist('share')
    users = User.objects.filter(id__in=users, company=company)
    file.shared_with.clear()
    for user in users:
     file.shared_with.add(user)
     file.save()
    return redirect('file_manager')


@login_required
def file_share_list(request, file=None):
    if request.is_ajax and request.method == 'GET':
        file = get_object_or_404_template_default(CompanyFile, id=file)
        already_shared = file.shared_with.all
        members = User.objects.filter(company=get_company_object_from_user(request.user.id), user_type=User.EMPLOYEE)

        form_string = render_to_string('file_shared_with.html', {'file': file, 'members': members, 'already_shared': already_shared}, request)
        return JsonResponse({'file_list_to_be_shared': form_string}, status=200)
    else:

        return JsonResponse({'error': 'something went wrong'}, status=400)

