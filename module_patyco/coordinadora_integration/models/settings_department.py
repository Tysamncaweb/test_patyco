from odoo import models, fields, api
import time

class SettingsDepartment(models.Model):
    _name = "coordinadora.settings.department"

    name = fields.Char('Departamento')

    #@api.model
    #def name_get(self):
     #   res = []
      #  for number in self:
       #     res.append((number.id, '%s'% (number.name)))
        #return res
