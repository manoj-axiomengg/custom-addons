from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_count = fields.Integer(
        string='Sales Orders',
        compute='_compute_sale_count',
        store=False
    )

    @api.depends('origin')
    def _compute_sale_count(self):
        """Count how many Balance MOs were created from this MO."""
        for so in self:
            so.sale_count = self.env['sale.order'].search_count([
                ('origin', '=', so.name)
            ])

    def action_open_split_wizard(self):
        
        return {
            'name': 'Split Quotation into Multiple Orders',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.split.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
            },
        }
    
    def action_view_sale_order(self):
        """Show all Balance Manufacturing Orders created from this MO"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('origin', '=', self.name)],
            'context': {'create': False},
        }