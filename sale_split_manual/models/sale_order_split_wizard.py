from odoo import api, fields, models, _

class SaleOrderSplitWizard(models.TransientModel):
    _name = 'sale.order.split.wizard'
    _description = 'Wizard to split a sale.order into multiple orders'

    sale_order_id = fields.Many2one('sale.order', string='Quotation', required=True)
    orders_count = fields.Integer(string='Number of Orders', default=2, required=True)
    cancel_original = fields.Boolean(
        string='Cancel original quotation after creating orders',
        default=False
    )
    line_ids = fields.One2many('sale.order.split.line', 'wizard_id', string='Quotation Lines')
    

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        sale_order_id = self.env.context.get('default_sale_order_id')
        if not sale_order_id:
            return res

        order = self.env['sale.order'].browse(sale_order_id)
        res['line_ids'] = [
            (0, 0, {
                'sale_line_id': line.id,
                'product_id': line.product_id.id,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom_id': line.product_uom_id.id,
                'tax_id': [(6, 0, line.tax_ids.ids)],
                'price_unit': line.price_unit,
                'order_number': 1,
            }) for line in order.order_line
        ]
        return res


    

    def action_create_orders(self):
        self.ensure_one()
        if not self.line_ids:
            raise models.ValidationError(_('No lines to split.'))

        order_numbers = sorted(set(self.line_ids.mapped('order_number')))
        order_map = {}
        created_orders = self.env['sale.order']

        for num in order_numbers:
            vals = {
                'partner_id': self.sale_order_id.partner_id.id,
                'pricelist_id': self.sale_order_id.pricelist_id.id,
                'team_id': self.sale_order_id.team_id.id,
                'payment_term_id': self.sale_order_id.payment_term_id.id,
                'campaign_id': self.sale_order_id.campaign_id.id,
                'medium_id': self.sale_order_id.medium_id.id,
                'lead_id': self.sale_order_id.lead_id.id,
                'partner_invoice_id': self.sale_order_id.partner_invoice_id.id,
                'partner_shipping_id': self.sale_order_id.partner_shipping_id.id,
                'client_order_ref': self.sale_order_id.client_order_ref,
                'origin': self.sale_order_id.name,
            }
            new_order = self.env['sale.order'].create(vals)
            order_map[num] = new_order
            created_orders |= new_order

        for wline in self.line_ids:
            target = order_map.get(wline.order_number)
            if not target:
                continue

            max_seq = max(target.order_line.mapped('sequence') or [0]) + 1

            line_vals = {
                'order_id': target.id,
                'product_id': wline.product_id.id,
                'name': wline.name,
                'product_uom_qty': wline.product_uom_qty,
                'product_uom_id': wline.product_uom_id.id,
                'price_unit': wline.price_unit,
                'tax_ids': [(6, 0, wline.tax_id.ids)],
                'sequence': max_seq,
            }

            new_line = self.env['sale.order.line'].create(line_vals)
            new_line._compute_amount()
        created_orders.action_confirm()
        msg = _('Orders created from quotation %s') % (self.sale_order_id.name)
        for new_order in created_orders:
            new_order.message_post(body=msg)

        if self.cancel_original:
            try:
                self.sale_order_id.action_cancel()
            except Exception:
                self.sale_order_id.message_post(
                    body=_('Warning: original quotation could not be cancelled.')
                )

        
    

        print("================ Wizard lines ================")
        for line in self.line_ids:
            print(
                "Sale Line ID:", line.sale_line_id.id,
                "Product:", line.product_id.name,
                "Qty:", line.product_uom_qty,
                "Unit:", line.product_uom_id.name,
                "Price:", line.price_unit,
                "Order Number:", line.order_number
            )
        return {
            'name': _('Generated Sales Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_orders.ids)],
        }    





class SaleOrderSplitLine(models.TransientModel):
    _name = 'sale.order.split.line'
    _description = 'Temporary line for sale.order split wizard'

    wizard_id = fields.Many2one('sale.order.split.wizard', ondelete='cascade')
    sale_line_id = fields.Many2one('sale.order.line')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Text(string='Description')
    product_uom_qty = fields.Float(string='Quantity')
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    price_unit = fields.Float(string='Unit Price')
    tax_id = fields.Many2many('account.tax')
    order_number = fields.Integer(default=1)
