from datetime import datetime,timezone
import datetime as datetime
from dateutil import relativedelta
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from accounts.utils import get_company_object_from_user
from checkin.models import CheckIn
from todo.models import Todo


class CheckInView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        users = company.users.values_list('id', flat=True)
        # template_name = 'checkinDetails.html'
        template_name = '../templates/attendance-employee.html'
        todos = Todo.objects.all()
        status = CheckIn.objects.filter(name=self.request.user).last()
        count = Todo.objects.filter(is_read=False,created_by=request.user).count()
        checkins = CheckIn.objects.filter(name__in=users)
        checkin_date = []
        checkin_hour = []
        for checkin in checkins:
            checkin_date.append(checkin.checkin.date())
            checkin_hour.append(checkin.hour)
        context ={'todos': todos, 'count': count, 'status': status, 'checkins': checkins, 'checkin_date': checkin_date, 'checkin_hour': checkin_hour}
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            status = CheckIn.objects.filter(name=self.request.user).last()
            if status != None:
                tz_info = status.checkin.tzinfo
            datetime_str = request.POST.get('datetime')
            if datetime_str == '':
                messages.error(request, 'Date Time can not be empty')
                return redirect(reverse('index'))
            date = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M %p')
            if status == None or status.is_active == False:
                if status != None:
                    if status.checkout.date() == datetime.datetime.now().date():
                        messages.error(request, 'Already Checked In Today')
                        return redirect(reverse('index'))
                if date.date() > datetime.datetime.now().date():
                    messages.error(request, 'Check in time must not be in future!')
                    return redirect(reverse('index'))
                comment = request.POST.get('comment')
                checkin = CheckIn(name=self.request.user, checkin=date, comment=comment, is_active=True)
                checkin.save()
                messages.success(request, 'Check In SuccessFully!')
                return redirect(reverse('index'))
            else:
                if date.date() > datetime.datetime.now().date():
                    messages.error(request, 'Check out time must not be in future!')
                    return redirect(reverse('index'))
                if date.replace(tzinfo=tz_info) < status.checkin:
                    messages.error(request, 'Check out time must not be in past')
                    return redirect(reverse('index'))
                status.comment = request.POST.get('comment')
                date = date.replace(tzinfo=tz_info)
                hours = total_hours(date, status.checkin)
                status.checkout = date
                status.is_active = False
                status.hour = hours
                status.save()
                messages.success(request, 'Check Out SuccessFully!')
            return redirect(reverse('index'))


class SingleCheckin(LoginRequiredMixin, View):

    def get(self, request , *args, **kwargs):
        singlecheckin = CheckIn.objects.get(id=kwargs.get('pk'))
        date = singlecheckin.checkin.date()
        tz_info = singlecheckin.checkin.tzinfo
        checkin_time = singlecheckin.checkin.time()
        checkout_time = singlecheckin.checkout
        if checkout_time != None:
            hours = total_hours(checkout_time, singlecheckin.checkin)
            checkout_time = checkout_time.time()
        else:
            now = datetime.datetime.now(tz=tz_info)
            hours = total_hours(now, singlecheckin.checkin)
        context = {'checkin': singlecheckin, 'date': date, 'hours': hours, 'checkin_time': checkin_time, 'checkout_time': checkout_time}
        return render(request, 'singleCheckin.html', context)


class DeleteCheckin(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            CheckIn.objects.get(id=kwargs.get('pk')).delete()
            return redirect(reverse('checkin'))


def total_hours(checkout_time, checkin_time):
    hours = relativedelta.relativedelta(checkout_time, checkin_time)
    year = hours.years
    year = year * 365 * 24
    month = hours.months
    month = month * 30 * 24
    day = hours.days
    day = day * 24
    hour = hours.hours
    minute = hours.minutes
    minute = minute / 60
    hours = year + day + month + minute + hour
    hours = round(hours, 2)
    return hours

