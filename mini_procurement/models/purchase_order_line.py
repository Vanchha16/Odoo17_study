from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _name = 'mini.purchase.order.line'
    _description = 'Purchase Order Line'

    order_id = fields.Many2one('mini.purchase.order', string='Order', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Float(string='Quantity', required=True, default=1.0)
    price_unit = fields.Float(string='Unit Price', required=True, default=0.0)
    currency_id = fields.Many2one(
        'res.currency',
        related='order_id.currency_id',
        store=True,
        readonly=True,
    )
    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit