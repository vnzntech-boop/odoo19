from odoo import fields,models,api,_

class Floors(models.Model):
    _name = 'floor.model'
    _description  = " model for floor "

    floor_number = fields.Char(string = "Floor number")
    area_of_focus = fields.Selection([('normal','Normal'),('body_building','Body Building'),('calisthetics','Calisthetics'),('yoga','Yoga'),('zoomba','Zoomba')],string="Area of Focus")
    capacity = fields.Integer(string="Capacity")


    def name_get(self):
            result = []
            for record in self:
                name = "{}/{}".format(record.floor_number, record.area_of_focus)  
                result.append((record.id, name))
            return result