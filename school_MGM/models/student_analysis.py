from odoo import models, fields, tools


class StudentAnalysis(models.Model):
    _name = 'school.student.analysis'
    _description = 'Student Analysis'
    _auto = False
    _rec_name = 'student_name'

    student_id = fields.Many2one('school.student', string='Student', readonly=True)
    student_name = fields.Char(string='Student Name', readonly=True)
    student_code = fields.Char(string='Student Code', readonly=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], string='Gender', readonly=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('enrolled', 'Enrolled'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True)
    age = fields.Integer(string='Age', readonly=True)
    major_id = fields.Many2one('school.major', string='Major', readonly=True)
    group_id = fields.Many2one('school.group', string='Group', readonly=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', readonly=True)
    semester_id = fields.Many2one('school.semester', string='Semester', readonly=True)
    program_year_id = fields.Many2one('school.program.year', string='Program Year', readonly=True)
    student_count = fields.Integer(string='Student Count', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW school_student_analysis AS (
                SELECT
                    s.id                    AS id,
                    s.id                    AS student_id,
                    s.name                  AS student_name,
                    s.student_code          AS student_code,
                    s.gender                AS gender,
                    s.status                AS status,
                    s.age                   AS age,
                    s.major_id              AS major_id,
                    s.group_id              AS group_id,
                    s.academic_year_id      AS academic_year_id,
                    s.semester_id           AS semester_id,
                    s.program_year_id       AS program_year_id,
                    1                       AS student_count
                FROM school_student s
            )
        """)