from odoo import models, fields, api ,_
from odoo.exceptions import ValidationError

class sale_order(models.Model):
    _name = 'rma.sale_order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Order'

    sale_code = fields.Char(string='Sale Code' , tracking=True , default='New')
    car_id = fields.Many2one('rma.car', string='Car', required=True , tracking=True)
    customer_id = fields.Many2one('rma.customer', string='Customer', required=True , tracking=True)
    seller_id = fields.Many2one('rma.seller', string='Seller', required=True , tracking=True)
    qty = fields.Integer(string='Quantity', required=True , tracking=True)
    sale_date = fields.Date(string='Sale Date', required=True , tracking=True)
    brand_id = fields.Many2one(related='car_id.brand_id', store=True, readonly=True)
    commission_rate = fields.Float(related='car_id.commission_rate', store=True, readonly=True)
    car_price = fields.Float(related='car_id.price', store=True, readonly=True)
    models = fields.Char(related='car_id.model', store=True, readonly=True)
    years = fields.Integer(related='car_id.year', store=True, readonly=True)
    colors = fields.Char(related='car_id.colorcode', store=True, readonly=True)
    engines = fields.Char(related='car_id.engine', store=True, readonly=True)


    total_car_in_stock = fields.Integer(
        string='Cars In Stock',
        compute='_compute_total_car_in_stock',
        store=False,
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('delivered', 'Delivered'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    booking_id = fields.Many2one('rma.cus.car.test', string='Test Drive Booking', readonly=True)

    def action_save_sale(self):
        self.status = 'draft'
        return self.env.ref('RMA_Car_MGM.action_report_sale_order_invoice').report_action(self)

    def action_print_invoice(self):
        return self.env.ref('RMA_Car_MGM.action_report_sale_order_invoice').report_action(self)
    def action_draft(self):
        self.status = 'draft'

    def action_delivered(self):
        self.status = 'delivered'

    def action_done(self):
        if self.status != 'delivered':
            raise ValidationError(
                _('Only delivered sales orders can be marked as done.')
            )
        if self.qty > self.car_id.qty:
            raise ValidationError(
                _('Not enough stock to complete this sale. Available: %d, Required: %d') % (self.car_id.qty, self.qty)
            )
        self.car_id.qty -= self.qty
        self.status = 'done'
        template = self.env.ref('RMA_Car_MGM.email_template_sale_order_done', raise_if_not_found=False)
        if template and self.customer_id.email:
            template.send_mail(self.id, force_send=True)

    def action_cancel(self):
        if self.status == 'done':
            self.car_id.qty += self.qty
        self.status = 'cancelled'

    commission_amount = fields.Monetary(
        string='Commission Amount',
        compute='_compute_commission',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('car_id', 'car_id.qty')
    def _compute_total_car_in_stock(self):
        for rec in self:
            rec.total_car_in_stock = rec.car_id.qty if rec.car_id else 0

    car_qty_available = fields.Integer(related='car_id.car_availability', store=True, readonly=True)
    @api.constrains('qty', 'car_qty_available')
    def _check_qty(self):
        for rec in self:
            if rec.qty > rec.car_qty_available | rec.qty == rec.car_qty_available:
                raise ValidationError(
                    _('You cannot sell more cars than available in stock. Available: %d, Requested: %d') % (rec.car_qty_available, rec.qty)
                )

    @api.depends('car_price', 'commission_rate')
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = (rec.car_price * rec.qty) * (rec.commission_rate / 100)
            print("Odoo testing", rec.commission_amount)

    @api.onchange('car_id', 'qty')
    def _onchange_commission(self):
        self._compute_commission()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sale_code', 'New') == 'New':
                vals['sale_code'] = self.env['ir.sequence'].next_by_code('rma.sale_order') or 'New'
        records = super(sale_order, self).create(vals_list)
        for rec in records:
            if rec.booking_id:
                rec.booking_id.sale_order_id = rec.id
        return records


