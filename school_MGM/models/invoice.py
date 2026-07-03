from odoo import models, fields, api

class Invoice(models.Model):
    _inherit = 'account.move'

    student_id = fields.Many2one('school.student', string='Student', ondelete='set null', index=True, copy=False)