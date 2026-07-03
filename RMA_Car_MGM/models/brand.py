from itertools import count
from odoo.exceptions import ValidationError
from odoo import models, fields, api ,_

class Brand(models.Model):
    _name = 'rma.brand'
    _inherit = ['mail.thread']
    _description = 'Brands'

    car_ids = fields.One2many('rma.car', 'brand_id', string='Cars')
    name = fields.Char(string='Name', required=True, tracking=True)
    image = fields.Image(string='Image', max_width=1920, max_height=1920)
    avatar_128 = fields.Image(
        string='Logo',
        related='image',
        max_width=128,
        max_height=128,
        store=True,
    )
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', tracking=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)',
         'A brand with this name already exists.'),
    ]

    car_count_label = fields.Char(string='Cars', compute='_compute_car_count_label')
    @api.depends('car_ids')
    def _compute_car_count_label(self):
        for rec in self:
            count = len(rec.car_ids)
            if count == 0:
                rec.car_count_label = 'No Cars'
            elif count == 1:
                rec.car_count_label = '1 Car'
            else:
                rec.car_count_label = f'{count} Cars'

    @api.ondelete(at_uninstall=False)
    def _check_car_brand(self):
        for rec in self:
            domain = [('brand_id', '=', rec.id)]
            cars = self.env['rma.car'].search(domain)
            if rec.car_ids:
                raise ValidationError(
                    _('You cannot delete this brand because there are cars linked to it. Please delete the cars first.'))