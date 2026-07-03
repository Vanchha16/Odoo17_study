from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Field 1 — Boolean: mark this contact as school-related
    is_school_partner = fields.Boolean(string='School Partner', default=False)

    # Field 2 — Selection: role this partner plays in the school
    school_partner_role = fields.Selection([
        ('parent', 'Parent / Guardian'),
        ('sponsor', 'Sponsor'),
        ('alumni', 'Alumni'),
        ('vendor', 'Vendor'),
    ], string='Partner Role')

    # Field 3 — Char: official MoE registration or partner reference number
    moe_ref_no = fields.Char(string='MoE Ref No.')

    # Field 4 — Many2one: linked student record
    student_id = fields.Many2one('school.student', string='Linked Student')
