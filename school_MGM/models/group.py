from odoo import models, fields, api

class Group(models.Model):
    _name = 'school.group'
    _inherit = ['mail.thread']
    _description = 'Class'
    _rec_name = 'display_group_name'

    name = fields.Char(string='Group Name', required=True, translate=True, tracking=True)
    label_id = fields.Many2one('school.group.label', string='Label', tracking=True)
    display_group_name = fields.Char(
        string='Group Label',
        compute='_compute_display_group_name',
        store=True, tracking=True)
    period = fields.Selection([
        ('M', 'Morning'),
        ('A', 'Afternoon'),
        ('E', 'Evening'),
         ], string='Period', required=True, tracking=True)

    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', tracking=True)
    semester_id = fields.Many2one('school.semester', string='Semester', tracking=True)
    program_year_id = fields.Many2one('school.program.year', string='Program Year', tracking=True)
    major_id = fields.Many2one('school.major', string='Major', tracking=True)

    student_ids = fields.One2many('school.student', 'group_id', string='Students')
    teacher_ids = fields.Many2many('school.teacher', string='Teacher', tracking=True, required=True)
    student_count = fields.Integer(string='Student Count', compute='_compute_student_count')
    teacher_count = fields.Integer(string='Teachers', compute='_compute_teacher_count')
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'A group with this name already exists.')
    ]

    @api.depends('label_id', 'label_id.name', 'name')
    def _compute_display_group_name(self):
        for rec in self:
            if rec.label_id and rec.name:
                rec.display_group_name = f"{rec.label_id.name}{rec.name}"
            else:
                rec.display_group_name = rec.name or ''
    @api.depends('student_ids')
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)

    @api.depends('teacher_ids')
    def _compute_teacher_count(self):
        for rec in self:
            rec.teacher_count = len(rec.teacher_ids)