from odoo import models, fields, api

class CrmLeadLine(models.Model):
    _name = 'crm.lead.line'
    _description = 'Enquiry Product Lines'

    lead_id = fields.Many2one('crm.lead', string='Enquiry', ondelete='cascade', required=True)
    sequence = fields.Integer(string="Sl. No.")
    product_id = fields.Many2one('product.template', string='Product')
    item_id = fields.Char(string="ITM-ID", store=True)
    customer_stock_code = fields.Char(string="Cus Stock Code", store=True)
    name = fields.Char(string='Description')
    product_uom_qty = fields.Float(string='Quantity', default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    # price_unit = fields.Float(string='Unit Price')
    cost_type = fields.Selection([
        ('maf-cs', 'MAF-CS'),
        ('trad-cs', 'TRAD-CS'),
        ('other', 'Other'),
    ], string="COST-TYPE")

    @api.onchange('product_id')
    def _onchange_product_id_set_values(self):
        if self.product_id:
            self.item_id = self.product_id.default_code or False
            self.customer_stock_code = self.product_id.x_studio_cus_stock_code or False
            self.name = self.product_id.name
            self.product_uom_id = self.product_id.uom_id.id


    


    @api.onchange("lead_id")
    def _onchange_lead_id(self):
        """Assign Sl.No immediately when line is added in CRM lead."""
        if self.lead_id and not self.sequence:
            existing_numbers = self.lead_id.enquiry_line_ids.mapped("sequence")
            self.sequence = (max(existing_numbers) if existing_numbers else 0) + 1

    @api.model
    def create(self, vals):
        # If vals is a list → multi create operation
        if isinstance(vals, list):
            for val in vals:
                self._assign_sequence(val)
            return super().create(vals)

        # Single create
        self._assign_sequence(vals)
        return super().create(vals)

    def _assign_sequence(self, vals):
        """Internal reusable logic for assigning sequence."""
        lead_id = vals.get("lead_id")
        if lead_id and "sequence" not in vals:
            lead = self.env["crm.lead"].browse(lead_id)
            max_seq = max(lead.enquiry_line_ids.mapped("sequence") or [0])
            vals["sequence"] = max_seq + 1
