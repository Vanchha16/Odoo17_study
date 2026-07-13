from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequest(models.Model):
    _name = 'mini.purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Request'

    name = fields.Char(string='Request Reference', default='New', readonly=True, tracking=True)
    product_id = fields.Many2one('product.product', string='Product', required=True, tracking=True)
    qty = fields.Float(string='Quantity', required=True, default=1.0, tracking=True)
    requested_by = fields.Many2one('res.users', string='Requested By',
                                   default=lambda self: self.env.user, tracking=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.today, tracking=True)
    notes = fields.Text(string='Notes')
    purchase_order_id = fields.Many2one('mini.purchase.order', string='Purchase Order', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    def action_submit(self):
        for rec in self:
            rec.state = 'submitted'

    def action_approve(self):
        for rec in self:
            if rec.state != 'submitted':
                raise ValidationError(_('Only submitted requests can be approved.'))
            rec.state = 'approved'

    def action_reject(self):
        for rec in self:
            rec.state = 'rejected'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mini.purchase.request') or 'New'
        return super().create(vals_list)