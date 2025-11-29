from odoo import models, fields, api, _

class CrmRejectWizard(models.TransientModel):
    _name = 'crm.reject.wizard'
    _description = 'CRM Reject Reason'

    rejection_reason = fields.Text(string="Reason", required=True)

    def action_reject(self):
        lead_id = self.env.context.get('active_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)

            # Write rejection reason to CRM Lead
            lead.write({
                'x_studio_rejection_reason': self.rejection_reason,
            })

            # Move to Rejected Stage if exists
            rejected_stage = self.env['crm.stage'].search([
                ('name', '=', 'Rejected')
            ], limit=1)

            if rejected_stage:
                lead.stage_id = rejected_stage.id
            else:
                lead.action_set_lost()

            # Post note in chatter
            lead.message_post(
                body=f"<b>Lead Rejected</b><br/>Reason: {self.rejection_reason}"
            )

        return {'type': 'ir.actions.act_window_close'}


