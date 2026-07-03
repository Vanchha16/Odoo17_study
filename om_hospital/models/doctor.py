from odoo import models, fields

class Doctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Hospital Doctor'

    name = fields.Char(string='Name', required=True)
    specialization = fields.Char(string='Specialization')