from odoo import models, fields, api, _

class ProgramYear(models.Model):
    _name = 'school.program.year'
    _description = 'Program Year'
    _rec_name = 'label'

    year_number = fields.Char(string='Year Number', required=True)
    label = fields.Char(string='Label', required=True)
    description = fields.Char(string='Description', required=True)