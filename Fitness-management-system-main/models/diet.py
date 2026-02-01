from odoo import api,fields,models,_
from odoo.exceptions import ValidationError
from _datetime import datetime,date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from builtins import str

class DietModel(models.Model):
    _name = 'diet.model'
    _description = "This model for list the diet details"
    
    _rec_name = "client_id"
    
    client_id = fields.Many2one("res.partner",'Client Name')
    phase = fields.Selection([('bulking','Bulking'),('cutting','Cutting'),('maintaining','Maintaining')])
    age = fields.Integer(string="Age",related = 'client_id.age')
    phone = fields.Char(string="Phone",related = 'client_id.phone')
    alt_phone = fields.Char(string="Alternate Phone",related = 'client_id.mobile')
    email = fields.Char(string="Email",related = 'client_id.email')
    height = fields.Integer(string="Height",related = 'client_id.height')
    weight = fields.Integer(string="Weight",related = 'client_id.weight')
    current_stage = fields.Selection(string='Current Stage',related ='client_id.current_stage' )
    activity_level = fields.Selection([('1.2','Sedentary (little or no exercise)'),('1.375','Lightly active (light exercise/sports 1-3 days/week)'),('1.55','Moderately active  (moderate exercise/sports 3-5 days/week)'),('1.725','Very active (hard exercise/sports 6-7 days a week)'),('1.9','Extremely active  (very hard exercise/sports & physical job or 2x training)')],string="Activity Level")
    calrie_intake = fields.Integer(string="Calorie Intake",compute = 'calculate_requirements')
    protein_intake = fields.Integer(string="Protein Intake",compute = 'calculate_requirements')
    carb_intake = fields.Integer(string="Carb Intake",compute = 'calculate_requirements')
    gender = fields.Selection(string = "Gender",related = "client_id.gender")

    assigned_trainer_id = fields.Many2one("hr.employee",'Assigned Trainer')

    date_field = fields.Date(string="Date field",default=fields.Date.today)
    area_of_focus = fields.Selection(string = "Area of focus",related = "client_id.area_of_focus")
    assigned_floor = fields.Many2one('floor.model','Assigned floor')
    
    cost_per_day = fields.Integer(string = "Cost per Day",compute = 'calculate_cost')
    number_of_clients = fields.Integer(string = "Number of customers handling")
    

    
    diet_line_ids = fields.One2many('diet.model.lines','diet_lines_id',string = 'Foods')
    workout_line_ids = fields.One2many('workout.model.lines','diet_id',string = 'Workouts')
    progress_line_ids = fields.One2many('progress.model.lines','diet_id',string = 'Progress')

        
    @api.model
    def create(self,vals):
        res = super(DietModel,self).create(vals)
        if res.assigned_trainer_id and res.client_id:
            if res.assigned_trainer_id.gender != res.client_id.gender:
                raise ValidationError(_("Gender miss match in Trainer and Client"))
        res.assigned_trainer_id.number_of_clients = res.assigned_trainer_id.number_of_clients + 1
        return res
    
    @api.onchange('area_of_focus')
    def filter_floor(self):
        records = self.env['floor.model'].search([('area_of_focus', '=', self.area_of_focus)]) 
        for rec in self:
            floors = self.env['floor.model'].search([('area_of_focus', '=', self.area_of_focus)])
            for floor in floors:
                return {'domain':{'assigned_floor':[('area_of_focus','=',self.area_of_focus)]}}
            
    

    

    
    
    @api.onchange('activity_level')
    def calculate_requirements(self):
        if self.phase == 'bulking':
            self.calrie_intake = ((88.362+(13.397*self.weight)+(4.799*self.height)-(5.677*self.age))*float(self.activity_level)) + 100
            self.protein_intake = (float(self.activity_level)*self.weight) + 15
            self.carb_intake = (self.calrie_intake/4) + 50
        elif self.phase == 'cutting':
            self.calrie_intake = ((88.362+(13.397*self.weight)+(4.799*self.height)-(5.677*self.age))*float(self.activity_level)) - 100
            self.protein_intake = (float(self.activity_level)*self.weight) - 15
            self.carb_intake = (self.calrie_intake/4) - 50
        else:
            self.calrie_intake = ((88.362+(13.397*self.weight)+(4.799*self.height)-(5.677*self.age))*float(self.activity_level))
            self.protein_intake = (float(self.activity_level)*self.weight)
            self.carb_intake = (self.calrie_intake/4)
  


    def send_mail(self):
        template_id = self.env.ref('fitness_management_system.email_template_for_trainers')
        if template_id:
                template_id.send_mail(self.id)
        sum_calorie = 0
        sum_protein = 0
        sum_carb = 0
        for rec in self.diet_line_ids:
           sum_calorie = sum_calorie+rec.calorie
           sum_protein = sum_protein+rec.protein
           sum_carb = sum_carb + rec.carbs
 
        if (self.calrie_intake > sum_calorie and self.protein_intake > sum_protein and self.carb_intake > sum_carb ) :
            raise ValidationError(_("Can't inform Client because, Created diet plan doesn't meet the requirements,"))
        else:
            template_id = self.env.ref('fitness_management_system.email_template_for_diet')
            if template_id:
                template_id.send_mail(self.id)
        
    
    _sql_constraints = [
        ('unique_fields', 'unique(client_id)', 'Error: Record already exist!'),
    ]

        
    # cron
    def update_client(self):
        template_id = self.env.ref('fitness_management_system.email_template_monthly_report')
        if template_id:
                template_id.send_mail(self.id)

    


    def unlink(self):
        for rec in self:
            rec.assigned_trainer_id.number_of_clients = rec.assigned_trainer_id.number_of_clients -1
            res = super(DietModel, self).unlink()
        
        return res
    



