
{
    "name": "Sales Paper Layout Config",
    "version": "19.0.1.0",
    "author": "Manoj",
    "category": "Sales",
    "depends": [
        "account","sale","custom_internal_layout_knk"
    ],
    
    "data": [
        "data/report_paperformat.xml",
        "report/account_report.xml",
        "views/sale_order_view.xml",
        "views/invoice_report.xml",
        "views/account_move_views.xml",
        "views/res_company.xml",
         
    ],
    'images': [
        'static/description/banner.jpg'
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
