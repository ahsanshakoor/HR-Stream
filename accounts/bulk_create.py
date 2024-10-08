from .models import RolePermission, Role

perms_list = [
    RolePermission(name='Basic', name_value='basic' ,description='All roles are defined with basic, Giving access to leaves system, attendance system and other basic functionality of HRStream.'),
    RolePermission(name='New Employees', name_value='new_employees' , description='Hire/Add new employees on companies behalf.'),
    RolePermission(name='Payrolls', name_value='payrolls' , description='Process payrolls for all employees on companies behalf, including deductions and other benefits.'),
    RolePermission(name='Company', name_value='company' , description='Edit company profile including locations and other company related details.'),
    RolePermission(name='Leave Policies', name_value='leave_policies' , description='Create and view company leave policies.'),
    RolePermission(name='Roles', name_value='roles' , description='Create and view company roles.'),
    RolePermission(name='Bank Info', name_value='bank_info' , description='Create and view employees bank info on company behalf.'),
    RolePermission(name='New Stakeholders', name_value='new_clients' , description='Add new clients on companies behalf.'),
    RolePermission(name='Attendance Policies', name_value='attendance_policies' , description='Add/Edit attendance policies on company behalf.'),
    RolePermission(name='Admin Dashboard', name_value='admin_dashboard' , description='Access to Admin Dashboard.'),
    RolePermission(name='Projects', name_value='projects', description='Manage projects on company behalf.'),
    RolePermission(name='Policies', name_value='policies', description='Manage all policies on company behalf.'),
    RolePermission(name='Departments', name_value='department', description='Manage Departments on company behalf.'),
    RolePermission(name='Designations', name_value='designations', description='Manage Designations on company behalf.'),
    RolePermission(name='Health Insurance', name_value='health_insurance' , description='manage health insurances for all employees on company behalf.'),
    RolePermission(name='Owner', name_value='owner', description='Owner of the company'),
    RolePermission(name='Announcement', name_value='announcement', description='Announcement for  company'),
    RolePermission(name='Equipments', name_value='equipment', description='Equipment of the company'),
    RolePermission(name='Time Logs', name_value='timelog', description='Time Log of company'),
    RolePermission(name='Claim', name_value='claim', description='Claims of company'),
    RolePermission(name='User Activation/Deactivation', name_value='activation_deactivation', description='Time Log of company'),
    RolePermission(name='Bookmarks', name_value='bookmark', description='Bookmarks of company'),
    RolePermission(name='Performance', name_value='performance', description='Performance of company'),
    RolePermission(name='File Manager', name_value='file_manager', description='Files of company'),
    # RolePermission(name='Attendance Requests', name_value='attendance_requests', description='Manage attendance requests'),

]


def create_objects():
    for p in perms_list:
        if not RolePermission.objects.filter(name_value=p.name_value).exists():
            RolePermission.objects.create(name=p.name, name_value=p.name_value, description=p.description)

    if not Role.objects.filter(name='Owner').exists():
        r = Role.objects.create(name='Owner')
        p = RolePermission.objects.get(name_value='owner')
        p.role.add(r)

    if not Role.objects.filter(name='all_company_clients_role__').exists():
        r = Role.objects.create(name='all_company_clients_role__')
        p = RolePermission.objects.get(name_value='projects')
        p.role.add(r)

    # RolePermission.objects.bulk_create(perms_list)
    # r = Role.objects.create(name='Owner')
    # p = RolePermission.objects.get(name_value='owner')
    # p.role.add(r)


def update_permission_names():
    for p in perms_list:
        permission = RolePermission.objects.filter(name_value=p.name_value).first()
        if permission:
            permission.name = p.name
            permission.save()
