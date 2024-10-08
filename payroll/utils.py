from django.utils import timezone

from accounts.models import User
from accounts.utils import get_company_object_from_user
from .models import PayrollPolicy


from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa


def get_all_users_whose_payroll_ready_to_generate(user_id):
    company = get_company_object_from_user(user_id)
    policies = PayrollPolicy.objects.filter(company=company)
    users = User.objects.none()
    if policies:
        now = timezone.now().date()
        for policy in policies:
            if now > policy.next_pay_period_end_date:
                u = User.objects.filter(payroll_policy=policy, company=company)
                users |= u
    return users


def render_to_pdf(template_src, context_dict={}):
    current_date='ac'
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PaySlip_{current_date}.pdf"'
        return response
        # return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse()
