# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError,Warning
import time
import re

from zeep import Client

class GenerateGuideInter(models.Model):
    _name = 'generate.guide.inter'
    _description = "History Salary Increase"


    name = fields.Char()
    date = fields.Date('Fecha')
    state = fields.Selection([('draft','Borrador'),('generate','Generar',)],default='draft')
    user_id = fields.Many2one('res.users', 'Usuario')
    user_name = fields.Char('Nombre de Usuario')
    number_guia = fields.Char('Numero de Guía')

    #Origin Data
    full_name_o = fields.Char('Nombre Completo',size=30)
    ci_o = fields.Char('Cédula',size=8)
    email_o = fields.Char('Correo Electrónico',size=40)
    city_o = fields.Char('Ciudad',size=40)
    address_o = fields.Char('Dirección',size=80)
    telephone_o = fields.Char('Teléfono',size=20)

    #Destination Data
    full_name_d = fields.Char('Nombre Completo', size=30)
    ci_d = fields.Char('Cédula', size=8)
    email_d = fields.Char('Correo Electrónico', size=40)
    city_d = fields.Char('Ciudad', size=40)
    address_d = fields.Char('Dirección', size=80)
    telephone_d = fields.Char('Teléfono', size=20)

    #package information
    declared_value = fields.Float('Valor Declarado de Todo el envío',size=50)
    long = fields.Float('Largo (cm)',size=10)
    high = fields.Float('Alto (cm)',size=10)
    width = fields.Float('Ancho (cm)',size=10)
    unit_weight = fields.Float('Peso de la Unidad (Kg)',size=10)
    quantity = fields.Integer('Cantidad',size=10,default=1)

    pais = fields.Many2one('res.country', string='País')
    codigo_postal = fields.Integer('Código Postal', size=10)

    _defaults = {
        'state': 'draft',
    }

    @api.model
    def name_get(self):
        res = []
        for number in self:
            if self.number_guia:
                res.append((number.id, 'Guía: %s' % (number.number_guia)))
            else:
                res.append((number.id, 'Guía: '))

        return res

    @api.onchange('full_name_o','full_name_d')
    def _onchange_full_name(self):
        if self.full_name_o:
            self.full_name_o = self.validate_full_name(self.full_name_o)
        if self.full_name_d:
            self.full_name_d = self.validate_full_name(self.full_name_d)

    @api.onchange('ci_o', 'ci_d')
    def _onchange_ci(self):
        if self.ci_o:
            self.validate_ci(self.ci_o)
        if self.ci_d:
            self.validate_ci(self.ci_o)

    @api.onchange('email_o', 'email_d')
    def _onchange_email(self):
        if self.email_o:
           self.email_o = self.validate_email(self.email_o)
        if self.email_d:
            self.email_d = self.validate_email(self.email_d)


    @api.onchange('telephone_o', 'telephone_d')
    def _onchange_telephone(self):
        if self.telephone_o:
            self.validate_telephone(self.telephone_o)
        if self.telephone_d:
            self.validate_telephone(self.telephone_d)

    @api.multi
    def obtener_fecha(self, values):
        if values:
            values['date'] = time.strftime('%Y-%m-%d')
            context = self._context
            current_uid = context.get('uid')
            var = self.env['res.users'].browse(current_uid)
            values['user_id'] = current_uid
            values['user_name'] = var.display_name
            values['var'] = values.get('numero')
            return

    @api.model
    def create(self, values):
        # Full_name
        values['full_name_o'] = self.validate_full_name(values.get('full_name_o',False))
        values['full_name_d'] = self.validate_full_name(values.get('full_name_d',False))
        # CI
        self.validate_ci(values['ci_o'])
        self.validate_ci(values['ci_d'])
        # Email
        values['email_o'] = self.validate_email(values.get('email_o', False))
        values['email_d'] = self.validate_email(values.get('email_d', False))
        # Telephone
        self.validate_telephone(values.get('telephone_o', False))
        self.validate_telephone(values.get('telephone_d', False))
        # Declared value of the entire shipment
        if values.get('declared_value') == 0.00:
            raise UserError('El campo valor declarado de todo el envío, no puede ser cero')
        # Long
        if values.get('long') == 0.00:
            raise UserError('El campo Longuitud, no puede ser cero')
        # High
        if values.get('high') == 0.00:
            raise UserError('El campo Altura, no puede ser cero')
        # Width
        if values.get('width') == 0.00:
            raise UserError('El campo Ancho, no puede ser cero')
        # Unit_weight
        if values.get('unit_weight') == 0.00:
            raise UserError('El campo Peso de la Unidad (Kg), no puede ser cero')
        # Quantity
        if values.get('quantity') == 0:
            raise UserError('El campo Cantidad, no puede ser cero')

        self.obtener_fecha(values)
        res = super(GenerateGuideInter, self).create(values)
        return res

    @api.multi
    def write(self, values):
        # Validación previa a guardar
        # Full_name
        if values.get('full_name_o'):
            values['full_name_o'] = self.validate_full_name(values.get('full_name_o', False))
        if values.get('full_name_d'):
            values['full_name_d'] = self.validate_full_name(values.get('full_name_d', False))
        # CI
        if values.get('ci_o'):
            self.validate_ci(values.get('ci_o',False))
        if values.get('ci_d'):
            self.validate_ci(values['ci_d'])
        # Email
        if values.get('email_o'):
            values['email_o'] = self.validate_email(values.get('email_o', False))
        if values.get('email_d'):
            values['email_d'] = self.validate_email(values.get('email_o', False))
        # Telephone
        if values.get('telephone_o'):
            self.validate_telephone(values.get('telephone_o', False))
        if values.get('telephone_d'):
            self.validate_telephone(values.get('telephone_d', False))
        # Declared value of the entire shipment
        if values.get('declared_value'):
            if values.get('declared_value', False) == 0.00:
                raise UserError('El campo valor declarado de todo el envío, no puede ser cero')
        # Long
        if values.get('long'):
            if values.get('long', False) == 0.00:
                raise UserError('El campo Longuitud, no puede ser cero')
        # High
        if values.get('high'):
            if values.get('high', False) == 0.00:
                raise UserError('El campo Altura, no puede ser cero')
        # Width
        if values.get('width'):
            if values.get('width', False) == 0.00:
                raise UserError('El campo Ancho, no puede ser cero')
        # Unit_weight
        if values.get('unit_weight'):
            if values.get('unit_weight', False) == 0.00:
                raise UserError('El campo Peso de la Unidad (Kg), no puede ser cero')
        # Quantity
        if values.get('quantity'):
            if values.get('quantity', False) == 0:
                raise UserError('El campo Cantidad, no puede ser cero')

        self.obtener_fecha(values)
        res = super(GenerateGuideInter, self).write(values)
        return res

    #Validaciones
    def validate_full_name(self,full_name):
        if full_name:
            val_name_o = full_name
            if (val_name_o.replace(" ", "")).isalpha():
                return full_name.title()
            else:
                raise UserError('Introduzca solo letras para el nombre completo')
        else:
            raise UserError('El campo "Nombre Completo" esta vacio')

    def validate_ci(self,ci):
        if ci:
            if ci.isdigit() :
                return True
            else:
                raise UserError('Introduzca solo número en la cedula')
        else:
            raise UserError('El campo "Cédula" esta vacio')

    def validate_email(self,email):
        exp_regular = r"[\w.%+-]+@[\w.-]+\.+[a-zA-Z]{2,3}"
        res = re.compile(exp_regular)
        res = res.match(email.lower())
        if res and len(email) == res.regs[0][1]:
            return email.lower()
        else:
            raise UserError('Introduzca un correo valido')

    def validate_telephone(self,telephone):
        if telephone:
            if telephone.isdigit():
                return True
            else:
                raise UserError('Introduzca solo número en el telefono')
        else:
            raise UserError('El campo "Teléfono" esta vacio')


    def _conexion(self):
        wsdl_url = "http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php?wsdl"
        soap_client = Client(wsdl_url)
        result = soap_client.getSet("xxx", "xxx", "494")


    @api.multi
    def generate_guide(self):
        self.write({
            'state':'generate',
            'number_guia': 89654372,
        })


