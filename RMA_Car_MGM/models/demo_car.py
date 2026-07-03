from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DemoCar(models.Model):
    _name = 'rma.demo.car'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Demo Cars'
    _rec_name = 'car_id'

    car_id   = fields.Many2one('rma.car', string='Car', required=True)
    models   = fields.Char(related='car_id.model',      store=True, readonly=True)
    years    = fields.Integer(related='car_id.year',    store=True, readonly=True)
    colors   = fields.Char(related='car_id.colorcode',  store=True, readonly=True)
    engines  = fields.Char(related='car_id.engine',     store=True, readonly=True)
    brand_id = fields.Many2one(related='car_id.brand_id', store=True, readonly=True)
    qty_demo = fields.Integer(string='Quantity', required=True)
    status   = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', tracking=True)

    @api.constrains('qty_demo')
    def _check_demo_car(self):
        for rec in self:
            if rec.qty_demo > rec.car_id.qty:
                raise ValidationError(
                    "Quantity cannot be greater than the available quantity of the car."
                )