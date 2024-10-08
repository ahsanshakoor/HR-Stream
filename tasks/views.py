import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, ProtectedError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View

from accounts.decorators import require_user_access_rights
from accounts.models import User
from accounts.utils import get_company_object_from_user, is_user_owner
from project.forms import ProjectForm, ProjectFileForm
from project.models import Project
from project.views import get_project_custom_id
from tasks.forms import TaskForm, TaskBoardForm, TaskBoardEditForm, BoardForm, CardForm, addTaskForm, CardFileFormSet
from tasks.models import Task, Board, Card, CardFile


class TaskView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        p_code = get_project_custom_id(request)
        form_class = ProjectForm(request, initial={'code': p_code})
        form_class1 = ProjectFileForm()
        clients = User.objects.filter(company=company)
        projects = Project.objects.filter(company=company)
        project = Project.objects.filter(company=company).first()
        if kwargs:
            project = Project.objects.get(id=kwargs.get('pk'))
        task_form = TaskForm(initial={'project': project})
        context = {'form': form_class, 'fileform': form_class1, 'task_form': task_form, 'projects': projects,
                   'project': project,
                   'clients': clients}
        return render(request, 'tasks.html', context)

    def post(self, request, *args, **kwargs):
        task_form = TaskForm(request.POST)
        pk = request.POST.get('project')
        if task_form.is_valid():
            task = task_form.save(commit=False)
            task.created_by = request.user
            task.save()
            return redirect('tasks_project', pk)
        else:
            messages.error(request, 'Something Went Wrong Please Try Again')
            return redirect('tasks')


def update_task_status(request, pk):
    task = Task.objects.get(id=pk)
    if task.status == Task.FINISHED:
        task.status = Task.PENDING
    else:
        task.status = Task.FINISHED
    task.save()
    return HttpResponse('success')


def delete_task(request, pk):
    task = Task.objects.get(id=pk)
    task.delete()
    return HttpResponse('success')


def delete_task_from_board(request, pk):
    task = Task.objects.get(id=pk)
    id = task.project.id
    task.delete()
    return redirect('task_board', id)


def assign_task_modal(request, **kwargs):
    project = Project.objects.get(id=kwargs.get('project_id'))
    task = Task.objects.get(id=kwargs.get('task_id'))
    members = User.objects.filter(id__in=project.team.all()).exclude(id__in=task.assign_to.all())
    # members = Project.objects.filter(id=kwargs.get('project_id')).exclude()
    if request.is_ajax and request.method == 'GET':
        form_string = render_to_string('assign-modal.html',
                                       {'task_id': task.id, 'project': project, 'members': members}, request)
        return JsonResponse({'project_task_modal': form_string}, status=200)
    messages.error(request, 'Processing Error!. Try Again')
    return redirect('tasks')


def assign_task(request, **kwargs):
    task = Task.objects.get(id=kwargs.get('task'))
    user = User.objects.get(id=kwargs.get('assignee'))
    task.assign_to.add(user)
    task.save()
    pk = task.project.id
    return redirect('tasks_project', pk)


def open_chat(request, **kwargs):
    task = Task.objects.get(id=kwargs.get('pk'))
    if request.is_ajax and request.method == 'GET':
        form_string = render_to_string('task-chat.html.html', {'taskid': task}, request)
        return JsonResponse({'task-modal': form_string}, status=200)
    messages.error(request, 'Processing Error!. Try Again')
    return redirect('tasks')


class TaskBoardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        project = Project.objects.get(id=kwargs.get('pk'))
        pending = Task.objects.filter(project=project, status=Task.PENDING)
        in_progress = Task.objects.filter(project=project, status=Task.IN_PROGRESS)
        finished = Task.objects.filter(project=project, status=Task.FINISHED)
        on_hold = Task.objects.filter(project=project, status=Task.ON_HOLD)
        under_review = Task.objects.filter(project=project, status=Task.UNDER_REVIEW)
        membersLead = User.objects.filter(company=company).exclude(id=project.lead_by.id)
        members = User.objects.filter(company=company).exclude(id__in=project.team.all())
        board_form = BoardForm(initial={'project': project})
        card_form = CardForm(company=company)
        boards = Board.objects.filter(project=project).prefetch_related('board_cards').order_by('created_at')
            # .prefetch_related(Prefetch('board_cards__assign_to', queryset=User.objects.filter(id__in=project.team.all()).prefetch_related('card_assignee')))
        # .prefetch_related('board_cards', 'board_cards__assign_to')
        # print(boards[0].board_cards.first())
        form = TaskBoardForm(initial={'project': project, 'due_date': datetime.datetime.now().date()})
        context = {'project': project, 'pending': pending, 'in_progress': in_progress, 'finished': finished,
                   'on_hold': on_hold, 'under_review': under_review, 'form': form, 'members': members,
                   'membersLead': membersLead,
                   'board_form': board_form, 'card_form': card_form, 'boards': boards}
        return render(request, 'task-board.html', context)


class ArchivedTaskBoardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        project = Project.objects.get(id=kwargs.get('pk'))
        pending = Task.objects.filter(project=project, status=Task.PENDING)
        in_progress = Task.objects.filter(project=project, status=Task.IN_PROGRESS)
        finished = Task.objects.filter(project=project, status=Task.FINISHED)
        on_hold = Task.objects.filter(project=project, status=Task.ON_HOLD)
        under_review = Task.objects.filter(project=project, status=Task.UNDER_REVIEW)
        membersLead = User.objects.filter(company=company).exclude(id=project.lead_by.id)
        members = User.objects.filter(company=company).exclude(id__in=project.team.all())
        board_form = BoardForm(initial={'project': project})
        card_form = CardForm(company=company)
        boards = Board.objects.filter(project=project).prefetch_related('board_cards').order_by('created_at')
            # .prefetch_related(Prefetch('board_cards__assign_to', queryset=User.objects.filter(id__in=project.team.all()).prefetch_related('card_assignee')))
        # .prefetch_related('board_cards', 'board_cards__assign_to')
        # print(boards[0].board_cards.first())
        form = TaskBoardForm(initial={'project': project, 'due_date': datetime.datetime.now().date()})
        context = {'project': project, 'pending': pending, 'in_progress': in_progress, 'finished': finished,
                   'on_hold': on_hold, 'under_review': under_review, 'form': form, 'members': members,
                   'membersLead': membersLead,
                   'board_form': board_form, 'card_form': card_form, 'boards': boards}
        return render(request, 'atask-board.html', context)


def add_task_to_board(request, **kwargs):
    form = TaskBoardForm(request.POST)
    pk = TaskBoardForm(request.POST.get('project'))
    if form.is_valid():
        task = form.save(commit=False)
        task.created_by = request.user
        task.status = kwargs.get('type')
        task.save()
        form._save_m2m()
        pk = task.project.id
        messages.success(request, 'Task has benn add to the board')
        return redirect('task_board', pk)
    else:
        messages.error(request, 'Something went Wrong!! Please Try Again')
        return redirect('task_board', pk)


