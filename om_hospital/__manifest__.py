{
    'name': 'Hospital Management System',
    'author': 'Cambodian Devs Team',
    'license': 'AGPL-3',
    'version': '17.0.1.1',
    'depends': [
        'base',
        'mail',
        'product',
        'account'
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/patient_view.xml',
        'views/patient_readonly_view.xml',
        'views/doctor_view.xml',
        'views/appointment_view.xml',
        'views/appointment_line_view.xml',
        'views/patient_tag_view.xml',
        'views/account_move_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'om_hospital/static/src/css/hospital.css',
        ],
    },
    'installable': True,
    'application': True,
} # type: ignore