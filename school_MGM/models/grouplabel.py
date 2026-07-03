from odoo import fields, models

class GroupLabel(models.Model):
    _name = 'school.group.label'
    _description = 'Group Label'
    name = fields.Char(string='Label', required=True)

    group_ids = fields.One2many('school.group', 'label_id', string='Groups')
