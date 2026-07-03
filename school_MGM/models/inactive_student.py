from odoo import models, fields, _
from odoo.exceptions import ValidationError

class InactiveStudent(models.TransientModel):
    _name = 'school.inactive.student'
    _description = 'Inactive Student Reason'

    student_id = fields.Many2one(
        'school.student',
        string='Student',
        required=True
    )
    note = fields.Text(string='Reason', required=True)

    def action_confirm(self):
        if not self.student_id:
            raise ValidationError(_('No student selected.'))
        if not self.note:
            raise ValidationError(_('Please provide a reason.'))

        print(self.note)
        print(self.student_id)

        self.student_id.write({
            'status': 'cancelled',
            'note': self.note,
        })
        return {'type': 'ir.actions.act_window_close'}