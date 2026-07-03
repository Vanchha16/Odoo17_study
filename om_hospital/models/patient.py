from odoo import models, fields ,_ ,api
from odoo.addons.base.models.res_country import FLAG_MAPPING
from odoo.exceptions import ValidationError , UserError 

class Patient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread']
    _description = 'Hospital Patient'

    name = fields.Char(string='Name', required=True , tracking=True)
    age = fields.Integer(string='Age' ,tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender' ,tracking=True)
    image_1920 = fields.Image(string='Photo', max_width=1920, max_height=1920)
    image_128 = fields.Image(
        string='Photo (small)',
        related='image_1920',
        max_width=128,
        max_height=128,
        store=True
    )
    phone = fields.Char(string='Phone' ,tracking=True)
    email = fields.Char(string='Email' ,tracking=True)
    address = fields.Text(string='Address' ,tracking=True)
    date_of_birth = fields.Date(string='Date of Birth',tracking=True)
    active = fields.Boolean(string='Active', default=True ,tracking=True)
    tag_ids = fields.Many2many('patient.tag', 'patient_tag_rel', 'tag_id', string='Tags' ,tracking=True)

    @api.ondelete(at_uninstall=False)
    def _check_patient_appointment(self):
        for rec in self:
            domain = [('patient_id', '=', rec.id)]
            appointments = self.env['hospital.appointment'].search(domain)
            if appointments:
                raise ValidationError(_('You cannot delete this patient because there are appointments linked to it. Please delete the appointments first.'))

