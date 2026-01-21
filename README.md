# MDA Nigerian HR Extension Module

## Overview

The MDA Nigerian HR Extension module extends Odoo's standard HR functionality with Nigerian-specific fields and features. This module is designed to meet the requirements of Nigerian organizations, particularly government agencies and public institutions.

## Features

### Personal Identification
- File Number (unique identifier)
- IPPIS (Integrated Payroll and Personnel Information System) Number
- Nigerian naming convention (Surname, First Name, Middle Name)

### Employment Information
- Nigerian rank/position system
- Comprehensive salary grade levels (GL, CONRAISS, CONTISS, CONHESS, CONMESS)
- Appointment types (Permanent, Contract, Temporary, Casual, Attachment)
- Date tracking for appointments
- Automatic retirement date calculation

### Pension & Financial
- Pension Fund Administrator (PFA) management
- RSA PIN tracking with validation
- Conditional requirements for permanent staff

### Geographical Information
- Complete Nigerian states and FCT
- Local Government Area (LGA) tracking
- Automatic geopolitical zone assignment

### Administrative Features
- Employee status tracking
- Qualification management
- Job description requirements
- Comprehensive reporting system

## Installation

1. Copy the `mda_hr` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "MDA Nigerian HR Extension" module
4. The module will automatically extend the existing HR functionality

## Dependencies

- `hr` (Odoo Human Resources)
- `hr_contract` (HR Contracts)

## Usage

### Employee Management

1. Navigate to **Human Resources > Employees**
2. Create or edit an employee record
3. Fill in the Nigerian-specific fields organized in tabs:
   - **Personal Information**: Names, file number, IPPIS
   - **Employment Details**: Rank, salary grade, appointment dates
   - **Location & Origin**: State, LGA, geopolitical zone
   - **Qualifications**: Educational background
   - **Pension & Financial**: PFA and RSA PIN (for permanent staff)

### Data Import

The module supports CSV import using Odoo's standard import mechanism. Key fields for import include:

Required fields:
- `file_number`
- `surname`
- `first_name`
- `rank`
- `salary_grade_level`
- `appointment_type`
- `date_first_appointment`
- `date_present_appointment`
- `state_of_origin`
- `qualification`
- `job_description`
- `salary_structure`

Additional fields for permanent staff:
- `pfa_name` (partner name)
- `rsa_pin`

### Reporting

The module includes comprehensive reporting features accessible via:
**Human Resources > Nigerian HR Reports > Generate Reports**

Available reports:
1. **Employee Master Report**: Complete employee listing
2. **Pension Compliance Report**: PFA and RSA PIN status
3. **Retirement Schedule Report**: Upcoming retirements by year
4. **Geographical Distribution Report**: Employee distribution by state/zone
5. **Qualification Analysis Report**: Staff qualification statistics

### Quick Views

Access pre-configured views via:
**Human Resources > Nigerian HR Reports > Quick Views**

- Employees by Status
- Employees by State
- Retirement Schedule

## Field Validations

The module includes automatic validations for:

- **File Number**: Must be unique across all employees
- **IPPIS Format**: 8-12 digits
- **RSA PIN Format**: "PEN" followed by 12 digits
- **Age Requirements**: Employees must be at least 18 years old
- **Date Logic**: Present appointment date >= First appointment date
- **Permanent Staff**: PFA and RSA PIN required for permanent appointments

## Computed Fields

- **Retirement Date**: Automatically calculated (60 years for general staff, 65 for PhD/Masters holders)
- **Age on Entry**: Calculated from DOB and first appointment date
- **Geopolitical Zone**: Auto-populated based on state of origin
- **Full Name**: Formatted as "Surname, First Name Middle Name"

## Technical Details

### Models Extended
- `hr.employee`: Main employee model with Nigerian fields

### New Models
- `hr.employee.report`: Report generation wizard
- `report.mda_hr.employee_reports`: Report data processor

### Security
- Inherits existing HR security model
- Appropriate access controls for sensitive information
- Role-based report access

## Customization

The module is designed to be easily customizable:

- Add new states/LGAs by modifying selection fields
- Extend salary grade levels in the model
- Customize report templates in the XML files
- Add new computed fields following the existing patterns

## Support

For technical support or customization requests, refer to your Odoo implementation partner or system administrator.

## Version Information

- **Module Version**: 18.0.1.0.0
- **Odoo Version**: 18.0
- **License**: LGPL-3

## Changelog

### Version 1.0.0
- Initial release
- Complete Nigerian HR extension
- All core features implemented
- Comprehensive reporting system
- Data import support