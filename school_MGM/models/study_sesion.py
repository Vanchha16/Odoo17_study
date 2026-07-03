from odoo import models, fields, api

class StudySession(models.Model):
    _name = 'school.study.session'
    _description = 'Study Session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'label'


    label = fields.Char(string='Session Label', required=True, tracking=True)
    session = fields.Selection([('session1', 'Session 1'), ('session2', 'Session 2'), ('session3', 'Session 3')],
                               string='Session', required=True, tracking=True)
    period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening')],
                              string='Period', required=True, tracking=True)
    start_time = fields.Float(string='Start Time', required=True, tracking=True)
    end_time = fields.Float(string='End Time', required=True, tracking=True)
