from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    custom_sequence = fields.Char(
        string="Enquiry No",
        readonly=True,
        copy=False,
        default='New'
    )
    item_count = fields.Integer(
        string="No. of Items",
        compute="_compute_item_count",
        store=True
    )

    @api.depends('enquiry_line_ids')
    def _compute_item_count(self):
        for lead in self:
            lead.item_count = len(lead.enquiry_line_ids)
    
    def action_reject_lead(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'crm.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    @api.model
    def create(self, vals):
        # If list of values → multiple record creation
        if isinstance(vals, list):
            for data in vals:
                if data.get('custom_sequence', 'New') == 'New':
                    data['custom_sequence'] = self.env['ir.sequence'].next_by_code(
                        'crm.lead.custom.seq'
                    ) or 'New'
            records = super(CrmLead, self).create(vals)
        else:
            # Single record creation
            if vals.get('custom_sequence', 'New') == 'New':
                vals['custom_sequence'] = self.env['ir.sequence'].next_by_code(
                    'crm.lead.custom.seq'
                ) or 'New'
            records = super(CrmLead, self).create(vals)

        return records

    is_enquiry = fields.Boolean(string='Is Enquiry', default=False)
    enquiry_line_ids = fields.One2many('crm.lead.line', 'lead_id', string='Enquiry Lines')
    quotation_ids = fields.One2many('sale.order', 'lead_id', string='Quotations', domain=[('state', '!=', 'sale')])
    sale_order_ids = fields.One2many('sale.order', 'lead_id', string='Sales Orders')

    quotation_count = fields.Integer(
        string="Quotation Count",
        compute="_compute_quotation_count",
        store=False
    )

    def _compute_quotation_count(self):
        for rec in self:
            standard_q = rec.order_ids.filtered(lambda s: s.state in ('draft', 'sent'))
            custom_q = rec.quotation_ids
            rec.quotation_count = len(standard_q | custom_q)

    # -----------------------------
    # ACTION: OPEN QUOTATIONS
    # -----------------------------
    def action_view_sale_quotation(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.action_quotations_with_onboarding"
        )

        # DOMAIN → SHOW BOTH STANDARD + CUSTOM
        action['domain'] = [
            '|',
            ('opportunity_id', '=', self.id),   # Odoo standard logic
            ('lead_id', '=', self.id)           # Your custom logic
        ]

        # MERGE BOTH SETS OF QUOTATIONS
        merged = (self.order_ids | self.quotation_ids).filtered(
            lambda s: s.state in ('draft', 'sent')
        )

        # CONTEXT when creating a NEW quotation
        action['context'] = {
            'default_opportunity_id': self.id,
            'default_lead_id': self.id,
            'default_partner_id': self.partner_id.id,
        }

        # IF ONLY ONE QUOTATION → OPEN FORM DIRECTLY
        if len(merged) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = merged.id

        return action

    def action_create_quotation(self):
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('Please select a customer on the enquiry before creating a quotation.'))
        SaleOrder = self.env['sale.order']
        order_vals = {
            'partner_id': self.partner_id.id,
            'opportunity_id': self.id,
            'lead_id': self.id,
            'team_id': self.team_id.id if self.team_id else False,
            'note': self.description or False,
        }
        order = SaleOrder.create(order_vals)

        # create order lines from enquiry lines (if any)
        if self.enquiry_line_ids:
            order_lines = []
            for l in self.enquiry_line_ids:
                product = l.product_id
                if not product:
                    continue
                uom = l.product_uom_id or product.uom_id
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'name': l.name or product.display_name,
                    'product_uom_qty': l.product_uom_qty,
                    # 'price_unit':  product.lst_price,
                    'product_uom_id': uom.id,
                }))
            if order_lines:
                order.write({'order_line': order_lines})
        # return action to open newly created quotation
        return {
            'name': _('Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': order.id,
            'view_mode': 'form',
            'target': 'current',
        }

