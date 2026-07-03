from odoo import models, fields, api, _

class NotInterestedWizard(models.TransientModel):
    _name = 'rma.not.interested.wizard'

    _description = 'Not Interested Reason'

    booking_id = fields.Many2one('rma.cus.car.test', string='Booking')

    reason = fields.Text(string='Reason', required=True)
    
    def action_confirm(self):
        self.booking_id.write({
            'status': 'not_interested',
            'not_interested_reason': self.reason,
        })