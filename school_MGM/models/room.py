from odoo import models, fields, api


class Room(models.Model):
    _name = 'school.room'
    _inherit = ['mail.thread']
    _description = 'Room'
    _order = 'sequence, room_label'
    _rec_name = 'room_label'

    floor = fields.Selection([
        ('1', 'Floor 1'),
        ('2', 'Floor 2'),
        ('3', 'Floor 3'),
        ('4', 'Floor 4'),
        ('5', 'Floor 5'),
    ], string='Floor', required=True, tracking=True)

    room_code = fields.Selection([
        ('A', 'A'), ('B', 'B'), ('C', 'C'),
        ('D', 'D'), ('E', 'E'), ('F', 'F'),
        ('G', 'G'), ('H', 'H'), ('I', 'I'),
        ('J', 'J'),
    ], string='Room Code', required=True, tracking=True)

    room_label = fields.Char(
        string='Room',
        compute='_compute_room_label',
        store=True,
        readonly=True,
    )
    sequence = fields.Integer(string='Sequence', default=10)
    capacity = fields.Integer(string='Capacity', tracking=True)
    note = fields.Text(string='Note')

    @api.depends('floor', 'room_code')
    def _compute_room_label(self):
        for rec in self:
            if rec.floor and rec.room_code:
                rec.room_label = f"{rec.floor}{rec.room_code}"
            else:
                rec.room_label = ''

    _sql_constraints = [
        ('room_unique', 'UNIQUE(floor, room_code)',
         'This room already exists on this floor.'),
    ]