# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, timedelta
from ..constants import NIGERIAN_STATES


class HrEmployeeReport(models.TransientModel):
    """Wizard for generating employee reports"""
    _name = 'hr.employee.report'
    _description = 'HR Employee Report Wizard'
    _inherit = ['mail.thread']

    report_type = fields.Selection([
        ('master', 'Employee Master Report'),
        ('pension', 'Pension Compliance Report'),
        ('retirement', 'Retirement Schedule Report'),
        ('geographical', 'Geographical Distribution Report'),
        ('qualification', 'Qualification Analysis Report'),
    ], string='Report Type', required=True, default='master')

    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    
    state_filter = fields.Selection(NIGERIAN_STATES, string='Filter by State')

    employee_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('retired', 'Retired'),
        ('deceased', 'Deceased'),
        ('terminated', 'Terminated'),
    ], string='Filter by Status')

    def print_report(self):
        """Generate the selected report"""
        data = {
            'report_type': self.report_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'state_filter': self.state_filter,
            'employee_status': self.employee_status,
        }
        
        if self.report_type == 'master':
            return self.env.ref('mda_hr.action_employee_master_report').report_action(self, data=data)
        elif self.report_type == 'pension':
            return self.env.ref('mda_hr.action_pension_compliance_report').report_action(self, data=data)
        elif self.report_type == 'retirement':
            return self.env.ref('mda_hr.action_retirement_schedule_report').report_action(self, data=data)
        elif self.report_type == 'geographical':
            return self.env.ref('mda_hr.action_geographical_report').report_action(self, data=data)
        elif self.report_type == 'qualification':
            return self.env.ref('mda_hr.action_qualification_report').report_action(self, data=data)


class HrEmployeeReportPrint(models.AbstractModel):
    """Abstract model for HR reports"""
    _name = 'mda_hr.employee.report.print'
    _description = 'HR Employee Reports'

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report data based on report type"""
        report_type = data.get('report_type', 'master')
        domain = self._get_employee_domain(data)
        employees = self.env['hr.employee'].search(domain)
        
        if report_type == 'master':
            return self._get_master_report_data(employees, data)
        elif report_type == 'pension':
            return self._get_pension_report_data(employees, data)
        elif report_type == 'retirement':
            return self._get_retirement_report_data(employees, data)
        elif report_type == 'geographical':
            return self._get_geographical_report_data(employees, data)
        elif report_type == 'qualification':
            return self._get_qualification_report_data(employees, data)

    def _get_employee_domain(self, data):
        """Build domain for employee search based on filters"""
        domain = []
        
        if data.get('state_filter'):
            domain.append(('state_of_origin', '=', data['state_filter']))
        
        if data.get('employee_status'):
            domain.append(('employee_status', '=', data['employee_status']))
        
        if data.get('date_from') and data.get('date_to'):
            domain.extend([
                ('date_first_appointment', '>=', data['date_from']),
                ('date_first_appointment', '<=', data['date_to'])
            ])
        
        return domain

    def _get_master_report_data(self, employees, data):
        """Get data for master report"""
        return {
            'doc_ids': employees.ids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'report_type': 'master',
            'company': self.env.company,
            'print_date': fields.Datetime.now(),
        }

    def _get_pension_report_data(self, employees, data):
        """Get data for pension compliance report"""
        permanent_staff = employees.filtered(lambda emp: emp.appointment_type == 'permanent')
        
        with_pfa = permanent_staff.filtered(lambda emp: emp.pfa_name)
        without_pfa = permanent_staff.filtered(lambda emp: not emp.pfa_name)
        with_rsa = permanent_staff.filtered(lambda emp: emp.rsa_pin)
        without_rsa = permanent_staff.filtered(lambda emp: not emp.rsa_pin)
        
        return {
            'doc_ids': permanent_staff.ids,
            'doc_model': 'hr.employee',
            'docs': permanent_staff,
            'report_type': 'pension',
            'company': self.env.company,
            'print_date': fields.Datetime.now(),
            'total_permanent': len(permanent_staff),
            'with_pfa': len(with_pfa),
            'without_pfa': len(without_pfa),
            'with_rsa': len(with_rsa),
            'without_rsa': len(without_rsa),
            'employees_without_pfa': without_pfa,
            'employees_without_rsa': without_rsa,
        }

    def _get_retirement_report_data(self, employees, data):
        """Get data for retirement schedule report"""
        # Filter employees retiring in the next 5 years
        today = date.today()
        five_years_ahead = date(today.year + 5, 12, 31)
        
        retiring_employees = employees.filtered(
            lambda emp: emp.retirement_date and today <= emp.retirement_date <= five_years_ahead
        ).sorted('retirement_date')
        
        # Group by year
        retirement_by_year = {}
        for emp in retiring_employees:
            year = emp.retirement_date.year
            if year not in retirement_by_year:
                retirement_by_year[year] = []
            retirement_by_year[year].append(emp)
        
        return {
            'doc_ids': retiring_employees.ids,
            'doc_model': 'hr.employee',
            'docs': retiring_employees,
            'report_type': 'retirement',
            'company': self.env.company,
            'print_date': fields.Datetime.now(),
            'retirement_by_year': retirement_by_year,
        }

    def _get_geographical_report_data(self, employees, data):
        """Get data for geographical distribution report"""
        # Group by geopolitical zone
        zone_distribution = {}
        state_distribution = {}
        
        for emp in employees:
            # Zone distribution
            zone = emp.geo_political_zone
            if zone:
                zone_display = dict(emp._fields['geo_political_zone'].selection)[zone]
                if zone_display not in zone_distribution:
                    zone_distribution[zone_display] = 0
                zone_distribution[zone_display] += 1
            
            # State distribution
            state = emp.state_of_origin
            if state:
                state_display = dict(emp._fields['state_of_origin'].selection)[state]
                if state_display not in state_distribution:
                    state_distribution[state_display] = 0
                state_distribution[state_display] += 1
        
        return {
            'doc_ids': employees.ids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'report_type': 'geographical',
            'company': self.env.company,
            'print_date': fields.Datetime.now(),
            'zone_distribution': zone_distribution,
            'state_distribution': state_distribution,
            'total_employees': len(employees),
        }

    def _get_qualification_report_data(self, employees, data):
        """Get data for qualification analysis report."""
        qualification_stats = {}
        
        for emp in employees:
            qual = emp.qualification
            if qual:
                # Since qualification is a Char field, use it directly as display value
                if qual not in qualification_stats:
                    qualification_stats[qual] = {
                        'count': 0,
                        'employees': []
                    }
                qualification_stats[qual]['count'] += 1
                qualification_stats[qual]['employees'].append(emp)
        
        return {
            'doc_ids': employees.ids,
            'doc_model': 'hr.employee',
            'docs': employees,
            'report_type': 'qualification',
            'company': self.env.company,
            'print_date': fields.Datetime.now(),
            'qualification_stats': qualification_stats,
            'total_employees': len(employees),
        }