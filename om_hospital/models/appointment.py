from odoo import models, fields ,api

class Appointment(models.Model):
    _name = 'hospital.appointment'
    _rec_name = 'patient_id'
    _inherit = ['mail.thread']
    _description = 'Hospital Appointment'
    _rec_names_search = ['reference', 'patient_id']

    reference = fields.Char(string='Reference', tracking=True ,default='New')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True, tracking=True , ondelete='restrict')
    date_appointment = fields.Date(string='Date', required=True, tracking=True)
    note = fields.Text(string='Note', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    appointment_line_ids = fields.One2many('hospital.appointment.line', 'appointment_id', string='Appointment Lines')
    total_qty = fields.Float( compute='_compute_total_qty', string='Total Quantity' , store=True)
    date_of_birth = fields.Date(related='patient_id.date_of_birth' , store=True)

    @api.model_create_multi
    def create(self, vals_list):
        print("Odoo testing", vals_list)
        for vals in vals_list:
            if vals.get('reference', 'New') == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('hospital.appointment') or 'New'
        return super(Appointment, self).create(vals_list)

    @api.depends('appointment_line_ids' , 'appointment_line_ids.quantity')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.appointment_line_ids.mapped('quantity'))

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.reference} - {rec.patient_id.name}"

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'


    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_set_draft(self):
        for rec in self:
            rec.state = 'draft'

class AppointmentLine(models.Model):
        _name = 'hospital.appointment.line'
        _description = 'Hospital Appointment Line'

        appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
        product_id = fields.Many2one('product.product', string='Product' , required=True)
        # price_unit = fields.Float(string='Unit Price')
        quantity = fields.Float(string='Quantity', default=1)
        # price_subtotal = fields.Float(string='Subtotal', compute='_compute_price_subtotal')