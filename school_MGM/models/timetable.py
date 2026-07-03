from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
import pytz

class SchoolTimetable(models.Model):
    _name = 'school.timetable'
    _inherit = ['mail.thread']
    _description = 'Weekly Timetable'
    _rec_name = 'reference'

    teacher_id = fields.Many2one(
        'school.teacher',
        string='Teacher',
        tracking=True,
    )
    reference = fields.Char(
        string='Reference', default='New',
        copy=False,
    )

    time_start = fields.Datetime(string='Start Time', required=True, tracking=True)
    time_end   = fields.Datetime(string='End Time',   required=True, tracking=True)

    period = fields.Selection(related='group_id.period', store=True, readonly=True)
    group_id = fields.Many2one(
        'school.group',
        string='Group',
        required=True,
        tracking=True,
        domain="[('teacher_ids', 'in', [teacher_id])]",
    )
    subject_id = fields.Many2one(
        'school.subject',
        string='Subject',
        required=True,
        tracking=True,
        domain="[('teacher_ids', 'in', [teacher_id])]",
    )


    room_id = fields.Many2one(
        'school.room',
        string='Room',
        required=True,
        tracking=True,
    )
    study_schedule_id = fields.Many2one(
        'school.study.schedule', string='Study Schedule',
        ondelete='set null', readonly=True, copy=False,
    )
    notes = fields.Text(string='Notes', tracking=True)

    state = fields.Selection([
        ('draft',     'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.onchange('time_start')
    def _onchange_time_start(self):
        if self.time_start:
            user_tz = pytz.timezone(self.env.user.tz or 'Asia/Phnom_Penh')
            local_time = pytz.utc.localize(self.time_start).astimezone(user_tz)
            h, m = local_time.hour, local_time.minute

            if (h, m) > (17, 44):
                self.time_end = self.time_start + timedelta(hours=1)
            else:
                self.time_end = self.time_start + timedelta(hours=1, minutes=30)

    # create() — runs once when a new record is inserted for the first time.
    # write() — runs every time an existing record is updated.
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code(
                    'school.timetable'
                ) or 'New'
        return super().create(vals_list)

    @api.constrains('time_start', 'time_end')
    def _check_time(self):
        for rec in self:
            if rec.time_end <= rec.time_start:
                raise ValidationError(_('End time must be after start time.'))

    @api.constrains('group_id', 'teacher_id', 'time_start', 'time_end', 'state')
    def _check_overlap(self):
        for rec in self:
            if rec.state == 'cancelled':
                continue
            group_overlap = self.search_count([
                ('group_id', '=', rec.group_id.id),
                ('state', '!=', 'cancelled'),
                ('id', '!=', rec.id),
                ('time_start', '<', rec.time_end),
                ('time_end', '>', rec.time_start),
            ])
            if group_overlap:
                raise ValidationError(_(
                    'Group "%s" already has a class during this time slot.'
                ) % rec.group_id.name)
            teacher_overlap = self.search_count([
                ('teacher_id', '=', rec.teacher_id.id),
                ('state', '!=', 'cancelled'),
                ('id', '!=', rec.id),
                ('time_start', '<', rec.time_end),
                ('time_end', '>', rec.time_start),
            ])
            if teacher_overlap:
                raise ValidationError(_(
                    'Teacher "%s" is already teaching during this time slot.'
                ) % rec.teacher_id.name)

    @api.onchange('teacher_id')
    def _onchange_teacher_id(self):
        self.group_id = False
        self.subject_id = False
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'