class DietModelLines(models.Model):
    _name = 'diet.model.lines'
    _description = 'diet lines'

    diet_lines_id = fields.Many2one('diet.model')

    food_id= fields.Many2one('product.product',string='Foods')
    time = fields.Char(string='Time')
    recipe  = fields.Text(string="Recipe")
    ingredients = fields.Text(string="Ingredients")
    calorie = fields.Float(string="Calorie")
    protein = fields.Float(string="Protein")
    carbs = fields.Float(string="Carbs")

    @api.onchange('food_id')
    def fields_change(self):
        self.calorie = self.food_id.calorie
        self.protein = self.food_id.protein
        self.carbs = self.food_id.carbs
        self.time = self.food_id.time
        self.recipe = self.food_id.recipe
        self.ingredients = self.food_id.ingredients
    
    

    @api.onchange('food_id')
    def filter_foods(self):
        records = self.env['res.partner'].search([('id', '=', self.diet_lines_id.client_id.id)]) 
        out = str(records.area_of_focus)
        for rec in self:
            foods = self.env['product.product'].search([])
            for food in foods:
                if food.area_of_focus != False:

                    return {'domain':{'food_id':[('area_of_focus','=',out)]}}

class workoutModelLines(models.Model):
    _name = 'workout.model.lines'
    _description = "workout model line"
    
    diet_id = fields.Many2one('diet.model')
    month = fields.Selection([('january','January'),('february','February'),('march','March'),('april','April'),('may','May'),
                              ('june','June'),('july','July'),('august','August'),('septemper','Septemper'),('october','October'),
                              ('november','November'),('december','December')])
    workout_id = fields.Many2one('workout.model',string="Workout")
    level = fields.Char(string="Level")
    warm_up = fields.Text(string="Warm Up")
    workouts = fields.Text(string="Workouts")
    post_workout  = fields.Text(string="Post Workouts")
    status = fields.Selection([('new','New'),('on_going','On Going'),('completed','Completed')])

    @api.onchange('workout_id')
    def update_vals(self):
        self.level = self.workout_id.level
        self.warm_up = self.workout_id.warm_up
        self.workouts = self.workout_id.workouts
        self.post_workout  = self.workout_id.post_workout
    

    
   
        
class ProgressTrackModel(models.Model):
    _name = 'progress.model.lines'
    _description="For track progress"
    
    diet_id = fields.Many2one('diet.model')
    
    month = fields.Selection([('january','January'),('february','February'),('march','March'),('april','April'),('may','May'),
                              ('june','June'),('july','July'),('august','August'),('septemper','Septemper'),('october','October'),
                              ('november','November'),('december','December')])
    
    height = fields.Char(string="Height")
    weight = fields.Char(string="Weight")
    bmi = fields.Integer(string="BMI",compute='add_bmi')



    @api.depends('height','weight')
    def add_bmi(self):
        self.bmi = False
        if int(self.height) and int(self.weight) !=0:
            height_in_meter =  int(self.height) /100
            bmi_of_client = int(self.weight)/height_in_meter
            self.bmi = bmi_of_client

    
    
