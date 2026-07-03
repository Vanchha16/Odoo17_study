from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

class Customer(models.Model):
    _name = 'rma.customer'
    _inherit = ['mail.thread']
    _description = 'Customers'

    name = fields.Char(string='Customer Name', required=True , tracking=True)
    phone = fields.Char(string='Phone', required=True , tracking=True)
    email = fields.Char(string='Email', required=True , tracking=True )
    address = fields.Text(string='Address', required=True , tracking=True)
    requests_id = fields.One2many('rma.cus.car.test', 'customer_id', string='Requests')


    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ], string='Status', default='draft', tracking=True)
    def action_save_custom(self):
        self.write({
            'state': 'available',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Saved!'),
                'message': _('Customer has been saved successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    _sql_constraints = [
        ('phone_unique', 'UNIQUE(phone)', 'A customer with this Phone Number already exists.'),
        ('email_unique', 'UNIQUE(email)', 'A customer with this Email already exists.'),
    ]
