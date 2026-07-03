from typing import Self
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CusCarTest(models.Model):
    _name = 'rma.cus.car.test'
    _inherit = ['mail.thread']
    _description = 'Test Drive Booking'
    _rec_name = 'booking_code'

    booking_code = fields.Char(
        string='Booking Reference',
        default='New',
        copy=False,
        readonly=True,
    )
    car_id = fields.Many2one('rma.car', string='Car', required=True, tracking=True, domain=[('qty', '>', 0)])
    car_qty = fields.Integer(related='car_id.qty', store=True, readonly=True)
    customer_id = fields.Many2one('rma.customer', string='Customer', required=True, tracking=True)
    phone = fields.Char(related='customer_id.phone', store=True, readonly=True)
    email = fields.Char(related='customer_id.email', store=True, readonly=True)
    address = fields.Text(related='customer_id.address', store=True, readonly=True)
    brand_id = fields.Many2one(related='car_id.brand_id', store=True, readonly=True)
    model = fields.Char(related='car_id.model', store=True, readonly=True)
    year = fields.Integer(related='car_id.year', store=True, readonly=True)
    colorcode = fields.Char(related='car_id.colorcode', store=True, readonly=True)
    engine = fields.Char(related='car_id.engine', store=True, readonly=True)
    test_time = fields.Datetime(string='Test Time', required=True, tracking=True)
    test_time_end = fields.Datetime(string='Test Time End', tracking=True , required=True)
    license_plate_id = fields.Many2one('rma.car.test.plate', string='License Plate', tracking=True)
    not_interested_reason = fields.Text(
        string='Reason',
        tracking=True,
        )
    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('not_interested', 'Not Interested'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)


    test_notes = fields.Text(string='Test Notes', tracking=True)
    sale_order_id = fields.Many2one('rma.sale_order', string='Sale Order', readonly=True, tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('booking_code', 'New') == 'New':
                vals['booking_code'] = self.env['ir.sequence'].next_by_code(
                    'rma.cus.car.test'
                ) or 'New'
        return super().create(vals_list)

    @api.constrains('test_time')
    def _check_test_time(self):
        for rec in self:
            if rec.test_time and rec.test_time < fields.Datetime.now():
                raise ValidationError(
                    _('Test drive time cannot be in the past.')
                )
    @api.constrains('test_time', 'test_time_end')
    def _check_test_time_end(self):
        for rec in self:
            if rec.test_time and rec.test_time_end < rec.test_time:
                raise ValidationError(
                    _('Test drive end time cannot be before test drive start time.')
                )

    @api.constrains('car_id', 'test_time', 'test_time_end', 'status')
    def _check_duplicate_booking(self):
        for rec in self:
            if rec.status in ('cancelled', 'not_interested'):
                continue
            overlapping = self.env['rma.cus.car.test'].search_count([
                ('car_id', '=', rec.car_id.id),
                ('id', '!=', rec.id),
                ('status', 'in', ['pending', 'confirmed']),
                ('test_time', '<', rec.test_time_end),
                ('test_time_end', '>', rec.test_time),
            ])
            if overlapping:
                raise ValidationError(
                    _('"%s" already has an active test drive booking from %s to %s that overlaps with the selected time. '
                      'Please choose a different time slot.') % (rec.car_id.name, rec.test_time, rec.test_time_end)
                )

    @api.ondelete(at_uninstall=False)
    def _check_deletable(self):
        for rec in self:
            if rec.status == 'pending':
                raise ValidationError(
                    _('You cannot delete booking "%s" because it is currently Pending.') % rec.booking_code
                )
            if rec.status == 'confirmed':
                raise ValidationError(
                    _('You cannot delete booking "%s" because it is already Confirmed.') % rec.booking_code
                )
    def action_pending(self):
        for rec in self:
            rec.status = 'pending'
    def action_confirm(self):
        self.ensure_one()
        self.status = 'confirmed'
        template = self.env.ref('RMA_Car_MGM.email_template_test_drive_confirmed', raise_if_not_found=False)
        if template and self.customer_id.email:
            template.send_mail(self.id, force_send=True)
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Sale Order',
            'res_model': 'rma.sale_order',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_car_id': self.car_id.id,
                'default_customer_id': self.customer_id.id,
                'default_booking_id': self.id,
            },
        }

    def action_open_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'rma.sale_order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }

    def action_cancel(self):
        for rec in self:
            rec.status = 'cancelled'

    def action_not_interested(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reason for Not Interested',
            'res_model': 'rma.not.interested.wizard',
            'view_mode': 'form',
            'target': 'new',   
            'context': {
                'default_booking_id': self.id,
            },
    }

