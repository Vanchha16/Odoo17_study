{
    'name': 'Mini Procurement',
    'version': '1.0',
    'category': 'Procurement',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': 'Mini Procurement Module',
    'description': """
        Mini Procurement Module - Purchase Request and Purchase Order workflow
    """,
    'author': 'RMA',
    'depends': ['base', 'mail', 'product'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'reports/purchase_order_report.xml',
        'views/purchase_request.xml',
        'views/purchase_order.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}