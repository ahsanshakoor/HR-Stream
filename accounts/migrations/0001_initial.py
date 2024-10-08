# Generated by Django 3.0.2 on 2023-01-09 08:43

import accounts.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import home.validator


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_company_users_profile_pics_path, validators=[home.validator.MaxSizeValidator(5)])),
                ('user_code', models.CharField(blank=True, max_length=20, null=True)),
                ('cell', models.CharField(blank=True, max_length=20, null=True)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], default='male', max_length=6)),
                ('user_type', models.CharField(choices=[('employee', 'Employee'), ('client', 'Client')], default='employee', max_length=8)),
                ('joining_date', models.DateField(blank=True, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('on_boarding', models.BooleanField(blank=True, default=False, null=True)),
                ('timezone', models.CharField(blank=True, max_length=50, null=True)),
                ('percentage_401k', models.PositiveSmallIntegerField(default=0)),
                ('apply_401k_before_tax', models.BooleanField(choices=[(True, 'Yes'), (False, 'No')], default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('company_type', models.CharField(blank=True, choices=[('corporation', 'Corporation'), ('LLC', 'LLC'), ('NON_PROFIT', 'Non Profit')], max_length=20, null=True)),
                ('website_url', models.URLField(blank=True, null=True)),
                ('date_established', models.DateField(blank=True, null=True)),
                ('tag_line', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_company_logo_path, validators=[home.validator.MaxSizeValidator(5)])),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('fax', models.CharField(blank=True, max_length=20, null=True)),
                ('country', models.CharField(blank=True, max_length=30, null=True)),
                ('state', models.CharField(blank=True, max_length=30, null=True)),
                ('city', models.CharField(blank=True, max_length=30, null=True)),
                ('zip', models.CharField(blank=True, max_length=10, null=True)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('facebook_url', models.URLField(blank=True, null=True)),
                ('linkedin_url', models.URLField(blank=True, null=True)),
                ('twitter_url', models.URLField(blank=True, null=True)),
                ('currency_code', models.CharField(blank=True, choices=[('ALL', 'Albania - Leke - ALL - Lek'), ('USD', 'America - Dollars - USD - $'), ('AFN', 'Afghanistan - Afghanis - AFN - ؋'), ('ARS', 'Argentina - Pesos - ARS - $'), ('AWG', 'Aruba - Guilders - AWG - ƒ'), ('AUD', 'Australia - Dollars - AUD - $'), ('AZN', 'Azerbaijan - New Manats - AZN - ман'), ('BSD', 'Bahamas - Dollars - BSD - $'), ('BBD', 'Barbados - Dollars - BBD - $'), ('BYR', 'Belarus - Rubles - BYR - p.'), ('EUR', 'Belgium - Euro - EUR - €'), ('BZD', 'Beliz - Dollars - BZD - BZ$'), ('BMD', 'Bermuda - Dollars - BMD - $'), ('BOB', 'Bolivia - Bolivianos - BOB - $b'), ('BAM', 'Bosnia and Herzegovina - Convertible Marka - BAM - KM'), ('BWP', 'Botswana - Pulas - BWP - P'), ('BGN', 'Bulgaria - Leva - BGN - лв'), ('BRL', 'Brazil - Reais - BRL - R$'), ('GBP', 'Britain (United Kingdom) - Pounds - GBP - £'), ('BND', 'Brunei Darussalam - Dollars - BND - $'), ('KHR', 'Cambodia - Riels - KHR - ៛'), ('CAD', 'Canada - Dollars - CAD - $'), ('KYD', 'Cayman Islands - Dollars - KYD - $'), ('CLP', 'Chile - Pesos - CLP - $'), ('CNY', 'China - Yuan Renminbi - CNY - ¥'), ('COP', 'Colombia - Pesos - COP - $'), ('CRC', 'Costa Rica - Colón - CRC - ₡'), ('HRK', 'Croatia - Kuna - HRK - kn'), ('CUP', 'Cuba - Pesos - CUP - ₱'), ('EUR', 'Cyprus - Euro - EUR - €'), ('CZK', 'Czech Republic - Koruny - CZK - Kč'), ('DKK', 'Denmark - Kroner - DKK - kr'), ('DOP', 'Dominican Republic - Pesos - DOP  - RD$'), ('XCD', 'East Caribbean - Dollars - XCD - $'), ('EGP', 'Egypt - Pounds - EGP - £'), ('SVC', 'El Salvador - Colones - SVC - $'), ('GBP', 'England (United Kingdom) - Pounds - GBP - £'), ('EUR', 'Euro - Euro - EUR - €'), ('FKP', 'Falkland Islands - Pounds - FKP - £'), ('FJD', 'Fiji - Dollars - FJD - $'), ('EUR', 'France - Euro - EUR - €'), ('GHC', 'Ghana - Cedis - GHC - ¢'), ('GIP', 'Gibraltar - Pounds - GIP - £'), ('EUR', 'Greece - Euro - EUR - €'), ('GTQ', 'Guatemala - Quetzales - GTQ - Q'), ('GGP', 'Guernsey - Pounds - GGP - £'), ('GYD', 'Guyana - Dollars - GYD - $'), ('EUR', 'Holland (Netherlands) - Euro - EUR - €'), ('HNL', 'Honduras - Lempiras - HNL - L'), ('HKD', 'Hong Kong - Dollars - HKD - HK$'), ('HUF', 'Hungary - Forint - HUF - Ft'), ('ISK', 'Iceland - Kronur - ISK - kr'), ('INR', 'India - Rupees - INR - ₹'), ('IDR', 'Indonesia - Rupiahs - IDR - Rp'), ('IRR', 'Iran - Rials - IRR - ﷼'), ('EUR', 'Ireland - Euro - EUR - €'), ('IMP', 'Isle of Man - Pounds - IMP - £'), ('ILS', 'Israel - New Shekels - ILS - ₪'), ('EUR', 'Italy - Euro - EUR - €'), ('JMD', 'Jamaica - Dollars - JMD - J$'), ('JPY', 'Japan - Yen - JPY - ¥'), ('JEP', 'Jersey - Pounds - JEP - £'), ('KZT', 'Kazakhstan - Tenge - KZT - лв'), ('KPW', 'Korea (North) - Won - KPW - ₩'), ('KRW', 'Korea (South) - Won - KRW - ₩'), ('KGS', 'Kyrgyzstan - Soms - KGS - лв'), ('LAK', 'Laos - Kips - LAK - ₭'), ('LVL', 'Latvia - Lati - LVL - Ls'), ('LBP', 'Lebanon - Pounds - LBP - £'), ('LRD', 'Liberia - Dollars - LRD - $'), ('CHF', 'Liechtenstein - Switzerland Francs - CHF - fr.'), ('LTL', 'Lithuania - Litai - LTL - Lt'), ('EUR', 'Luxembourg - Euro - EUR - €'), ('MKD', 'Macedonia - Denars - MKD - ден'), ('MYR', 'Malaysia - Ringgits - MYR - RM'), ('EUR', 'Malta - Euro - EUR - €'), ('MUR', 'Mauritius - Rupees - MUR - ₨'), ('MXN', 'Mexico - Pesos - MXN - $'), ('MNT', 'Mongolia - Tugriks - MNT - ₮'), ('MZN', 'Mozambique - Meticais - MZN - MT'), ('NAD', 'Namibia - Dollars - NAD - $'), ('NPR', 'Nepal - Rupees - NPR - ₨'), ('ANG', 'Netherlands Antilles - Guilders - ANG - ƒ'), ('EUR', 'Netherlands - Euro - EUR - €'), ('NZD', 'New Zealand - Dollars - NZD - $'), ('NIO', 'Nicaragua - Cordobas - NIO - C$'), ('NGN', 'Nigeria - Nairas - NGN - ₦'), ('KPW', 'North Korea - Won - KPW - ₩'), ('NOK', 'Norway - Krone - NOK - kr'), ('OMR', 'Oman - Rials - OMR - ﷼'), ('PKR', 'Pakistan - Rupees - PKR - ₨'), ('PAB', 'Panama - Balboa - PAB - B/.'), ('PYG', 'Paraguay - Guarani - PYG - Gs'), ('PEN', 'Peru - Nuevos Soles - PEN - S/.'), ('PHP', 'Philippines - Pesos - PHP - ₱'), ('PLN', 'Poland - Zlotych - PLN - zł'), ('QAR', 'Qatar - Rials - QAR - ﷼'), ('RON', 'Romania - New Lei - RON - lei'), ('RUB', 'Russia - Rubles - RUB - руб'), ('SHP', 'Saint Helena - Pounds - SHP - £'), ('SAR', 'Saudi Arabia - Riyals - SAR - ﷼'), ('RSD', 'Serbia - Dinars - RSD - Дин.'), ('SCR', 'Seychelles - Rupees - SCR - ₨'), ('SGD', 'Singapore - Dollars - SGD - $'), ('EUR', 'Slovenia - Euro - EUR - €'), ('SBD', 'Solomon Islands - Dollars - SBD - $'), ('SOS', 'Somalia - Shillings - SOS - S'), ('ZAR', 'South Africa - Rand - ZAR - R'), ('KRW', 'South Korea - Won - KRW - ₩'), ('EUR', 'Spain - Euro - EUR - €'), ('LKR', 'Sri Lanka - Rupees - LKR - ₨'), ('SEK', 'Sweden - Kronor - SEK - kr'), ('CHF', 'Switzerland - Francs - CHF - fr.'), ('SRD', 'Suriname - Dollars - SRD - $'), ('SYP', 'Syria - Pounds - SYP - £'), ('TWD', 'Taiwan - New Dollars - TWD - 元'), ('THB', 'Thailand - Baht - THB - ฿'), ('TTD', 'Trinidad and Tobago - Dollars - TTD - TT$'), ('TRY', 'Turkey - Lira - TRY - ₺'), ('TRL', 'Turkey - Liras - TRL - £'), ('TVD', 'Tuvalu - Dollars - TVD - $'), ('UAH', 'Ukraine - Hryvnia - UAH - ₴'), ('GBP', 'United Kingdom - Pounds - GBP - £'), ('USD', 'United States of America - Dollars - USD - $'), ('UYU', 'Uruguay - Pesos - UYU - $U'), ('UZS', 'Uzbekistan - Sums - UZS - лв'), ('EUR', 'Vatican City - Euro - EUR - €'), ('VEF', 'Venezuela - Bolivares Fuertes - VEF - Bs'), ('VND', 'Vietnam - Dong - VND - ₫'), ('YER', 'Yemen - Rials - YER - ﷼'), ('ZWD', 'Zimbabwe - Zimbabwe Dollars - ZWD - Z$')], max_length=4, null=True)),
                ('currency_sym', models.CharField(blank=True, max_length=8, null=True)),
                ('currency_dir', models.CharField(blank=True, max_length=5, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='accounts.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ManyToManyField(related_name='company_roles', to='accounts.Company')),
            ],
        ),
        migrations.CreateModel(
            name='UserSalary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.DecimalField(decimal_places=0, max_digits=20)),
                ('salary_raise', models.DecimalField(decimal_places=0, default=0, max_digits=20)),
                ('employment_type', models.CharField(choices=[('fulltime', 'Full Time'), ('parttime', 'Part Time'), ('intern', 'Intern')], default='fulltime', max_length=30)),
                ('salary_type', models.CharField(choices=[('hourly', 'Hourly'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], default='yearly', max_length=30)),
                ('comments', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserSalaries', to='accounts.Company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salaries', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('file', models.FileField(max_length=1000, upload_to=accounts.models.get_company_users_files_path, validators=[home.validator.MaxSizeValidator(5)])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserFiles', to='accounts.Company')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userfiles', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RolePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('name_value', models.CharField(blank=True, max_length=30, null=True)),
                ('description', models.CharField(blank=True, max_length=250, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('role', models.ManyToManyField(blank=True, related_name='role_permissions', to='accounts.Role')),
            ],
        ),
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=20, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PersonalInfos', to='accounts.Company')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('job_position', models.CharField(blank=True, max_length=50, null=True)),
                ('period_from', models.DateField(blank=True, null=True)),
                ('period_to', models.DateField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Experiences', to='accounts.Company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_experience', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('relationship', models.CharField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, max_length=18, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='EmergencyContacts', to='accounts.Company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_emergency_contact', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EducationInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('institution', models.CharField(blank=True, max_length=100, null=True)),
                ('degree', models.CharField(blank=True, max_length=50, null=True)),
                ('starting_date', models.DateField(blank=True, null=True)),
                ('ending_date', models.DateField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='EducationInfos', to='accounts.Company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_edu_info', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='company_designations', to='accounts.Company')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='designations', to='accounts.Department')),
            ],
        ),
        migrations.CreateModel(
            name='CompanyClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stakeholder_name', models.CharField(max_length=150)),
                ('first_name', models.CharField(blank=True, max_length=30)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to=accounts.models.get_company_clients_profile_pics_path, validators=[home.validator.MaxSizeValidator(5)])),
                ('client_code', models.CharField(blank=True, max_length=20, null=True)),
                ('cell', models.CharField(blank=True, max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='accounts.Company')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clients_created_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BankInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('routing', models.CharField(blank=True, max_length=20, null=True)),
                ('account_no', models.CharField(blank=True, max_length=30, null=True)),
                ('account_type', models.CharField(blank=True, max_length=30, null=True)),
                ('account_title', models.CharField(blank=True, max_length=50, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='BankInfos', to='accounts.Company')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_bank', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('announced_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='announcements', to='accounts.Company')),
            ],
        ),
    ]
