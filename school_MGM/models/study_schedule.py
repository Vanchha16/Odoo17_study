from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime
import pytz


class StudySchedule(models.Model):
    _name = 'school.study.schedule'
    _description = 'Study Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string='Schedule Name', tracking=True)

    group_id = fields.Many2one('school.group', string='Group', required=True, tracking=True)
    major_id = fields.Many2one(
        'school.major', related='group_id.major_id',
        string='Major', store=True, readonly=True
    )
    group_period = fields.Selection(
        related='group_id.period_MAE',
        string='Group Period',
        readonly=True,
        store=False,
    )
    subject_offering_id = fields.Many2one(
        'school.subject.offering', string='Subject Offering',
        required=True, tracking=True
    )
    subject_id = fields.Many2one(
        'school.subject',
        related='subject_offering_id.subject_id',
        string='Subject', store=True, readonly=True
    )
    room_id = fields.Many2one('school.room', string='Room', required=True, tracking=True)
    teacher_id = fields.Many2one('school.teacher', string='Teacher', required=True, tracking=True , domain="[('subject_id', 'in', [subject_id])]")

    study_session_id = fields.Many2one(
        'school.study.session', string='Study Session',
        required=True, tracking=True
    )
    day_of_week = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], string='Day of Week', required=True, tracking=True)

    state = fields.Selection([
        ('draft',     'Draft'),
        ('active',    'Active'),
        ('cancelled', 'Cancelled'),
    ], default='draft', string='Status', tracking=True)

    # ── Related from group (all stored so they can be searched/filtered) ──
    academic_year_id = fields.Many2one(
        'school.academic.year', related='group_id.academic_year_id',
        string='Academic Year', store=True, readonly=True
    )
    semester_id = fields.Many2one(
        'school.semester', related='group_id.semester_id',
        string='Semester', store=True, readonly=True, tracking=True
    )
    program_year_id = fields.Many2one(
        'school.program.year', related='group_id.program_year_id',
        string='Program Year', store=True, readonly=True, tracking=True
    )

    # ── Link back to generated timetable entries ──────────────────
    timetable_ids = fields.One2many(
        'school.timetable', 'study_schedule_id',
        string='Generated Sessions'
    )
    session_count = fields.Integer(
        compute='_compute_session_count', string='Sessions Generated'
    )
    display_date = fields.Datetime(
        string="Display Date"
    )

    @api.depends('timetable_ids')
    def _compute_session_count(self):
        for rec in self:
            rec.session_count = len(rec.timetable_ids)

    # ── Overlap validation ────────────────────────────────────────
    @api.constrains('group_id', 'teacher_id', 'room_id', 'day_of_week', 'study_session_id', 'state')
    def _check_overlap(self):
        for rec in self:
            if rec.state == 'cancelled':
                continue
            base = [
                ('state', '!=', 'cancelled'),
                ('day_of_week', '=', rec.day_of_week),
                ('study_session_id', '=', rec.study_session_id.id),
                ('id', '!=', rec.id),
            ]
            if self.search_count(base + [('group_id', '=', rec.group_id.id)]):
                raise ValidationError(_(
                    'Group "%s" already has a schedule on this day and session.'
                ) % rec.group_id.display_group_name)
            if self.search_count(base + [('teacher_id', '=', rec.teacher_id.id)]):
                raise ValidationError(_(
                    'Teacher "%s" is already assigned on this day and session.'
                ) % rec.teacher_id.name)
            if self.search_count(base + [('room_id', '=', rec.room_id.id)]):
                raise ValidationError(_(
                    'Room "%s" is already booked on this day and session.'
                ) % rec.room_id.room_label)

    # ── Helpers ───────────────────────────────────────────────────
    def _float_to_hm(self, value):
        """Convert float hour (e.g. 7.5 → 7h 30m)."""
        hour = int(value)
        minute = round((value - hour) * 60)
        return hour, minute

    def _to_utc(self, d, float_time):
        """Combine a date + float time in user's timezone → naive UTC datetime."""
        user_tz = pytz.timezone(self.env.user.tz or 'Asia/Phnom_Penh')
        h, m = self._float_to_hm(float_time)
        local_dt = user_tz.localize(datetime(d.year, d.month, d.day, h, m, 0))
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    # ── Core: generate one timetable entry per week ───────────────
    def action_generate_sessions(self):
        for rec in self:
            if not rec.semester_id:
                raise ValidationError(
                    _('Group "%s" has no semester assigned.') % rec.group_id.display_group_name
                )
            sem = rec.semester_id
            if not sem.start_date or not sem.end_date:
                raise ValidationError(
                    _('Semester "%s" is missing start or end date.') % sem.name
                )

            # Remove any previously generated sessions for this schedule
            rec.timetable_ids.unlink()

            target_dow = int(rec.day_of_week)   # 0 = Monday … 6 = Sunday
            session = rec.study_session_id

            # Find the first matching weekday on or after semester start
            current = sem.start_date
            days_ahead = (target_dow - current.weekday()) % 7
            current = current + timedelta(days=days_ahead)

            to_create = []
            while current <= sem.end_date:
                to_create.append({
                    'study_schedule_id': rec.id,
                    'group_id':   rec.group_id.id,
                    'teacher_id': rec.teacher_id.id,
                    'subject_id': rec.subject_id.id,
                    'room_id':    rec.room_id.id,
                    'time_start': self._to_utc(current, session.start_time),
                    'time_end':   self._to_utc(current, session.end_time),
                    'state':      'confirmed',
                })
                current += timedelta(weeks=1)

            self.env['school.timetable'].create(to_create)
            rec.state = 'active'

        total = sum(len(r.timetable_ids) for r in self)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title':   _('Sessions Generated'),
                'message': _('%d sessions created until end of semester.') % total,
                'type':    'success',
            },
        }

    def action_cancel(self):
        for rec in self:
            rec.timetable_ids.write({'state': 'cancelled'})
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            rec.timetable_ids.unlink()
            rec.state = 'draft'

    def action_view_sessions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generated Sessions'),
            'res_model': 'school.timetable',
            'view_mode': 'tree,calendar,form',
            'domain': [('study_schedule_id', '=', self.id)],
            'context': {'default_study_schedule_id': self.id},
        }