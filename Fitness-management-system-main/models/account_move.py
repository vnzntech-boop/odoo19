from odoo import fields,api,models,_

class AccountMove(models.Model):
    _inherit = 'account.move'


    amount = fields.Integer(string = "Amount")
