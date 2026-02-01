from odoo import api,fields,models,_
from _datetime import datetime,date
import re
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit= "res.partner"
    
    
    is_client = fields.Boolean(string="Client",default=True)
    name = fields.Char(string="Client Name")
    serial_number = fields.Char(string = "Serial Number")
    age = fields.Integer(string = "Age",compute = '_calc_age')
    height = fields.Integer(string="Height",default = 150)
    weight = fields.Integer(string="Weight",default = 55)
    gender = fields.Selection([('male','Male'),('female','Female')],string="Gender")
    dob = fields.Date(string="Date of birth")
    area_of_focus = fields.Selection([('normal','Normal'),('body_building','Body Building'),('calisthetics','Calisthetics'),('yoga','Yoga'),('zoomba','Zoomba')],string="Area of Focus")
    trainer_requirement = fields.Selection([('male','Male Trainers'),('female','Female Trainers')],string="Trainer Requirements")
    current_stage = fields.Selection([('beginer','Beginer'),('intermediate','Intermediate'),('advanced','Advanced')],string="Current Stage")
    membership = fields.Integer(string="Membership")
    joining_date = fields.Date(string = 'Joining Date',default=fields.Date.today)
    validity = fields.Char(string="Validity")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('expired','Expired'),('cancelled','Cancelled')],default='draft')
    expiry_in_months = fields.Integer(string="Expiry in months")
    cancel_reason = fields.Text(string="Cancel Reason")
    caution_paid = fields.Boolean(string="Caution paid/not")
    
    @api.depends('dob')
    def _calc_age(self):
        for record in self:
            if record.dob:
                dob_year=record.dob.year
                current_year=datetime.now().year
                record.age=current_year-dob_year
            else:
                record.age=0

    def renew(self):
        for rec in self:
            rec.state = 'confirm'
            rec.membership = 0
            rec.expiry_in_months = 0
            rec.cancel_reason = ''
            rec.validity = None

    # schedular
    def inform_expiry(self):
        for rec in self:
            rec.expiry_in_months  = rec.expiry_in_months - 1
            if rec.expiry_in_months == 1 :
                template_id = self.env.ref('fitness_management_system.email_template_inform_expiry')
                if template_id:
                    template_id.send_mail(self.id)

            elif rec.expiry_in_months == 0:
                rec.state = 'expired'
                template_id = self.env.ref('fitness_management_system.email_template_inform_expiry')
                if template_id:
                    template_id.send_mail(self.id)
        

    @api.model
    def create(self,vals):
        vals['serial_number'] = self.env['ir.sequence'].next_by_code('partner.code')
        active_model = self.env.context.get('active_model')

        template_id = self.env.ref('fitness_management_system.email_template_for_inform_registration')
        if active_model and active_model == 'res.partner':
            if template_id:
                template_id.send_mail(self.id)
                vals['expiry_in_months'] = vals.get('membership')
                number = vals.get('membership')
                date_str = str(vals.get('joining_date'))
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                formatted_date = date_obj.strftime('%Y/%m/%d')
                formatted_date = date_obj.strftime('%Y-%m-%d')
                formatted_date = str(formatted_date)
                input_date = datetime.strptime(formatted_date, '%Y-%m-%d')
                calculated_date = input_date + relativedelta(months=number)
                calculated_date = str(calculated_date)
                calculated_date = calculated_date[:-9]
                vals['validity'] = calculated_date
        


        res=super(ResPartner,self).create(vals)

                
        return res
    
    def caution_payment(self):
        records = self.env['account.payment'].search([('partner_id.id', '=', self.id)]) 
        if not records:
            new_record = self.env['account.payment'].create({
                'partner_id': self.id,
                'state':'draft',
                'caution_deposit':2000,
                'amount':2000})
            return new_record
        else:
            result ={
            'type': 'ir.actions.act_window',
            'name': 'Caution Deposit',
            'res_model': 'account.payment',
            'view_mode':'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'target': 'current',
            }
            return result
        
        
    

    @api.constrains('dob')
    def check_dob(self):
        for rec in self:
            today=date.today()
            if(rec.dob and rec.dob>=today):
                raise ValidationError(_("Invalid Date of Birth"))
    
    @api.constrains('age')
    def age_limit(self):
        for rec in self:
            if rec.age < 15:
                raise ValidationError(_("Age must be greater than 15"))
            
    @api.constrains('phone')
    def check_phone(self):
        for rec in self:
            if(rec.phone):
                if(len(rec.phone)>10 or len(rec.phone)<10):
                    raise ValidationError(_("Phone number must be ten digits"))
            
        
    @api.constrains('mobile')
    def check_alt_phone(self):
        for rec in self:
            if(rec.mobile):
                if(len(rec.mobile)>10 or len(rec.mobile)<10):
                    raise ValidationError(_("Mobile number must be ten digits"))
                        
    @api.constrains('email')
    def _check_valid_email(self):
        for record in self:     
            if(record.email):       
                if not re.match(r"[^@]+@[^@]+\.[^@]+", record.email):
                    raise ValidationError(_('Invalid email address.'))  
                


    @api.constrains('phone', 'mobile')
    def _check_phone_mobile_unique(self):
        for partner in self:
            if partner.phone and partner.mobile and partner.phone == partner.mobile:
                raise ValidationError("Phone and Mobile cannot have the same value.")
    

    @api.constrains('height','weight')
    def _check_informations(self):
        for record in self:     
            if(record.height and record.weight):
                if record.height <= 0 or record.weight <= 0 :
                    raise ValidationError(_("Height or Weight can't be Zero"))
                

    def action_open_payments(self):
        records = self.env['account.payment'].search([('partner_id.id', '=', self.id)]) 
        result={
                'type': 'ir.actions.act_window',
                'name': 'Payments',
                'res_model': 'account.payment',
                'view_mode':'tree,form',
                'offers':None,
                'domain': [('partner_id', '=', self.id)],
                'target': 'current',}
        if records:
            return result
        elif (not records and self.membership >0):
            payment_record = self.env['account.payment'].create({
            'partner_id': self.id,
            'state':'draft',
            'base_fee':500,
            'caution_deposit':2000,})
            return payment_record,result
        return result
        
    
    def action_open_diet_and_workout(self):
        result ={
            'type': 'ir.actions.act_window',
            'name': 'Diet and Workout',
            'res_model': 'diet.model',
            'view_mode':'tree,form',
            'domain': [('client_id', '=', self.id)],
            'target': 'current',
            }
        return result
        

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Error: User Name Already In Use!'),
    ]

            
            
    
    
    
