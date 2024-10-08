from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View

from accounts.decorators import require_user_access_rights
from accounts.mixins import PerformanceRequiredMixin
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from performance.forms import IndicatorForm, PerformanceForm, PerformanceIndicatorFormSet
from performance.models import Indicator, Performance, PerformanceIndicator


class IndicatorView(LoginRequiredMixin, PerformanceRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        indicator_form = IndicatorForm()
        indicators = Indicator.objects.filter(company=company)
        context = {'indicators': indicators, 'indicator_form': indicator_form}
        return render(request, 'performance-indicator.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        form_class = IndicatorForm(request.POST)
        if form_class.is_valid():
            form = form_class.save(commit=False)
            form.created_by = request.user
            form.company = company
            form.save()
            messages.success(request, 'Indicator Added ')
            return redirect('indicator')
        else:
            messages.error(request, 'Something went Wrong!! Please Try Again')
            return redirect('indicator')


@require_user_access_rights(['owner', 'performance'])
@login_required
def indicator_delete(request, *args, **kwargs):
    try:
        if kwargs.get('pk'):
            Indicator.objects.get(id=kwargs.get('pk')).delete()
            messages.success(request, 'Indicator Deleted')
        return redirect('indicator')
    except:
        messages.error(request, 'Already Deleted')
        return redirect('indicator')


@require_user_access_rights(['owner', 'performance'])
@login_required
def indicator_edit(request, pk=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'GET':
        indicator = get_object_or_404_template_default(Indicator, company=company, id=pk)
        indicatorForm = IndicatorForm(instance=indicator)
        form_string = render_to_string('indicator_edit_form.html',
                                       {'indicator_form': indicatorForm, 'indicator_id': indicator.id}, request)
        return JsonResponse({'indicator_edit_form': form_string}, status=200)
    else:
        return JsonResponse({'error': 'can not edit'}, status=400)


@require_user_access_rights(['owner', 'performance'])
@login_required
def indicator_form_edit(request, pk):
    company = get_company_object_from_user(request.user.id)
    indicator = Indicator.objects.filter(company=company, id=pk).first()
    indicatorForm = IndicatorForm(request.POST, instance=indicator)
    if indicatorForm.is_valid():
        indicatorForm.save()
        messages.success(request, 'Indicator Updated Successfully')
        return redirect('indicator')
    else:
        messages.error(request, 'Something Went Wrong. Please Try Again')
        return redirect('indicator')


class PerformanceView(LoginRequiredMixin, PerformanceRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        performance_form = PerformanceForm(company=company)
        performance_indicator_form = PerformanceIndicatorFormSet(queryset=Indicator.objects.filter(company=company, status=True))
        indicators = Indicator.objects.filter(company=company)
        context = {'indicators': indicators, 'performance_form': performance_form, 'performance_indicator_form': performance_indicator_form}
        return render(request, 'performance.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        form_class = PerformanceIndicatorFormSet(request.POST)
        form_class1 = PerformanceForm(request.POST, company=company)
        if form_class.is_valid() and form_class1.is_valid():
            performance = form_class1.save(commit=False)
            performance.company = company
            performance.created_by = request.user
            performance.save()
            for form in form_class:
                obtained_weightage = form.cleaned_data['obtained_weightage']
                total_weightage = form.cleaned_data['total_weightage']
                indicator = form.cleaned_data['name']
                perfotmance_indicator = PerformanceIndicator(performance=performance, obtained_weightage=obtained_weightage,
                                                             total_weightage=total_weightage, company=company, indicator=indicator)
                perfotmance_indicator.save()
            messages.success(request, 'Performance has been saved')
            return redirect('performance')
        else:
            messages.error(request, 'Something went Wrong!! Please Try Again')
            return redirect('performance')


@require_user_access_rights(['owner', 'performance'])
@login_required
def performance_delete(request, *args, **kwargs):
    try:
        if kwargs.get('pk'):
            Performance.objects.get(id=kwargs.get('pk')).delete()
            messages.success(request, 'Performance Deleted')
        return redirect('performance_list')
    except:
        messages.error(request, 'Already Deleted')
        return redirect('performance_list')


class PerformanceListView(LoginRequiredMixin, PerformanceRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        performances = Performance.objects.filter(company=company)
        list = []
        for performance in performances:
            dict = {
                'performance': performance,
                'total': PerformanceIndicator.objects.filter(performance=performance).aggregate(Sum('total_weightage')),
                'obtained': PerformanceIndicator.objects.filter(performance=performance).aggregate(Sum('obtained_weightage'))
            }
            list.append(dict)
        context = {'performances': list}
        return render(request, 'performance-list.html', context)



@login_required
def performance_graph(request, pk=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'GET':
        if pk is not None:
            performance = Performance.objects.filter(id=pk, company=company).first()
            performance_indicators = PerformanceIndicator.objects.filter(performance=performance, company=company)
            list_indicator_name = []
            list_indicator_obtained = []
            list_indicator_total = []
            for p_i in performance_indicators:
                list_indicator_name.append(p_i.indicator)
                list_indicator_obtained.append(p_i.obtained_weightage)
                list_indicator_total.append(p_i.total_weightage)
            list = [{'name': list_indicator_name,
                     'obtained': list_indicator_obtained,
                     'total': list_indicator_total}]
            return JsonResponse({'data': list}, status=200)
    return JsonResponse({'error': ''}, status=400)


@require_user_access_rights(['owner', 'performance'])
@login_required
def performance_graph_detail(request, pk=None):
    company = get_company_object_from_user(request.user.id)
    if pk is not None:
        performance = Performance.objects.filter(id=pk, company=company).first()
        context = {'performance': performance}
        return render(request, 'performance-graph.html', context)
    messages.error(request, "Can't Find Details For The Performance")
    return redirect('performance_list')


class PerformanceEmployeeView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        performances = Performance.objects.filter(company=company, employee=request.user, published=True)
        context = {'performances': performances}
        return render(request, 'performance-employee.html', context)


@login_required
def employee_performance_detail(request, performance_id=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'GET':
        if performance_id is not None:
            performance = Performance.objects.filter(id=performance_id, company=company).first()
            performance_indicators = PerformanceIndicator.objects.filter(performance=performance, company=company)
            list_indicator_name = []
            list_indicator_obtained = []
            list_indicator_total = []
            comment = performance.comment
            for p_i in performance_indicators:
                list_indicator_name.append(p_i.indicator)
                list_indicator_obtained.append(p_i.obtained_weightage)
                list_indicator_total.append(p_i.total_weightage)
            list = [{'name': list_indicator_name,
                     'obtained': list_indicator_obtained,
                     'total': list_indicator_total}]
            return JsonResponse({'data': list, 'comment': comment}, status=200)
    return JsonResponse({'error': ''}, status=400)


@require_user_access_rights(['owner', 'performance'])
@login_required
def publish_performance(request, performance_id=None):
    if performance_id:
        company = get_company_object_from_user(request.user.id)
        try:
            performance = Performance.objects.get(company=company, id=performance_id)
            if performance.published is True:
                performance.published = False
            else:
                performance.published = True
            performance.save()
            messages.success(request, 'Performance is Published')
            return redirect('performance_list')
        except:
                messages.error(request, 'Performance does not exist')
                return redirect('performance_list')
