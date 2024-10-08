from rest_framework import serializers

from payroll.models import Payroll, SalaryAdjustment, PayrollTax


class SalaryAdjustmentSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = SalaryAdjustment
        fields = '__all__'


class PayrollTaxSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = PayrollTax
        fields = '__all__'


class PayrollSerializer(serializers.ModelSerializer):
    salary_adjustment = SalaryAdjustmentSerializer(many=True, source='payroll_salary_adjustments')
    payroll_tax = PayrollTaxSerializer(many=True, source='payroll_taxes')

    class Meta(object):
        model = Payroll
        fields = '__all__'
        depth = 1