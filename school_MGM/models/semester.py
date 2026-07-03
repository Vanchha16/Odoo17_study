from odoo import models, fields, api, _

class Semester(models.Model):
    _name = 'school.semester'
    _description = 'Semester'

    name = fields.Char(string='Semester', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    midterm_date = fields.Date(string='Midterm Date', required=True)
    final_date = fields.Date(string='Final Date', required=True)

    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)