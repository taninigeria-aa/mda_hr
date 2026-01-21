# mda_hr/models/promotion_schedule.py
from odoo import models, fields, api
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class HrPromotionSchedule(models.Model):
    _name = 'mda.hr.promotion.schedule'
    _description = 'Promotion Schedule'

    name = fields.Char(string='Promotion Name', required=True)
    promotion_year = fields.Integer(string='Promotion Year', required=True)
    min_years_in_grade = fields.Integer(string='Minimum Years in Grade', default=3)

    exam_date = fields.Date(string='Examination Date')
    interview_start = fields.Date(string='Interview Start')
    interview_end = fields.Date(string='Interview End')
    board_approval_date = fields.Date(string='Board Approval Date')
    effective_date = fields.Date(string='Effective Date of Promotion')

    eligible_employee_ids = fields.Many2many('hr.employee', string='Eligible Employees')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('screening', 'Screening'),
        ('exam', 'Examination'),
        ('approval', 'Approval'),
        ('closed', 'Closed')
    ], default='draft')

    @api.model
    def compute_eligible_employees(self):
        """Compute eligible employees based on time-in-grade."""
        today = date.today()
        eligible = self.env['hr.employee'].search([])
        eligible_ids = []
        
        for emp in eligible:
            if emp.date_present_appointment:
                # Use relativedelta for accurate year-based calculation
                cutoff_date = today - relativedelta(years=self.min_years_in_grade)
                if emp.date_present_appointment <= cutoff_date:
                    eligible_ids.append(emp.id)
        
        self.eligible_employee_ids = [(6, 0, eligible_ids)]
