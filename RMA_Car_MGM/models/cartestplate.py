from odoo import models, fields

class CarTestPlate(models.Model):
    _name = 'rma.car.test.plate'
    _description = 'Test Drive License Plate'
    _rec_name = 'license_plate'

    test_id = fields.Many2one('rma.car', string='Car', ondelete='cascade')
    license_plate = fields.Char(string='License Plate')
    license_plate_ids = fields.One2many('rma.car.test.plate', 'test_id', string='License Plates')
    _sql_constraints = [
        ('license_plate_unique', 'unique(license_plate)', 'License Plate must be unique!'),
    ]