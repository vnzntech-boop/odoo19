from odoo import fields,models,api,_

class WorkoutModel(models.Model):
    _name = 'workout.model'
    _description = "Model for create workout"
    
    
    serial_number =fields.Char(string = "Serial Number")
    level = fields.Selection([('beginer','Beginer'),('inermediate','Intermediate'),('advanced','Advanced')])
    warm_up = fields.Text(string="Warm UP")
    workouts = fields.Text(string="Workouts")
    post_workout = fields.Text(string="Stretching")



    def name_get(self):
        result = []
        for record in self:
            name = "{} - {} ".format(record.serial_number, record.level)  
            result.append((record.id, name))
        return result
    
