# mda_hr/models/promotion_history.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ..constants import SALARY_GRADE_LEVELS


class HrPromotionHistory(models.Model):
    _name = 'mda.hr.promotion.history'
    _description = 'Employee Promotion History'
    _order = 'effective_date desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    old_salary_grade_level = fields.Selection(
        related='employee_id.salary_grade_level', string='Old Grade Level', readonly=True)
    old_rank = fields.Char(string='Old Rank', related='employee_id.rank', readonly=True)

    new_salary_grade_level = fields.Selection(SALARY_GRADE_LEVELS, string='New Grade Level', required=True)
    new_rank = fields.Char(string='New Rank/Position', required=True)
    effective_date = fields.Date(string='Effective Date', required=True)
    approval_date = fields.Date(string='Approval Date')
    approved_by = fields.Many2one('res.users', string='Approved By')
    remarks = fields.Text(string='Remarks')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented')
    ], default='draft')

    # Eligibility tracking
    promotion_eligibility_status = fields.Text(
        string='Eligibility Status',
        compute='_compute_promotion_eligibility_status',
        help='Shows promotion eligibility check results'
    )
    is_promotion_eligible = fields.Boolean(
        string='Is Eligible',
        compute='_compute_is_promotion_eligible',
        help='True if employee meets all promotion requirements'
    )

    @api.depends('employee_id')
    def _compute_promotion_eligibility_status(self):
        """Check and display promotion eligibility status."""
        for record in self:
            if record.employee_id:
                is_eligible, reasons = record.employee_id.check_promotion_eligibility()
                if is_eligible:
                    record.promotion_eligibility_status = '✓ Employee is eligible for promotion'
                else:
                    record.promotion_eligibility_status = 'Employee is NOT eligible:\n' + '\n'.join(f'• {reason}' for reason in reasons)
            else:
                record.promotion_eligibility_status = 'Please select an employee'

    @api.depends('employee_id')
    def _compute_is_promotion_eligible(self):
        """Check if employee is eligible for promotion."""
        for record in self:
            if record.employee_id:
                is_eligible, _ = record.employee_id.check_promotion_eligibility()
                record.is_promotion_eligible = is_eligible
            else:
                record.is_promotion_eligible = False

    @api.constrains('employee_id', 'state')
    def _check_promotion_eligibility_on_approve(self):
        """Validate promotion eligibility when moving to approved state."""
        for record in self:
            if record.state == 'approved':
                is_eligible, reasons = record.employee_id.check_promotion_eligibility()
                if not is_eligible:
                    raise UserError(
                        _('Cannot approve promotion. Employee is not eligible:\n\n') + 
                        '\n'.join(f'• {reason}' for reason in reasons)
                    )