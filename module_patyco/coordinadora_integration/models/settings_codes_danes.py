from odoo import models, fields, api
from odoo.exceptions import UserError,Warning,ValidationError

class SettingsCodesDanes(models.Model):
    _name = "coordinadora.settings.codes.danes"

    code_dane = fields.Char('Codigo Dane')
    name = fields.Char('Nombre')
    department_id = fields.Many2one('coordinadora.settings.department', 'Departamentos')
    states = fields.Selection([('not_available', 'No disponible'), ('available', 'disponible')])


    @api.onchange('code_dane')
    def onchage_code_dane(self):
        if self.code_dane:
            if not self.code_dane.isdigit():
                raise UserError(('Introduzca solo números en el campo Codigo Dane'))

    @api.model
    def create(self, values):
        res = super(SettingsCodesDanes, self).create(values)
        return res

    #@api.model
    #def name_get(self):
     #   res = []
      #  for number in self:
       #     res.append((number.id, '%s'%(number.name)))
        #return res


