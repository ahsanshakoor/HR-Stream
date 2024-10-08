import datetime
import decimal
import os

import pendulum
from django import template
# from accounts.models import User, Role
from accounts.models import User
from accounts.utils import user_has_access, get_company_object_from_user
from leave.models import LeaveRequest
from payroll.models import Payroll, PayrollPolicy
from payroll.utils import get_all_users_whose_payroll_ready_to_generate


def do_if_has_access(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, user_id, access_rights = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly three arguments i.e, %r tag id_of_the_current_user 'list of access rights'" %
            (token.contents.split()[0], token.contents.split()[0]))

    if not (access_rights[0] == access_rights[-1] and access_rights[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)

    access_rights = access_rights.strip("'")
    nodelist_true = parser.parse(('else', 'endif_has_access'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_has_access',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    # print(access_rights.split())
    return AccessRightsNode(user_id, access_rights, nodelist_true, nodelist_false)


class AccessRightsNode(template.Node):
    def __init__(self, user_id, access_rights, nodelist_true, nodelist_false):
        self.user_id = template.Variable(user_id)
        self.access_rights_list = access_rights.split()
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        try:
            user_id = self.user_id.resolve(context)
        except template.VariableDoesNotExist:
            raise template.TemplateSyntaxError("user id %r is not resolved" % self.user_id)

        if user_has_access(user_id, self.access_rights_list):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


def do_get_company_object(parser, token):
    try:
        tag_name, user_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires only one argument i.e user id" % token.contents.split()[0])
    return GetCompanyObjectNode(user_id)


class GetCompanyObjectNode(template.Node):
    def __init__(self, user_id):
        self.user_id = template.Variable(user_id)

    def render(self, context):
        user_id = self.user_id.resolve(context)
        company = get_company_object_from_user(user_id)
        context['company_name'] = company
        return ''


def do_get_count_object(parser, token):
    try:
        tag_name, user_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires only one argument i.e user id" % token.contents.split()[0])
    return GetCountObjectNode(user_id)


class GetCountObjectNode(template.Node):
    def __init__(self, user_id):
        self.user_id = template.Variable(user_id)

    def render(self, context):
        user_id = self.user_id.resolve(context)
        All_Users = get_all_users_whose_payroll_ready_to_generate(user_id)
        company = get_company_object_from_user(user_id)
        # now = datetime.datetime.now().date()
        # end_of_year = pendulum.date(now.year, now.month, now.day).end_of('year')
        # end_of_month = pendulum.date(now.year, now.month, now.day).end_of('month')
        # week_start_of_end_of_month = end_of_month - datetime.timedelta(days=end_of_month.weekday())  # Monday
        # end_of_month = week_start_of_end_of_month + datetime.timedelta(days=4)  # Friday
        # week_start_of_end_of_year = end_of_year - datetime.timedelta(days=end_of_year.weekday())  # Monday
        # end_of_year = week_start_of_end_of_year + datetime.timedelta(days=4)  # Friday
        # start_of_week = now - datetime.timedelta(days=now.weekday())  # Monday
        # end_of_week = start_of_week + datetime.timedelta(days=4)  # Fridday
        # mid_of_month = now.replace(day=15)
        # start_of_bi_week = mid_of_month - datetime.timedelta(days=mid_of_month.weekday())  # Monday
        # end_of_bi_week = start_of_bi_week + datetime.timedelta(days=4)  # fridayday
        # count = 0
        # all_users = User.objects.filter(company=company)
        # for user in all_users:
        #     if user.payroll_policy is not None:
        #         if user.payroll_policy.payroll_cycle == PayrollPolicy.YEARLY and end_of_year == now:
        #             count += 1
        #         elif user.payroll_policy.payroll_cycle == PayrollPolicy.MONTHLY and end_of_month == now:
        #             count += 1
        #         elif user.payroll_policy.payroll_cycle == PayrollPolicy.WEEKLY and end_of_week == now:
        #             count += 1
        #         elif user.payroll_policy.payroll_cycle == PayrollPolicy.BI_WEEKLY and end_of_bi_week == now or end_of_month == now:
        #             count += 1
        leave_count = LeaveRequest.objects.filter(employee__leave_policy__company=company,
                                                  status='New', employee__report_to=user_id).count()
        context['leave_count'] = leave_count
        # context['payroll_count'] = count

        context['payroll_count'] = All_Users.count()
        return ''


register = template.Library()
register.tag('if_has_access', do_if_has_access)
register.tag('get_company_object', do_get_company_object)
register.tag('get_count_object', do_get_count_object)


@register.filter
def getfilename(value):
    return os.path.basename(value.file.name)


@register.filter(name='subtract')
def subtract(value, arg):
    return round(decimal.Decimal(value) - decimal.Decimal(arg), 2)


@register.filter(name='subtractLeave')
def subtractLeave(value, arg):
    return value - arg


@register.filter(name='subtractTime')
def subtractTime(exit, enter):
    enter_delta = datetime.timedelta(hours=enter.hour, minutes=enter.minute, seconds=enter.second)
    exit_delta = datetime.timedelta(hours=exit.hour, minutes=exit.minute, seconds=exit.second)
    difference_delta = exit_delta - enter_delta
    return round(difference_delta.total_seconds() / 3600, 2)
