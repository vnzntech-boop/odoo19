from odoo import api,fields,models,_
from _datetime import datetime,date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class CancelMembership(models.TransientModel):
    _name = 'cancel.wizard'
    _description = "Model for cancel membership"

    partner_id = fields.Many2one('res.partner',string="Client")
    current_membership = fields.Integer(string="Balance Membership",related = 'partner_id.expiry_in_months')
    cancel_reason =fields.Text(string="Cancel Reason")

    @api.model
    def default_get(self, fields):
        defaults = super(CancelMembership, self).default_get(fields)
        active_id = self._context.get('active_id')
        if active_id:
            active_record = self.env['res.partner'].browse(active_id)
            defaults['partner_id'] = active_record.id
        
        return defaults
    
    def cancel_membership(self):
        self.partner_id.state = 'cancelled'
        for rec in self:
            rec.partner_id.cancel_reason = rec.cancel_reason
            rec.partner_id.membership = rec.current_membership
            rec.partner_id.expiry_in_months = 0
        payment_record = self.env['account.payment'].create({
                'partner_id': self.partner_id.id,
                'state':'draft',
                'base_fee':500,
                'caution_deposit':2000,
                'payment_type':'outbound',
                })
        return payment_record
            
            
