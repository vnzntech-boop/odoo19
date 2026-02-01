from odoo import api,models,fields,_
import datetime


class ProductProduct(models.Model):
    _inherit="product.product"
    
    
    
    expiry_date = fields.Date(string = "Expiry Date")
    
    is_supplement =fields.Boolean(string="Supplement")
    is_food   = fields.Boolean(string="Food")
    
    
    time = fields.Selection([('morning','Morning'),('afternoon','Afternoon'),('evening','Evening'),('night','Night')])
    area_of_focus = fields.Selection([('normal','Normal'),('body_building','Body Building'),('calisthetics','Calisthetics'),('yoga','Yoga'),('zoomba','Zoomba')],string="Area of Focus")
    recipe = fields.Text(string="Recipe")
    ingredients = fields.Text(string="Ingredients")
    calorie = fields.Float(string = "Calories/100gm")
    protein = fields.Float(string = "Protein/100gm")
    carbs = fields.Float(string = "Carbohydrate/100gm")

    def name_get(self):
        result = []
        for record in self:
            if record.is_food == True:
                name = "{} - {} - {}".format(record.name, record.time,record.area_of_focus)  
                result.append((record.id, name))
            else:
                name = "{}".format(record.name)  
                result.append((record.id, name))

        return result


    def expired_products(self):
        record = self.env['product.product'].search([('is_food','=',False),('expiry_date','!=',None)])
        today = datetime.date.today()
        for rec in record:
            if rec.expiry_date:
                if today < rec.expiry_date:
                    rec.unlink()
   
    
