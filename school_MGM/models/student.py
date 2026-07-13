from multiprocessing.reduction import duplicate
from re import search

from odoo import models, fields, api, _
from  odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class Student(models.Model):
    _name = 'school.student'
    _inherit = ['mail.thread']
    _description = 'Student'

    student_code = fields.Char(string='Student Code', tracking=True, default='New')
    name = fields.Char(string='Student Name', required=True, translate=True, tracking=True)
    dob = fields.Date(string='Date of birth', tracking=True)
    email = fields.Char(string='Email', tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')], string='Gender',
                              tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    status = fields.Selection([('draft', 'Draft'), ('enrolled', 'Enrolled'), ('cancelled', 'Cancelled')],
                              string='Status', default='draft', tracking=True)
    group_id = fields.Many2one('school.group', string='Group', tracking=True, required=True , domain="[('major_id', 'in', [major_id])]")
    major_id = fields.Many2one('school.major', string='Major', tracking=True, required=True)
    name_major = fields.Char(string='Major Name', related='major_id.name', store=True, tracking=True)
    name_major_code = fields.Char(string='Major Code', related='major_id.code', store=True, tracking=True)
    user_id = fields.Many2one('res.users', string='User', tracking=True)
    note = fields.Text(string='Note Reason', tracking=True)
    age = fields.Integer(
        string='Age',
        compute='_compute_age',
        store=True,
        tracking=True,
    )
    check = fields.Boolean(string='Check', tracking=True)

    academic_year_id = fields.Many2one(
        'school.academic.year',
        related='group_id.academic_year_id',
        string='Academic Year',
        store=True,
        readonly=True
    )
    semester_id = fields.Many2one('school.semester',
                                  related='group_id.semester_id',
                                  string='Semester',
                                  tracking=True)
    program_year_id = fields.Many2one('school.program.year',
                                      related='group_id.program_year_id',
                                      string='Program Year',
                                      tracking=True)

    student_count = fields.Integer(string='Student Count', compute='_compute_student_count')

    @api.depends('group_id')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.group_id.student_ids)

    @api.model
    def create(self, vals):
        vals['student_code'] = self.env['ir.sequence'].next_by_code('school.student')
        return super(Student, self).create(vals)

    @api.depends('dob')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.dob:
                age = today.year - rec.dob.year
                if (today.month, today.day) < (rec.dob.month, rec.dob.day):
                    age -= 1
                rec.age = age
            else:
                rec.age = 0

    @api.constrains('dob', 'age')
    def _check_dob(self):
        for rec in self:
            if rec.age < 18:
                raise ValidationError(_("Student must be at least 18 years old."))

    def action_set_cancelled(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Set Cancelled'),
            'res_model': 'school.inactive.student',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_student_id': self.id,
            },
        }

    def action_set_draft(self):
        for rec in self:
            rec.note = ''
        self.write({'status': 'draft'})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payment',
            'res_model': 'school.payment',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_major_id': self.major_id.id,
                'default_group_id': self.group_id.id,
                'default_student_id': self.id,
            },
        }

    def action_set_enrolled(self):
        for rec in self:
            rec.note = ''
        self.with_context(mail_notrack=True).write({'status': 'enrolled'})

    def action_generate_payment(self):
        created_ids = []
        for student in self:
            existing = self.env['school.payment'].search([
                ('student_id', '=', student.id),
                ('payment_amount', '=', 'unpaid'),
            ], limit=1)
            if not existing:
                payment = self.env['school.payment'].create({
                    'student_id': student.id,
                    'group_id': student.group_id.id,
                    'major_id': student.major_id.id,
                    'payment_amount': 'unpaid',
                    'payment_date': fields.Datetime.now(),
                })
                created_ids.append(payment.id)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payments'),
            'res_model': 'school.payment',
            'view_mode': 'tree,form',
            'domain': [('student_id', 'in', self.ids)],
        }

    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone and self.search_count([('phone', '=', rec.phone), ('id', '!=', rec.id)]) > 0:
                raise ValidationError(_("Phone number already exists."))\

    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            duplicate = self.search([('email', '=', rec.email), ('id', '!=', rec.id)], limit=1)
            if duplicate:
                raise ValidationError(_("Email already exists use by %s.") % duplicate.name)