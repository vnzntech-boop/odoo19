from odoo import api,fields,models,_
from _datetime import datetime,date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class UpdateMembershipWizard(models.TransientModel):
    _name = 'update.wizard'
    _description = "Model for update membership"
    
    partner_id = fields.Many2one('res.partner',string="Client")
    updated_date = fields.Char('Current Validity')
    membership = fields.Integer(string="Membership")

    

    @api.model
    def default_get(self, fields):
        defaults = super(UpdateMembershipWizard, self).default_get(fields)
        active_id = self._context.get('active_id')
        if active_id:
            active_record = self.env['res.partner'].browse(active_id)
            defaults['partner_id'] = active_record.id
        return defaults

    @api.onchange('membership')
    def get_date(self):
        if self.partner_id.validity:
            self.updated_date= self.partner_id.validity
        else:
            self.updated_date = self.partner_id.joining_date
    
    

    def update_membership(self):
        for rec in self:
            rec.partner_id.expiry_in_months = rec.partner_id.expiry_in_months + rec.membership
            rec.partner_id.membership = rec.membership
            membership = rec.partner_id.membership
            validity = rec.updated_date
        
        number = int(membership)
        date_str = str(validity)
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = date_obj.strftime('%Y/%m/%d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        formatted_date = str(formatted_date)
        input_date = datetime.strptime(formatted_date, '%Y-%m-%d')
        calculated_date = input_date + relativedelta(months=number)
        calculated_date = str(calculated_date)
        calculated_date = calculated_date[:-9]
        self.partner_id.validity = calculated_date

        payment_record = self.env['account.payment'].create({
            'partner_id': self.partner_id.id,
            'state':'draft',
            'base_fee':500,
            'caution_deposit':2000,
            
        })
        return payment_record
        
   
                