from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    lead_id = fields.Many2one('crm.lead', string='Enquiry/Lead', help='Reference to the originating Enquiry (crm.lead)')

    def action_view_enquiry(self):
        self.ensure_one()
        if not self.lead_id:
            return {'type': 'ir.actions.act_window_close'}
        return {
            'name': _('Enquiry'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': self.lead_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals.get('name') in ('New', '/', False):
                # Only assign quotation sequence initially
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.quotation') or '/'
        return super().create(vals_list)

    # Override action_confirm to assign sales order sequence on confirmation
    def action_confirm(self):
        for order in self:
            # If the current name is a quotation sequence, assign sales order sequence
            if order.name :
                order.name = self.env['ir.sequence'].next_by_code('sale.order') or '/'
        return super().action_confirm()
