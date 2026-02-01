from odoo import models, fields,api
from datetime import date
import io
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import base64

class CustomAccountPayment(models.Model):
    _inherit = 'account.payment'

    custom_field = fields.Char(string="custom")
    base_fee = fields.Integer(string = 'Base fee',default = 500)
    caution_deposit = fields.Integer(string="Caution Deposit",default = 2000)
    offers = fields.Selection([('10','Christmas offer'),('20','New Year offer'),('30','Financial year end'),('0','No offer')])
    membership = fields.Integer(string="Membership",related='partner_id.membership')
    caution_paid = fields.Boolean(string="is caution paid",related = 'partner_id.caution_paid')

    @api.onchange('partner_id','offers')
    def calculate_total_amount(self):
        record = self.env['res.partner'].search([('name', '=',self.partner_id.name)])
        membership =record.membership
        total_fee = membership * self.base_fee
        if self.offers:
            if int(self.offers)>0:
                reduction = total_fee / int(self.offers)
                total_fee  = total_fee - reduction
            else:
                total_fee = total_fee
        self.amount = total_fee

    def send_mail(self):
        template_id = self.env.ref('fitness_management_system.email_template_inform_pending_fee')
        if template_id:
                template_id.send_mail(self.id)

  


    def create_invoice(self):
        rec = self.env['product.product'].search([('name','=','amount')])
        if not rec:
            self.env['product.product'].create({
            'name': 'amount',
            'detailed_type':'service',
            'invoice_policy':'ordered'
            ,})
        

        new_record = self.env['account.move'].create({
                'partner_id': self.partner_id.id,
                'invoice_date':self.date,
                'amount':self.amount,
                'move_type':'out_invoice',
                'invoice_line_ids':[(0,0,{
                'product_id': rec.id,
                'quantity': 1,
                'price_unit': self.amount,
                'tax_ids':None})],
                # 'payment_ids':[(4,self.id)]
                })
        new_record.action_post()
        # self.move_id = new_record.id
        
        return {
                'name': 'Create Invoice',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': new_record.id,
                'view_type': 'form',
                'view_id': self.env.ref('account.view_move_form').id,
                'view_mode':'form',
                'context': self._context,

                'target': 'current',
                }
    





    # def test(self):
    #    payment = self.env['account.payment'].browse(self.id)
    #    invoice_values = {
    #         'partner_id': payment.partner_id.id,
    #         'invoice_date': fields.Date.today(),  # Use today's date for the invoice
    #         'amount':self.amount,
           
    #     }
    #    self.env['account.move'].create(invoice_values)
    #    draft_entry = self.env['account.move'].browse(self.id)

    #     # Define values for the invoice
    #    invoice_values = {
    #         'partner_id': draft_entry.partner_id.id,
    #         'type': 'out_invoice',  # or 'in_invoice' for supplier invoices
    #         'invoice_date': fields.Date.today(),  # Use today's date for the invoice
    #         # Add more fields as needed
    #     }
    #    new_invoice = self.env['account.move'].create(invoice_values)
    #    for line in draft_entry.line_ids:
    #         invoice_line_values = {
    #             'move_id': new_invoice.id,
    #             'product_id': 55,
    #             'quantity': 1,
    #             'price_unit': self.amount,
    #             'name': line.name,
    #             # Add more fields as needed
    #         }
    #         self.env['account.move.line'].create(invoice_line_values)
        
    #    return new_invoice.id

    
    