from odoo import models, fields, api, _


class SubjectOffering(models.Model):
    _name = 'school.subject.offering'
    _inherit = ['mail.thread']
    _description = 'Subject Offering'
    _rec_name = 'display_name'
    subject_id = fields.Many2one('school.subject', string='Subject', tracking=True, required=True)

    program_year_id = fields.Many2one('school.program.year', string='Program Year', tracking=True, required=True)
    semester_id = fields.Many2one('school.semester', string='Semester', tracking=True, required=True)
    major_id = fields.Many2one('school.major', string='Major', tracking=True, required=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    _sql_constraints = [
        ('unique_offering',
         'UNIQUE(major_id, program_year_id, semester_id, subject_id)',
         'This subject is already offered for this Major / Year / Semester.')
    ]

    @api.depends('major_id', 'program_year_id', 'semester_id', 'subject_id')
    def _compute_display_name(self):
        for r in self:
            parts = [
                r.major_id.code or '',
                r.program_year_id.label or '',
                r.semester_id.name or '',
                r.subject_id.name or '',
            ]
            r.display_name = ' | '.join(filter(None, parts))