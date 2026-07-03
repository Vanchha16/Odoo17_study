from  odoo import models, fields, api ,_
from odoo.exceptions import ValidationError



class Car(models.Model):
    _name = 'rma.car'
    _inherit = ['mail.thread']
    _description = 'Vehicles'

    name = fields.Char(string='Name', required=True , tracking=True)
    qty = fields.Integer(string='Quantity', required=True , tracking=True)
    model = fields.Char(string='Model', required=True , tracking=True)
    year = fields.Integer(string='Year', required=True , tracking=True)
    colorcode = fields.Char(string='Color Code', required=True , tracking=True)
    engine = fields.Char(string='Engine', required=True     , tracking=True)
    car_for_test = fields.Integer(string='Car For Test', tracking=True)
    status = fields.Selection([
        ('available', 'Available'),
        ('not_available', 'Not Available'),
    ], string='Status', default='available', tracking=True)
    brand_id = fields.Many2one('rma.brand', string='Brand', required=True , tracking=True)
    cus_car_test_ids = fields.One2many('rma.cus.car.test', 'car_id', string='Test Drive')
    car_count_from_test = fields.Integer(
        string='Car Count from Test',
        compute='_compute_car_count_from_test',
        store=True,
        help='Total number of cars from test'
    )
    # qty_on_test_drive = fields.Integer(
    #     string='Cars Currently on Test Drive',
    #     compute='_compute_qty_on_test_drive',
    #     store=True,
    #     help='Number of cars currently held by active (pending/confirmed) test drive bookings'
    # )
    license_plate_ids = fields.One2many('rma.car.test.plate', 'test_id', string='License Plates')
    @api.onchange('car_for_test')
    def _onchange_car_for_test(self):
        if self.car_for_test < 0:
            self.car_for_test = 0
            return

        current_count = len(self.license_plate_ids)
        target = self.car_for_test

        if target > current_count:
            for _ in range(target - current_count):
                self.license_plate_ids = [(0, 0, {'license_plate': ''})]

        elif target < current_count:
            to_remove = self.license_plate_ids[target:]
            self.license_plate_ids = [(3, rec.id, 0) for rec in to_remove]

    # @api.depends('cus_car_test_ids.status')
    # def _compute_qty_on_test_drive(self):
    #     for car in self:
    #         active_bookings = car.cus_car_test_ids.filtered(
    #             lambda t: t.status in ('confirmed')
    #         )
    #         car.qty_on_test_drive = len(active_bookings)

    @api.depends('cus_car_test_ids')
    def _compute_car_count_from_test(self):
        for car in self:
            car.car_count_from_test = len(car.cus_car_test_ids)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('available', 'Available'),
        ('sold', 'Sold'),
    ], string='Status', default='draft', tracking=True)
    price = fields.Float(string='Price', required=True , tracking=True)

    commission_rate = fields.Float(
        string='Commission Rate (%)',
        default=1.0,
        tracking=True,
        help='Percentage commission earned on sales of this brand'
    )

    car_availability = fields.Integer(
        string='Car Availability',
        compute='_compute_car_availability',
        store=True,
        help='Percentage of cars available in stock'
    )
    sale_ids = fields.One2many('rma.sale_order', 'car_id', string='Sales')

    @api.depends('qty' ,'sale_ids.qty')
    def _compute_car_availability(self):
        for car in self:
            car.car_availability = car.qty - sum(car.sale_ids.mapped('qty')) 

    def action_save_custom(self):
        self.write({
            'state': 'available',
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Saved!'),
                'message': _('Vehicle has been saved successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        if self.brand_id and self.brand_id.status == 'inactive':
            self.brand_id = False
            return {
                'warning': {
                    'title': _('Inactive Brand'),
                    'message': _('You cannot add a car to an inactive brand.'),
                }
            }

    @api.constrains('brand_id')
    def _check_brand_active(self):
        for rec in self:
            if rec.brand_id and rec.brand_id.status == 'inactive':
                raise ValidationError(
                    _('You cannot add a car to an inactive brand.')
                )

    availability_status = fields.Selection([
        ('sold_out', 'Sold Out'),
        ('available', 'Available'),
    ], compute='_compute_availability_status', store=True)

    @api.depends('car_availability')
    def _compute_availability_status(self):
        for rec in self:
            rec.availability_status = 'sold_out' if rec.car_availability <= 0 else 'available'

