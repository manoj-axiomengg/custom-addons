{
    'name': 'Sale: Split Quotation (Manual)',
    'version': '1.0.0',
    'summary': 'Split a quotation into multiple sales orders using a manual wizard',
    'category': 'Sales',
    'author': 'Custom',
    'website': 'https://example.com',
    'license': 'LGPL-3',
    'depends': ['sale_management','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_order_split_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}