# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta
from ..constants import SALARY_GRADE_LEVELS, NIGERIAN_STATES, GEO_POLITICAL_ZONE_MAPPING


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Personal Identification
    file_number = fields.Char('File Number')
    ippis = fields.Char('IPPIS Number')
    surname = fields.Char('Surname')
    first_name = fields.Char('First Name')
    middle_name = fields.Char('Middle Name')

    # Employment Information
    rank = fields.Char('Rank/Position')
    department_id = fields.Many2one('hr.department', 'Department')
    salary_grade_level = fields.Selection(SALARY_GRADE_LEVELS, 'Salary Grade Level')

    appointment_type = fields.Selection([
        ('permanent', 'Permanent'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('casual', 'Casual'),
        ('attachment', 'Attachment'),
    ], 'Appointment Type', default='contract')

    date_first_appointment = fields.Date('Date of First Appointment')
    date_present_appointment = fields.Date('Date of Present Appointment')
    retirement_date = fields.Date('Retirement Date', compute='_compute_retirement_date', store=True)

    # Pension & Financial
    rsa_pin = fields.Char('RSA PIN')
    pfa_name = fields.Char('PFA Name')

    # Geographical Information
    state_of_origin = fields.Selection(NIGERIAN_STATES, 'State of Origin')

    lga = fields.Char('Local Government Area')
    geo_political_zone = fields.Selection([
        ('north_central', 'North Central'),
        ('north_east', 'North East'),
        ('north_west', 'North West'),
        ('south_east', 'South East'),
        ('south_south', 'South South'),
        ('south_west', 'South West'),
    ], 'Geopolitical Zone', compute='_compute_geo_political_zone', store=True)

    # Administrative
    employee_status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('retired', 'Retired'),
        ('deceased', 'Deceased'),
        ('terminated', 'Terminated'),
    ], 'Employee Status', default='active')

    remark = fields.Text('Remarks')

    # Qualification & Job
    age_on_entry = fields.Integer('Age on Entry', compute='_compute_age_on_entry', store=True)
    qualification = fields.Char('Qualification')
    nature_of_desc = fields.Char('Nature of Description')
    job_description = fields.Text('Job Description')
    salary_structure = fields.Selection([
        ('contiss', 'CONTISS'),
        ('conraiss', 'CONRAISS'),
        ('conhess', 'CONHESS'),
        ('conmess', 'CONMESS'),
        ('conpss', 'CONPSS'),
        ('others', 'Others'),
    ], 'Salary Structure')

    # Override the name field from base model
    name = fields.Char('Employee Name')

    # Promotion tracking
    promotion_history_ids = fields.One2many(
        'mda.hr.promotion.history', 'employee_id', string='Promotion History'
    )

    next_promotion_due = fields.Date(
        string='Next Promotion Due',
        compute='_compute_next_promotion_due', store=True
    )

    # Promotion eligibility fields
    is_confirmed = fields.Boolean(
        string='Confirmed Staff',
        compute='_compute_is_confirmed',
        store=True,
        help='Staff must be confirmed (2 years from date of present appointment)'
    )
    date_confirmed = fields.Date(
        string='Date Confirmed',
        help='Date when staff was confirmed'
    )
    has_disciplinary_case = fields.Boolean(
        string='Has Disciplinary Case',
        default=False,
        help='Check if employee has any disciplinary cases'
    )
    passed_promotion_exam = fields.Boolean(
        string='Passed Promotion Exam',
        default=False,
        help='Has the employee passed the promotion exam?'
    )
    promotion_exam_date = fields.Date(
        string='Promotion Exam Date',
        help='Date when promotion exam was taken'
    )
    promotion_vacancy_available = fields.Boolean(
        string='Promotion Vacancy Available',
        default=False,
        help='Is there a vacancy for promotion in the target grade?'
    )

    @api.model
    def create(self, vals_list):
        """Create employee records with validation and auto-name generation."""
        # Process each record in the batch
        for vals in vals_list:
            # Validate date constraints
            if vals.get('date_first_appointment') and vals.get('date_present_appointment'):
                if vals['date_present_appointment'] < vals['date_first_appointment']:
                    raise UserError(_(
                        "Date of Present Appointment cannot be before Date of First Appointment."
                    ))
            
            # Auto-generate name from name parts
            if not vals.get('name') and (vals.get('surname') or vals.get('first_name')):
                name_parts = []
                if vals.get('surname'):
                    name_parts.append(vals['surname'])
                if vals.get('first_name'):
                    name_parts.append(vals['first_name'])
                if vals.get('middle_name'):
                    name_parts.append(vals['middle_name'])
                vals['name'] = ' '.join(name_parts)
        
        return super().create(vals_list)

    def write(self, vals):
        """Write records with validation."""
        # Validate date constraints
        if any(field in vals for field in ['date_first_appointment', 'date_present_appointment']):
            for record in self:
                date_first = vals.get('date_first_appointment', record.date_first_appointment)
                date_present = vals.get('date_present_appointment', record.date_present_appointment)
                if date_first and date_present and date_present < date_first:
                    raise UserError(_(
                        "Date of Present Appointment cannot be before Date of First Appointment."
                    ))
        
        # Update name from name parts if any changed
        if any(field in vals for field in ['surname', 'first_name', 'middle_name']):
            for record in self:
                name_parts = []
                surname = vals.get('surname', record.surname)
                first_name = vals.get('first_name', record.first_name)
                middle_name = vals.get('middle_name', record.middle_name)
                
                if surname:
                    name_parts.append(surname)
                if first_name:
                    name_parts.append(first_name)
                if middle_name:
                    name_parts.append(middle_name)
                
                if name_parts and not vals.get('name'):
                    vals['name'] = ' '.join(name_parts)
        return super().write(vals)

    @api.depends('birthday', 'qualification')
    def _compute_retirement_date(self):
        for rec in self:
            if rec.birthday:
                birth_year = rec.birthday.year
                retirement_age = 65 if rec.qualification and rec.qualification.lower() in ['phd', 'master'] else 60
                rec.retirement_date = date(birth_year + retirement_age, rec.birthday.month, rec.birthday.day)
            else:
                rec.retirement_date = False

    @api.depends('birthday', 'date_first_appointment')
    def _compute_age_on_entry(self):
        for rec in self:
            if rec.birthday and rec.date_first_appointment:
                birth_date = rec.birthday
                appointment_date = rec.date_first_appointment
                age = appointment_date.year - birth_date.year
                if appointment_date.month < birth_date.month or \
                   (appointment_date.month == birth_date.month and appointment_date.day < birth_date.day):
                    age -= 1
                rec.age_on_entry = age
            else:
                rec.age_on_entry = 0

    @api.depends('state_of_origin')
    def _compute_geo_political_zone(self):
        for rec in self:
            rec.geo_political_zone = GEO_POLITICAL_ZONE_MAPPING.get(rec.state_of_origin, False)

    @api.depends('promotion_history_ids.effective_date', 'date_present_appointment')
    def _compute_next_promotion_due(self):
        """Calculate next promotion due date (minimum 3 years between promotions)."""
        for emp in self:
            if emp.promotion_history_ids:
                last_promo = max(emp.promotion_history_ids.mapped('effective_date'))
                # Minimum 3 years between promotions (CONHESS rule)
                emp.next_promotion_due = last_promo + relativedelta(years=3)
            elif emp.date_present_appointment:
                emp.next_promotion_due = emp.date_present_appointment + relativedelta(years=3)
            else:
                emp.next_promotion_due = False

    @api.depends('date_present_appointment', 'date_confirmed')
    def _compute_is_confirmed(self):
        """Check if employee is confirmed (2 years from present appointment)."""
        for emp in self:
            if emp.date_confirmed:
                # Employee explicitly marked as confirmed
                emp.is_confirmed = True
            elif emp.date_present_appointment:
                # Check if 2 years have passed since present appointment
                years_in_service = (date.today() - emp.date_present_appointment).days / 365.25
                emp.is_confirmed = years_in_service >= 2
            else:
                emp.is_confirmed = False

    def get_maturity_period_years(self):
        """Get maturity period based on current salary grade level."""
        if not self.salary_grade_level:
            return 0
        
        try:
            grade_level = int(self.salary_grade_level)
            if grade_level <= 5:
                return 2
            elif grade_level <= 12:
                return 3
            else:  # grade_level >= 14
                return 4
        except (ValueError, TypeError):
            return 3  # Default to 3 years

    def is_maturity_period_met(self):
        """Check if maturity period requirement is met after confirmation."""
        if not self.date_confirmed:
            return False
        
        maturity_years = self.get_maturity_period_years()
        years_since_confirmation = (date.today() - self.date_confirmed).days / 365.25
        return years_since_confirmation >= maturity_years

    def check_promotion_eligibility(self):
        """
        Check if employee is eligible for promotion.
        Returns tuple: (is_eligible, reasons_for_ineligibility)
        """
        reasons = []
        
        # 1. Check confirmation status
        if not self.is_confirmed:
            reasons.append('Staff must be confirmed (2 years from present appointment)')
        
        # 2. Check maturity period
        if not self.is_maturity_period_met():
            maturity_years = self.get_maturity_period_years()
            if self.date_confirmed:
                years_remaining = maturity_years - ((date.today() - self.date_confirmed).days / 365.25)
                reasons.append(f'Maturity period not met. Grade {self.salary_grade_level} requires {maturity_years} years. {years_remaining:.1f} years remaining.')
            else:
                reasons.append(f'Maturity period not met for grade level {self.salary_grade_level} ({maturity_years} years required)')
        
        # 3. Check disciplinary cases
        if self.has_disciplinary_case:
            reasons.append('Staff has disciplinary case(s)')
        
        # 4. Check vacancy availability
        if not self.promotion_vacancy_available:
            reasons.append('No promotion vacancy available')
        
        # 5. Check promotion exam
        if not self.passed_promotion_exam:
            reasons.append('Staff must pass promotion exam')
        
        is_eligible = len(reasons) == 0
        return is_eligible, reasons

    def implement_promotion(self, promotion_history_id):
        """Implement an approved promotion."""
        promo = self.env['mda.hr.promotion.history'].browse(promotion_history_id)
        if promo.state != 'approved':
            raise UserError(_("Promotion must be approved before implementation."))

        emp = promo.employee_id
        emp.write({
            'salary_grade_level': promo.new_salary_grade_level,
            'rank': promo.new_rank,
            'date_present_appointment': promo.effective_date
        })

        promo.write({'state': 'implemented'})
