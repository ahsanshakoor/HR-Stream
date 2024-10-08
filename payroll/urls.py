from django.urls import path
from payroll.views import PayrollPolicyView, \
    edit_payroll_item, delete_payroll_item, PayrollItemView, payrollPolicies, deletePayrollPolicy, \
    editPayrollPolicyStatus, editPayrollPolicy, editPayrollItemStatus, PayrollSalaryView, \
    add_payroll_tax_item, editPayrollTaxItemStatus, edit_tax_payroll_item, delete_payroll_tax_item, \
    healthInsurances, health_insurance_create, health_insurance_edit, health_insurance_delete, \
    health_insurance_status_edit, generate_salary_slip, calculate_salary_slip, manually_add_payroll, employee_payrolls, \
    get_detail_for_payroll, editPayrollPublish, deletePayroll, veiw_salary_slip, unpublished_payroll_search, \
    published_payroll_search, create_n_edit_claim_type, delete_claim_type, company_claim_type, company_claims, \
    create_n_edit_claim, delete_claim, company_claims_admin, claim_status, get_claim_files, claim_search, \
    pending_payroll_search, download_pay_slip, deletePendingPayroll

urlpatterns = [
    # path('payroll/', PayrollView.as_view(), name='payroll'),
    path('payrollPolicy/', PayrollPolicyView.as_view(), name='payroll_policy'),
    path('payrollItem/', PayrollItemView.as_view(), name='payroll_item'),
    path('payrollTaxItem/', add_payroll_tax_item, name='payroll_tax_item'),
    path('payrollItem/<int:pk>/', PayrollItemView.as_view(), name='payroll_item'),
    path('deletePayrollItem/<int:pk>/<int:policy_id>/', delete_payroll_item, name='delete_payroll_item'),
    path('deletePayrollTaxItem/<int:pk>/<int:policy_id>/', delete_payroll_tax_item, name='delete_payroll_tax_item'),
    path('editPayrollItem/<int:pk>/', edit_payroll_item, name='edit_payroll_item'),
    path('editPayrollTaxItem/<int:pk>/', edit_tax_payroll_item, name='edit_payroll_tax_item'),
    path('payrollPolicies/', payrollPolicies, name='payroll_policies'),
    path('deletePayrollPolicy/<int:pk>/', deletePayrollPolicy, name='delete_payroll_policy'),
    path('editPayrollPolicyStatus/<int:pk>/<str:status>/', editPayrollPolicyStatus, name='edit_payroll_policy_status'),
    path('editPayrollItemStatus/<int:pk>/<str:status>/', editPayrollItemStatus, name='edit_payroll_item_status'),
    path('editPayrollTaxItemStatus/<int:pk>/<str:status>/', editPayrollTaxItemStatus, name='edit_payroll_tax_item_status'),
    path('editPayrollPolicy/<int:pk>/', editPayrollPolicy, name='edit_payroll_policy'),
    path('paySlip/', PayrollSalaryView.as_view(), name='payroll_salary'),
    # path('SalarySlip/<int:pk>/', getPaySlip, name='salary_slip'),
    path('calculatePaySlip/<int:pay_id>/', calculate_salary_slip, name='calculate_salary_slip'),
    path('generatePaySlip/<int:pay_id>/', generate_salary_slip, name='generate_salary_slip'),
    path('download_payslip/<int:user_id>/<int:payroll_id>/', download_pay_slip, name='download_pay_slip'),
    # path('SalarySearch/', salarySearch, name='salary_search'),
    path('health-insurances/', healthInsurances, name='health_insurances'),
    path('health-insurance/create/', health_insurance_create, name='health_insurance_create'),
    path('health-insurance/<int:pk>/edit/', health_insurance_edit, name='health_insurance_edit'),
    path('health-insurance/<int:pk>/delete/', health_insurance_delete, name='health_insurance_delete'),
    path('health-insurance-status-edit/<int:pk>/<str:status>/', health_insurance_status_edit, name='health_insurance_status_edit'),
    path('manuallyAddPayroll/', manually_add_payroll, name='manually_add_payroll'),
    path('employee-payrolls/', employee_payrolls, name='employee_payroll'),
    path('editPayrollPublishStatus/<int:pk>/<str:status>/', editPayrollPublish, name='publish_payroll'),
    path('deletePayroll/<int:pk>/', deletePayroll, name='delete_payroll'),
    path('deletePendingPayroll/<int:pk>/', deletePendingPayroll, name='delete_pending_payroll'),
    path('veiwPaySlip/<int:user_id>/<int:payroll_id>/', veiw_salary_slip, name='veiw_salary_slip'),
    path('payroll_detail/<int:payroll_id>/get/', get_detail_for_payroll, name='get_detail_for_payroll'),
    path('unpublished_payroll_search/', unpublished_payroll_search, name='unpublished_payroll_search'),
    path('published_payroll_search/', published_payroll_search, name='published_payroll_search'),
    path('claim_type/', company_claim_type, name='showClaimType'),
    path('claim_type/new/', create_n_edit_claim_type, name='createClaimType'),
    path('claim_type/<int:claim_type_id>/edit/', create_n_edit_claim_type, name='editClaimType'),
    path('claim_type/<int:claim_type_id>/delete/', delete_claim_type, name='deleteClaimType'),
    path('claims/', company_claims, name='showClaims'),
    path('claims_admin/', company_claims_admin, name='showClaimsAdmin'),
    path('claim/new/', create_n_edit_claim, name='createClaim'),
    path('claim/<int:claim_id>/edit/', create_n_edit_claim, name='editClaim'),
    path('claim/<int:claim_id>/delete/', delete_claim, name='deleteClaim'),
    path('update_claim/<int:request_id>/<str:name>', claim_status, name='claim_status_update'),
    path('claim_files/<int:claim_id>/', get_claim_files, name='claim_files'),
    path('claim_search/', claim_search, name='claim_search'),
    path('pending_payroll_search/', pending_payroll_search, name='pending_payroll_search'),


]