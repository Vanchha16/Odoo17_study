from odoo import models, fields, api

class ManageTeacher(models.Model):
    _name = 'manage.teacher'
    _inherit = ['mail.thread']
    _description = 'Manage Teacher'

    teacher_id = fields.Many2one('school.teacher', string='Teacher', tracking=True, required=True)
    subject_id = fields.Many2many('school.subject', string='Subject', tracking=True, required=True)
    group_id = fields.Many2many('school.group', string='Group', tracking=True, required=True)