from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approved_by_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False
    )

    def button_approve(self, force=False):
        res = super(PurchaseOrder, self).button_approve(force=force)
        for order in self:
            order.approved_by_id = self.env.user.id
            if 'picking_ids' in order._fields and order.picking_ids:
                order.picking_ids.action_assign()
        return res