from odoo import fields,api,models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    is_trainer = fields.Boolean(string="Is a Trainer")
    is_manager = fields.Boolean(string="Is a Manager")
    hr_empoyee_id = fields.Many2one('hr.employee','Manger')
    gender = fields.Selection([('male','Male'),('female','Female')])
    number_of_clients = fields.Integer(string="Number of clients")


    def action_open_clients(self):       
        return{
            'type': 'ir.actions.act_window',
            'name': 'Clients',
            'res_model': 'diet.model',
            'view_mode':'tree,form',
            'domain': [('assigned_trainer_id', '=', self.name)],
            'target': 'current',
            }
    
    @api.onchange('is_manager')
    def job_position(self):
        for rec in self:
            if rec.is_manager == True:
                rec.job_id = 9
    
    def name_get(self):
        result = []
        for record in self:
            name = "{}".format(record.name)  # Customize as needed
            result.append((record.id, name))
        return result
    
    @api.model
    def create(self,vals):

        res=super(HrEmployee,self).create(vals)
        return res