from odoo import models, fields, api


class ViewStudentReport(models.AbstractModel):
    _name = 'report.school_MGM.report_student_template'
    _description = 'Student Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['school.student'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'school.student',
            'docs': docs,
        }