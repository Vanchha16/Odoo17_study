{
    'name': 'RMA Car MGM',
    'version': '1.0',
    'category': 'RMA Car Management System',
    'license': 'LGPL-3',
    'sequence': 1,
    'summary': 'RMA Car MGM',
    'description': """
        RMA Car MGM
    """,
    'author': 'RMA',
    'depends': ['base',
                'mail',
                ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/email_template.xml',
        'views/car/car_view_only.xml',
        'views/car/car.xml',
        'views/car/licenseplate.xml',
        'views/car/demo_car.xml',
        'views/car/view_demo_car.xml',
        'views/brand/brand.xml',
        'views/customer/customer_view.xml',
        'views/customer/customer.xml',
        'views/customer/cus_register.xml',
        'views/customer/cus_test_drive.xml',
        'views/sale/salesperson.xml',
        'views/sale/sale_order.xml',
        'views/menu.xml',
        'reports/sale_order_report.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'RMA_Car_MGM/static/src/css/brand.css',
        ],
    },
    'installable': True,
    'application': True
}