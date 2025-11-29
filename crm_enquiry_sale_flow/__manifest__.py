{
    "name": "CRM Enquiry to Quotation Flow",
    "version": "1.0.0",
    "category": "Sales/CRM",
    "summary": "Link CRM Enquiries to multiple Quotations and Sales Orders (flexible, minimal intrusion)",
    "description": "Adds Enquiry product lines, buttons to create quotations from enquiries and link SOs back to enquiries. Keeps using standard sale.order for quotations.",
    "author": "Generated for user",
    "license": "AGPL-3",
    "website": "",
    "depends": [
        "crm",
        "sale_management",
        "product","base"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/crm_lead_views.xml",
        "views/sale_order_views.xml",
        "views/crm_reject_wizard_view.xml",
    ],
    "installable": True,
    "application": False
}
