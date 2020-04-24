from odoo import models, fields, api
from odoo.exceptions import UserError,Warning
import hashlib

class SettingsCoordinadoraRes(models.Model):
    _name = "coordinadora.settings"

    user = fields.Char('Usuario',config_parameter='coordinadora_integration.user')
    password = fields.Char('Clave',config_parameter='coordinadora_integration.password')
    password_sha256 = fields.Char(config_parameter='coordinadora_integration.password_sha256')


    id_cliente = fields.Char('Id del Usuario',config_parameter='coordinadora_integration.id_cliente')
    nit_cliente = fields.Char('Nit del Usuario', config_parameter='coordinadora_integration.nit_cliente')
    apikey = fields.Char('ApiKey',config_parameter='coordinadora_integration.apikey')
    password_apikey = fields.Char('Clave ApiKey', config_parameter='coordinadora_integration.password_apikey')

    @api.model
    def name_get(self):
        res = []
        for number in self:
            res.append((number.id, 'Configuración de Usuario'))
        return res

    @api.onchange('id_cliente')
    def onchage_id_cliente(self):
        if self.id_cliente:
            if not self.id_cliente.isdigit():
                raise UserError(('Introduzca solo números en el campo Id de Usuario'))

    @api.model
    def create(self,values):
        if values.get('password'):
            values['password_sha256'] = hashlib.sha256(values.get('password').encode()).hexdigest()
        res = super(SettingsCoordinadoraRes, self).create(values)
        return res

    @api.onchange('password')
    def onchange_password(self):
        if self.password:
            self.password_sha256 = hashlib.sha256(self.password.encode()).hexdigest()

    @api.onchange('user','password','id_cliente','apikey','password_sah256')
    def _onchange_user(self):
        var = self.env['coordinadora.settings'].search([('id', '!=', 0)])
        if var:
            if not self.user:
                self.user = var[-1].user
            if not self.password:
                self.password = var[-1].password
            if not self.password_sha256:
                self.password_sha256 = var[-1].password_sha256
            if not self.id_cliente:
                self.id_cliente = var[-1].id_cliente
            if not self.nit_cliente:
                self.nit_cliente = var[-1].nit_cliente
            if not self.apikey:
                self.apikey = var[-1].apikey
            if not self.password_apikey:
                self.password_apikey = var[-1].password_apikey

