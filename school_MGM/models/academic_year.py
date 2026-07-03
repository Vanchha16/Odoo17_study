from odoo import models, fields, api, _

class AcademicYear(models.Model):
    _name = 'school.academic.year'
    _inherit = ['mail.thread']
    _description = 'Academic Year'

    name = fields.Char(string='Academic Year', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    status = fields.Selection([
        ('active', 'Active'),
        ('closed', 'Closed'),
    ], string='Status', default='active')
    # semester_count = fields.Integer(compute='_compute_counts')
    # group_count = fields.Integer(compute='_compute_counts')
    # progress = fields.Integer(compute='_compute_progress')

    # @api.depends('semester_ids', 'group_ids')
    # def _compute_counts(self):
    #     for r in self:
    #         r.semester_count = len(r.semester_ids)
    #         r.group_count = len(r.group_ids)
    #
    # @api.depends('start_date', 'end_date')
    # def _compute_progress(self):
    #     today = fields.Date.today()
    #     for r in self:
    #         if r.status == 'archived':
    #             r.progress = 100
    #         elif r.start_date and r.end_date and r.start_date <= today <= r.end_date:
    #             total = (r.end_date - r.start_date).days
    #             done = (today - r.start_date).days
    #             r.progress = round((done / total) * 100) if total else 0
    #         else:
    #             r.progress = 0