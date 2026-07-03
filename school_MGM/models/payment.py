from odoo import models, fields, api, _


class Payment(models.Model):
    _name = 'school.payment'
    _description = 'Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'reference'

    reference = fields.Char(string='Reference', required=True, readonly=True, copy=False, default='New')
    payment_date = fields.Datetime(string='Payment Date', required=True, default=fields.Datetime.now() , tracking=True)

    student_id = fields.Many2one('school.student', string='Student', required=True , tracking=True)
    group_id = fields.Many2one('school.group', string='Group', required=True, tracking=True)
    major_id = fields.Many2one('school.major', string='Major', required=True, tracking=True)
    over_due = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Over Due', default='no')
    payment_amount = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('paid_50', 'Paid 50%'),
    ], default='unpaid', string='Payment Status', required=True)
    payment_method = fields.Selection([('cash', 'Cash'), ('aba', 'ABA Bank'), ('acleda', 'Acleda') , ('other', 'Other')],
                                      string='Payment Method', default='cash')
    academic_year_id = fields.Many2one(
        'school.academic.year',
        related='group_id.academic_year_id',
        string='Academic Year',
        store=True,
        readonly=True
    )
    semester_id = fields.Many2one('school.semester',
                                  related='group_id.semester_id',
                                  string='Semester',
                                  tracking=True)
    program_year_id = fields.Many2one('school.program.year',
                                      related='group_id.program_year_id',
                                      string='Program Year',
                                      tracking=True)


    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('school.payment') or _('New')
        return super(Payment, self).create(vals)

    def action_print_receipt(self):
        return self.env.ref('school_MGM.action_report_student_payment').report_action(self)

    def action_confirm_payment(self):
        if self.payment_amount == 'unpaid':
            self.student_id.status = 'draft'
            template = self.env.ref('school_MGM.email_template_school_unpaid', raise_if_not_found=False)
            if template and self.student_id.email:
                template.send_mail(self.student_id.id, force_send=True)
        else:
            self.student_id.status = 'enrolled'
            template = self.env.ref('school_MGM.email_template_student_enrolled', raise_if_not_found=False)
            if template and self.student_id.email:
                template.send_mail(self.student_id.id, force_send=True)

