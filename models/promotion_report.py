# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta


class PromotionReport(models.Model):
    _name = 'mda.promotion.report'
    _description = 'Promotion Analysis Report'
    _auto = False
    _rec_name = 'employee_name'

    # Employee Information
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    employee_name = fields.Char(string='Employee Name', readonly=True)
    file_number = fields.Char(string='File Number', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)

    # Current Position
    current_grade = fields.Char(string='Current Grade Level', readonly=True)
    current_rank = fields.Char(string='Current Rank', readonly=True)
    appointment_date = fields.Date(string='Appointment Date', readonly=True)

    # Promotion History
    promotion_count = fields.Integer(string='Total Promotions', readonly=True)
    last_promotion_date = fields.Date(string='Last Promotion Date', readonly=True)
    new_grade = fields.Char(string='New Grade Level', readonly=True)
    new_rank = fields.Char(string='New Rank', readonly=True)
    promotion_effective_date = fields.Date(string='Effective Date', readonly=True)

    # Eligibility Status
    is_confirmed = fields.Boolean(string='Confirmed', readonly=True)
    date_confirmed = fields.Date(string='Date Confirmed', readonly=True)
    has_disciplinary_case = fields.Boolean(string='Has Disciplinary Case', readonly=True)
    passed_promotion_exam = fields.Boolean(string='Passed Exam', readonly=True)
    promotion_vacancy = fields.Boolean(string='Vacancy Available', readonly=True)
    is_eligible = fields.Boolean(string='Is Eligible', readonly=True)

    # Status
    promotion_state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('implemented', 'Implemented')
    ], string='Promotion Status', readonly=True)

    @property
    def _table_query(self):
        return """(
            SELECT
                emp.id * 1000 + COALESCE(ph.id, 0) as id,
                emp.id as employee_id,
                emp.name as employee_name,
                emp.file_number,
                emp.department_id,
                emp.salary_grade_level as current_grade,
                emp.rank as current_rank,
                emp.date_present_appointment as appointment_date,
                COALESCE(prom.promotion_count, 0) as promotion_count,
                COALESCE(ph.effective_date, NULL) as last_promotion_date,
                COALESCE(ph.new_salary_grade_level, NULL) as new_grade,
                COALESCE(ph.new_rank, NULL) as new_rank,
                COALESCE(ph.effective_date, NULL) as promotion_effective_date,
                emp.is_confirmed,
                emp.date_confirmed,
                emp.has_disciplinary_case,
                emp.passed_promotion_exam,
                emp.promotion_vacancy_available as promotion_vacancy,
                CASE 
                    WHEN emp.is_confirmed AND 
                         NOT emp.has_disciplinary_case AND 
                         emp.passed_promotion_exam AND 
                         emp.promotion_vacancy_available 
                    THEN TRUE 
                    ELSE FALSE 
                END as is_eligible,
                COALESCE(ph.state, 'draft') as promotion_state
            FROM hr_employee emp
            LEFT JOIN mda_hr_promotion_history ph ON emp.id = ph.employee_id
            LEFT JOIN (
                SELECT employee_id, COUNT(*) as promotion_count
                FROM mda_hr_promotion_history
                WHERE state = 'implemented'
                GROUP BY employee_id
            ) prom ON emp.id = prom.employee_id
            WHERE emp.active = TRUE
            ORDER BY emp.name, ph.effective_date DESC
        )"""


class PromotionEligibilityReport(models.Model):
    _name = 'mda.promotion.eligibility.report'
    _description = 'Promotion Eligibility Report'
    _auto = False
    _rec_name = 'employee_name'

    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    employee_name = fields.Char(string='Employee Name', readonly=True)
    file_number = fields.Char(string='File Number', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    current_grade = fields.Char(string='Grade Level', readonly=True)
    current_rank = fields.Char(string='Rank', readonly=True)

    # Eligibility Criteria
    confirmed_eligible = fields.Boolean(string='Staff Confirmed (2yrs)', readonly=True)
    maturity_eligible = fields.Boolean(string='Maturity Period Met', readonly=True)
    discipline_check = fields.Boolean(string='No Disciplinary Cases', readonly=True)
    exam_check = fields.Boolean(string='Passed Promotion Exam', readonly=True)
    vacancy_check = fields.Boolean(string='Vacancy Available', readonly=True)

    # Overall Status
    overall_eligible = fields.Boolean(string='Overall Eligible', readonly=True)
    eligibility_percentage = fields.Float(string='Eligibility %', readonly=True)

    @property
    def _table_query(self):
        return """(
            SELECT
                emp.id as id,
                emp.id as employee_id,
                emp.name as employee_name,
                emp.file_number,
                emp.department_id,
                emp.salary_grade_level as current_grade,
                emp.rank as current_rank,
                CASE WHEN emp.is_confirmed THEN TRUE ELSE FALSE END as confirmed_eligible,
                CASE 
                    WHEN emp.is_confirmed THEN TRUE
                    ELSE FALSE 
                END as maturity_eligible,
                CASE WHEN NOT emp.has_disciplinary_case THEN TRUE ELSE FALSE END as discipline_check,
                CASE WHEN emp.passed_promotion_exam THEN TRUE ELSE FALSE END as exam_check,
                CASE WHEN emp.promotion_vacancy_available THEN TRUE ELSE FALSE END as vacancy_check,
                CASE 
                    WHEN emp.is_confirmed AND 
                         NOT emp.has_disciplinary_case AND 
                         emp.passed_promotion_exam AND 
                         emp.promotion_vacancy_available 
                    THEN TRUE 
                    ELSE FALSE 
                END as overall_eligible,
                ROUND(
                    ((CASE WHEN emp.is_confirmed THEN 1 ELSE 0 END +
                      CASE WHEN NOT emp.has_disciplinary_case THEN 1 ELSE 0 END +
                      CASE WHEN emp.passed_promotion_exam THEN 1 ELSE 0 END +
                      CASE WHEN emp.promotion_vacancy_available THEN 1 ELSE 0 END) * 100.0 / 4), 2
                ) as eligibility_percentage
            FROM hr_employee emp
            WHERE emp.active = TRUE
            ORDER BY emp.name
        )"""
