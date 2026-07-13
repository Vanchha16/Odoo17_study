from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _name = 'mini.purchase.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Order'

    name = fields.Char(string='Order Reference', default='New', readonly=True, tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True, tracking=True)
    order_date = fields.Date(string='Order Date', default=fields.Date.today, tracking=True)
    order_line_ids = fields.One2many('mini.purchase.order.line', 'order_id', string='Order Lines')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    amount_total = fields.Monetary(
        string='Total Amount',
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id',
    )
    notes = fields.Text(string='Notes')
    purchase_request_id = fields.Many2one('mini.purchase.request', string='Source Request', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('order_line_ids.subtotal')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.order_line_ids.mapped('subtotal'))

    def action_confirm(self):
        for rec in self:
            if not rec.order_line_ids:
                raise ValidationError(_('Please add at least one product line before confirming.'))
            rec.state = 'confirmed'

    def action_receive(self):
        for rec in self:
            if rec.state != 'confirmed':
                raise ValidationError(_('Only confirmed orders can be marked as received.'))
            rec.state = 'received'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'received':
                raise ValidationError(_('Received orders cannot be cancelled.'))
            rec.state = 'cancelled'

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('mini.purchase.order') or 'New'
        return super().create(vals_list)