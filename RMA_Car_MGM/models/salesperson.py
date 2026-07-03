from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

class Seller(models.Model):
    _name = 'rma.seller'
    _inherit = ['mail.thread']
    _description = 'Seller'


    name = fields.Char(string='SellerName', required=True , tracking=True)
    phone = fields.Char(string='Phone', required=True , tracking=True)
    email = fields.Char(string='Email', required=True , tracking=True)
    address = fields.Text(string='Address', required=True , tracking=True)
    sale_history_id = fields.One2many('rma.sale_order', 'seller_id', string='History')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ], string='Status', default='draft', tracking=True)
    def action_save_seller(self):
        self.write({
            'state': 'available',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Saved!'),
                'message': _('Seller has been saved successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }