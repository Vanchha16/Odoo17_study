from odoo import models, fields , api,_


class Subject(models.Model):
    _name = 'school.subject'
    _inherit = ['mail.thread']
    _description = 'Subject'

    name = fields.Char(string='Subject Name', required=True , translate=True , tracking=True)
    sequence = fields.Integer(default=10)
    teacher_ids = fields.Many2many('school.teacher', string='Teacher', tracking=True)

    def count_teacher(self):
        for rec in self:
            rec.teacher_count = len(rec.teacher_ids)
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'A subject with this name already exists.')
    ]