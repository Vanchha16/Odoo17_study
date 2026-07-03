from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Major(models.Model):
    _name = 'school.major'
    _description = 'Major'
    _rec_name = 'code'

    code = fields.Char(string='Major Code', required=True)
    name = fields.Char(string='Major Name', required=True)
    degree_level = fields.Selection([('bachelor', 'Bachelor'), ('associate', 'Associate'), ('master', 'Master')], string='Degree Level', required=True)
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], string='Status', default='active')

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for rec in self:
            if rec.code and rec.name:
                rec.display_name = f"{rec.code} - {rec.name}"
            else:
                rec.display_name = rec.name or rec.code or ''