from odoo import fields,models,api,_
from _datetime import datetime,date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PaymentModel(models.Model):
    _name = 'payments.model'
    _description = "model for payments"

    _rec_name='partner_id'

    state = fields.Selection([('unpaid','Un Paid'),('paid','Paid')])

    partner_id = fields.Many2one('res.partner','Name of client')
    membership = fields.Integer(string = "Membership",related = 'partner_id.membership')
    
    offers = fields.Selection([('10','Christmas offer'),('20','New Year offer'),('30','Financial year end')])
    base_fee = fields.Integer(string="Base Fee per month",default = 500)
    caution_deposit = fields.Integer(string="Caution Deposit",default = 2000)
    is_caution_paid =fields.Boolean(string="Paid")
    fees = fields.Integer(string="Fees")
    remaining_fees = fields.Integer(string="Total Remainig Fees",compute = 'calculate_remining_fees')

    payment_line_ids = fields.One2many('payment.model.lines','payment_id',string='Payments')


    def send_mail(self):
        template_id = self.env.ref('fitness_management_system.email_template_inform_pending_fee')
        if template_id:
                template_id.send_mail(self.id)


    @api.model
    def create(self,vals):
        
        res = super(PaymentModel,self).create(vals)        
        return res
    
    def write(self,vals):
        
        
        res = super(PaymentModel,self).write(vals)
        
        return res
    
    @api.depends('payment_line_ids')
    def calculate_remining_fees(self):
        total_fee = 0
        for rec in self:
            total_fee = total_fee + (rec.membership * rec.base_fee)
            if int(rec.offers) > 0:
                reduction = total_fee / int(rec.offers)
                total_fee  = total_fee - reduction
        paid_amount = 0
        for rec in self.payment_line_ids:
            paid_amount = paid_amount + rec.amount_paid

        total_fee = total_fee - paid_amount

        self.remaining_fees = total_fee

        if self.remaining_fees == 0:
            self.state = 'paid'
            self.payment_line_ids.payment_status = 'paid'
        elif self.remaining_fees !=0:
            self.state = 'unpaid'
            self.payment_line_ids.payment_status = 'paid'

   
    
    

    _sql_constraints = [
        ('unique_fields', 'unique(partner_id)', 'Error: Record already exist!'),
    ]


    


class PaymentModelLines(models.Model):
    _name='payment.model.lines'
    _description="for payment tracking"

    payment_id = fields.Many2one('payments.model')

    date_field = fields.Date(string="Date")
    
    actual_amount = fields.Integer(string="Fees/Pending amount")
    amount_paid= fields.Integer(string="Amount Paid")
    balance_amount = fields.Char(string="Balance")
    payment_status = fields.Selection([('paid','Paid'),('pending','Pending')],default = 'pending')
