# -*- coding: utf-8 -*-
{
    'name': 'MDA Nigerian HR Extension',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Nigerian-specific HR extensions for employee management',
    'description': """
Nigerian HR Extension Module
============================

This module extends Odoo's standard HR functionality with Nigerian-specific fields:

* Personal identification (File Number, IPPIS)
* Employment information (Rank, Salary Grade, Appointment Type)
* Pension & Financial (PFA, RSA PIN)
* Geographical information (State of Origin, LGA, Geopolitical Zone)
* Administrative fields (Employee Status, Qualifications)

Features:
* Automatic retirement date calculation
* State-LGA dependency management  
* Geopolitical zone auto-population
* Field validations for Nigerian standards
* Enhanced reporting capabilities
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['hr', 'hr_contract', 'mail'],
    'data': [
        'security/hr_security.xml',
        'data/pfa_partners.xml',
        'security/report_security.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/promotion_history_views.xml',
        'views/hr_report_templates.xml',
        'views/views.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}