def edit_task_form(request, *args, **kwargs):
    task = Task.objects.get(id=kwargs.get('pk'))
    pk = task.project.id
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        form = TaskBoardEditForm(request, request.POST, instance=task, company=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task Update Successful!')
            return redirect('task_board', pk)
        else:
            print(form.errors)
            messages.error(request, 'Task Not Updated!')
            return redirect('task_board', pk)
    if request.is_ajax and request.method == 'GET':
        form = TaskBoardEditForm(request, instance=task, company=company)
        form_string = render_to_string('taskBoardForm.html', {'form': form, 'task_id': task.id}, request)
        return JsonResponse({'task_add_form': form_string}, status=200)
    messages.error(request, 'Processing Error!. Try Again')
    return redirect('projects')


def add_task_form(request, *args, **kwargs):
    project = Project.objects.get(id=kwargs.get('pk'))
    id = project.id
    status = kwargs.get('status')
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        form = addTaskForm(request, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.status = status
            task.save()
            form._save_m2m()
            messages.success(request, 'Task Added Successful!')
            return redirect('task_board', id)
        else:
            messages.error(request, 'Task Not Added!')
            return redirect('task_board', id)
    if request.is_ajax and request.method == 'GET':
        form = addTaskForm(request, initial={'project': project})
        form_string = render_to_string('addTaskForm.html', {'form': form, 'project_id': project.id, 'status': status},
                                       request)
        return JsonResponse({'task_add_form': form_string}, status=200)

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
    return redirect('task_board', pk)


@require_user_access_rights(['owner', 'projects'])
@login_required
def assign_lead(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.get(id=kwargs.get('project'), company=company)
    user = User.objects.get(id=kwargs.get('user'), company=company)
    project.lead_by = user
    project.save()
    pk = project.id
    return redirect('task_board', pk)


@require_user_access_rights(['owner', 'projects'])
@login_required
def add_board(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    form = BoardForm(request.POST)
    if form.is_valid():
        board = form.save(commit=False)
        board.color = request.POST.get('radio')
        board.company = company
        board.save()
        messages.success(request, board.name + ' Board has been added to project ' + board.project.name)
        pk = board.project.id
        return redirect('task_board', pk)
    else:
        pk = request.POST.get('project')
        messages.error(request, 'Something went wrong.Please Try Again!!!')
        return redirect('task_board', pk)


@require_user_access_rights(['owner', 'projects'])
@login_required
def edit_task_board_form(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    board = Board.objects.get(id=kwargs.get('pk'), company=company)
    pk = board.project.id
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            board_form = form.save(commit=False)
            board_form.color = request.POST.get('radio')
            board_form.save()
            messages.success(request, board_form.name + ' Board Updated Successful!')
            return redirect('task_board', pk)
        else:
            messages.error(request, 'Board Not Updated!')
            print(form.errors)
            return redirect('task_board', pk)

    if request.is_ajax and request.method == 'GET':
        form = BoardForm(instance=board)
        form_string = render_to_string('BoardEditForm.html', {'board_form': form, 'board_id': board.id}, request)
        return JsonResponse({'task_board_edit_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('projects')


@require_user_access_rights(['owner', 'projects'])
@login_required
def delete_board(request, pk):
    board = None
    company = get_company_object_from_user(request.user.id)
    if Board.objects.filter(company=company, id=pk).exists():
        board = Board.objects.get(company=company, id=pk)
    if board is not None:
        try:
            board.delete()
            messages.success(request, 'Leave Type has been deleted')
        except ProtectedError as e:
            messages.error(request, "Some Thing Went Wrong.Reload The Page")
    id = board.project.id
    return redirect('task_board', id)


@login_required
def add_card(request, pk):
    company = get_company_object_from_user(request.user.id)
    board = Board.objects.get(id=pk, company=company)
    id = board.project.id
    if request.method == 'POST':
        form = CardForm(request.POST, company=company)
        fileformset = CardFileFormSet(request.POST, request.FILES)
        if form.is_valid() and fileformset.is_valid():
            card_form = form.save(commit=False)
            card_form.created_by = request.user
            card_form.company = company
            card_form.save()
            form.save_m2m()
            for f in fileformset:
                file1 = f.save(commit=False)
                file1.company = company
                file1.card = card_form
                file1.save()
            messages.success(request, card_form.name + ' has been Successfully added to Board ' + board.name)
            return redirect('task_board', id)
        else:
            # print(form.cleaned_data)
            messages.error(request, 'Card Not Added. Try Again. ')
            return redirect('task_board', id)
    if request.is_ajax and request.method == 'GET':
        form = CardForm(initial={'board': board}, company=company)
        fileformset = CardFileFormSet()
        form_string = render_to_string('addCard.html', {'form': form, 'board_id': board.id, 'fileformset':fileformset}, request)
        return JsonResponse({'add_card_form': form_string}, status=200)
    messages.error(request, 'Processing Error!. Try Again')
    return redirect('projects')


@login_required
def edit_card_form(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    card = Card.objects.get(id=kwargs.get('pk'), company=company)
    pk = card.board.project.id
    card_files = CardFile.objects.filter(company=company, card=card).all()
    if request.method == 'POST':
        form = CardForm(request.POST, instance=card, company=company)
        fileformset = CardFileFormSet(request.POST, request.FILES, instance=card, queryset=card_files)
        if form.is_valid() and fileformset.is_valid():
            card_form = form.save(commit=False)
            card_form.save()
            for f in fileformset:
                file1 = f.save(commit=False)
                file1.company = company
                file1.card = card_form
                file1.save()
            messages.success(request, card.name + ' Card Update Successful in Board ' + card.board.name)
            return redirect('task_board', pk)
        else:
            messages.error(request, 'Task Not Updated!')
            print(form.errors)
            return redirect('task_board', pk)

    if request.is_ajax and request.method == 'GET':
        form = CardForm(instance=card, company=company)
        fileformset = CardFileFormSet(instance=card, queryset=card_files)
        form_string = render_to_string('EditCardForm.html', {'form': form, 'card_id': card.id, 'fileformset': fileformset}, request)
        return JsonResponse({'card_edit_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('projects')


@login_required
def get_card(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    card = Card.objects.prefetch_related('cardfiles').get(id=kwargs.get('pk'), company=company)
    if request.is_ajax and request.method == 'GET':
        form = CardForm(instance=card, company=company)
        form_string = render_to_string('GetCardForm.html', {'form': form, 'card_id': card.id, 'card': card}, request)
        return JsonResponse({'card_get_form': form_string}, status=200)


@login_required
def delete_card(request, pk):
    card = None
    company = get_company_object_from_user(request.user.id)
    if Card.objects.filter(company=company, id=pk).exists():
        card = Card.objects.get(company=company, id=pk)
    if card is not None:
        try:
            card.delete()
            messages.success(request, 'Card has been deleted')
        except ProtectedError as e:
            messages.error(request, "Some Thing Went Wrong.Reload The Page")
    id = card.board.project.id
    return redirect('task_board', id)


@require_user_access_rights(['owner', 'projects', 'basic'])
@login_required
def update_card_status(request, pk):
    company = get_company_object_from_user(request.user.id)
    card = Card.objects.get(id=pk, company=company)
    if card.status == Card.FINISHED:
        card.status = Card.PENDING
    else:
        card.status = Card.FINISHED
    card.save()
    return HttpResponse('success')


@login_required
def update_task_status_on_board_change(request, project_id):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        task_id = request.POST.get('taskid')
        task_status = request.POST.get('dBoardStatus')
        task = Task.objects.get(project=project_id, id=task_id, company=company)
        task.status = task_status
        task.save()
        # print(task_status)
        return JsonResponse({'success': 'Task is updated'}, status=200)


@login_required
def update_card_on_board_change(request, project_id):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        cardId = request.POST.get('cardId')
        dBoardId = request.POST.get('dBoardId')
        sBoardId = request.POST.get('sBoardId')

        dBoard = Board.objects.get(id=dBoardId, company=company)
        sBoard = Board.objects.get(id=sBoardId, company=company)
        card = Card.objects.get(id=cardId, company=company)
        card.board = dBoard
        card.save()
        return JsonResponse({'success': 'Task is updated'}, status=200)


@login_required
def expand_tasks_list(request, project_id, board_id):
    company = get_company_object_from_user(request.user.id)
    project = Project.objects.filter(id=project_id, company=company).select_related('lead_by').prefetch_related('team').first()
    cards = board = None

    if project:
        if is_user_owner(request.user.id) or project.team.filter(id=request.user.id).exists() or project.lead_by.id == request.user.id:
            board = Board.objects.get(id=board_id, company=company)
            cards = Card.objects.filter(board=board, company=company).all()
        else:
            return render(request, 'light/error-404.html')
    else:
        return render(request, 'light/error-404.html')

    return render(request, 'expand_tasks_list.html', {'cards': cards, 'board': board})


def toggle_archive_tasks(request, status, card_id):
    company = get_company_object_from_user(request.user.id)
    card = Card.objects.filter(id=card_id, company=company).select_related('board__project').first()
    if status == 'archive':
        card.archived = True
        card.save()
        return redirect('task_board', card.board.project.id)
    else:
        card.archived = False
        card.save()
        return redirect('atask_board', card.board.project.id)

