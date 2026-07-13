from odoo import models, fields

class Teacher(models.Model):
    _name = 'school.teacher'
    _inherit = ['mail.thread']
    _description = 'Teacher'

    name = fields.Char(string='Name', required=True ,   translate=True , tracking=True)
    email = fields.Char(string='Email' , tracking=True , required=True)
    phone = fields.Char(string='Phone' , tracking=True , required=True)
    subject_id = fields.Many2many('school.subject', string='Subject', tracking=True )
    group_id = fields.Many2many('school.group', string='Group', tracking=True )

    user_id = fields.Many2one('res.users', string='User', tracking=True)

    def action_craete_user(self):
        for record in records:
            if record.email and not record.user_id:
                user = env['res.users'].create({
                    'name': record.name,
                    'login': record.email,
                    'email': record.email,
                    'password': '123',
                    'groups_id': [(6, 0, [
                        env.ref('school_MGM.group_school_teacher').id,
                    ])],
                })
                record.write({
                    'user_id': user.id,
                })