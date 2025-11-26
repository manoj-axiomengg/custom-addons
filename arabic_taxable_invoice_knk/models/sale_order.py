from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attention = fields.Char("Attention")
    fax = fields.Char("FAX")
    customer_rfq = fields.Char("Customer RFQ #")
    delivery_terms = fields.Char("Delivery Terms")
    manufacturer = fields.Char("Manufacturer")
    delivery_period = fields.Char("Delivery Period")
