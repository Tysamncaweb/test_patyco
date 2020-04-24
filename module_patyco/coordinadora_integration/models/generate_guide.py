# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError,Warning
import time
import xmltodict
from .functions import validate_full_name,validate_ci,validate_email,validate_telephone,_conexion,_print_documents

class GenerateGuide(models.Model):
    _name = 'generate.guide'
    _description = "Permite generar una guía nacional en coordinadora"

    name = fields.Char()
    date = fields.Date('Fecha')
    state = fields.Selection([('draft','Borrador'),('generate','Generar')],default='draft')
    user_id = fields.Many2one('res.users', 'Usuario')
    user_name = fields.Char('Nombre de Usuario')
    number_guia = fields.Char('Numero de Guía')
    code_pdf = fields.Char()

    # fields for download xls
    state_report = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Archivo Preparado', filters='.pdf', readonly=True)
    name_report = fields.Char('File Name')

    #Origin Data
    full_name_o = fields.Char('Nombre Completo',size=30)
    ci_o = fields.Char('Cédula',size=8)
    email_o = fields.Char('Correo Electrónico',size=40)
    department_o = fields.Many2one('coordinadora.settings.department', 'Departamento')
    city_o = fields.Many2one('coordinadora.settings.codes.danes', 'Ciudad')
    address_o = fields.Char('Dirección',size=80)
    telephone_o = fields.Char('Teléfono',size=20)

    #Destination Data
    full_name_d = fields.Char('Nombre Completo', size=30)
    ci_d = fields.Char('Cédula', size=8)
    email_d = fields.Char('Correo Electrónico', size=40)
    department_d = fields.Many2one('coordinadora.settings.department', 'Departamento')
    city_d = fields.Many2one('coordinadora.settings.codes.danes', 'Ciudad')
    address_d = fields.Char('Dirección', size=80)
    telephone_d = fields.Char('Teléfono', size=20)

    #package information
    declared_value = fields.Float('Valor Declarado de Todo el envío',size=50)
    long = fields.Float('Largo (cm)',size=10)
    high = fields.Float('Alto (cm)',size=10)
    width = fields.Float('Ancho (cm)',size=10)
    unit_weight = fields.Float('Peso de la Unidad (Kg)',size=10)
    quantity = fields.Integer('Cantidad',size=10,default=1)

    #data aditional
    content = fields.Char('Contenido del paquete')
    observations = fields.Char('Observaciones')
    state_pack = fields.Selection([('IMPRESO', '')], default="IMPRESO")
    id_remitente = fields.Integer(default=0)

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
            self.full_name_o = validate_full_name(self,self.full_name_o)
        if self.full_name_d:
            self.full_name_d = validate_full_name(self,self.full_name_d)

    @api.onchange('ci_o', 'ci_d')
    def _onchange_ci(self):
        if self.ci_o:
            validate_ci(self,self.ci_o)
        if self.ci_d:
            validate_ci(self,self.ci_o)

    @api.onchange('email_o', 'email_d')
    def _onchange_email(self):
        if self.email_o:
           self.email_o = validate_email(self,self.email_o)
        if self.email_d:
            self.email_d = validate_email(self,self.email_d)

    @api.onchange('telephone_o', 'telephone_d')
    def _onchange_telephone(self):
        if self.telephone_o:
            validate_telephone(self,self.telephone_o)
        if self.telephone_d:
            validate_telephone(self,self.telephone_d)

    @api.onchange('department_o')
    def _onchange_department(self):
        self.city_o = False

    @api.onchange('department_d')
    def _onchange_department(self):
        self.city_d = False

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
        values['full_name_o'] = validate_full_name(self,values.get('full_name_o',False))
        values['full_name_d'] = validate_full_name(self,values.get('full_name_d',False))
        # CI
        validate_ci(self,values['ci_o'])
        validate_ci(self,values['ci_d'])
        # Email
        if self.email_d or self.email_o:
            values['email_o'] = validate_email(self,values.get('email_o', False))
            values['email_d'] = validate_email(self,values.get('email_d', False))
        # Telephone
        validate_telephone(self,values.get('telephone_o', False))
        validate_telephone(self,values.get('telephone_d', False))
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
        res = super(GenerateGuide, self).create(values)
        return res

    @api.multi
    def write(self, values):
        # Validación previa a guardar
        # Full_name
        if values.get('full_name_o'):
            values['full_name_o'] = validate_full_name(self,values.get('full_name_o', False))
        if values.get('full_name_d'):
            values['full_name_d'] = validate_full_name(self,values.get('full_name_d', False))
        # CI
        if values.get('ci_o'):
            validate_ci(self,values.get('ci_o',False))
        if values.get('ci_d'):
            validate_ci(self,values['ci_d'])
        # Email
        if values.get('email_o'):
            values['email_o'] = validate_email(self,values.get('email_o', False))
        if values.get('email_d'):
            values['email_d'] = validate_email(self,values.get('email_o', False))
        # Telephone
        if values.get('telephone_o'):
            validate_telephone(self,values.get('telephone_o', False))
        if values.get('telephone_d'):
            validate_telephone(self,values.get('telephone_d', False))
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
        res = super(GenerateGuide, self).write(values)
        return res

    @api.multi
    def generate_guide(self):

        bus = self.env['coordinadora.settings'].search([('id','!=',0)])
        if not bus:
            raise UserError('No se pudo Generar la Guía debido a que no se a realizado la configuración del usuario de Coordinadora')
        bus = bus[-1]
        var = [
                bus.id_cliente,
                self.id_remitente,

                self.ci_o,
                self.full_name_o,
                self.address_o,
                self.telephone_o,
                self.city_o.code_dane,

                self.ci_d,
                self.full_name_d,
                self.address_d,
                self.telephone_d,
                self.city_d.code_dane,

                self.declared_value,
                self.content,

                self.high,
                self.width,
                self.long,
                self.unit_weight,
                self.quantity,

                self.observations,
                self.state_pack,
                bus.user,
                bus.password_sha256,
            ]

        url = "http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php"
        payload = "<Envelope xmlns=\"http://schemas.xmlsoap.org/soap/envelope/\">\n" \
                        "<Body>\n" \
                            "<Guias_generarGuia xmlns=\"http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php\">\n" \
                                "<p>\n \t" \
                                    "<id_cliente xsi:type=\"xsd:int\">%s</id_cliente>\n \t" \
                                    "<id_remitente xsi:type=\"xsd:int\">%s</id_remitente>\n \t" \
                                    "<nit_remitente xsi:type=\"xsd:string\">%s</nit_remitente>\n\t\t" \
                                    "<nombre_remitente xsi:type=\"xsd:string\">%s</nombre_remitente>\n\t\t" \
                                    "<direccion_remitente xsi:type=\"xsd:string\">%s</direccion_remitente>\n\t\t" \
                                    "<telefono_remitente xsi:type=\"xsd:string\">%s</telefono_remitente>\n\t\t" \
                                    "<ciudad_remitente xsi:type=\"xsd:string\">%s</ciudad_remitente>\n \n\t\t" \
                                    "<nit_destinatario xsi:type=\"xsd:string\">%s</nit_destinatario>\n\t\t" \
                                    "<nombre_destinatario xsi:type=\"xsd:string\">%s</nombre_destinatario>\n\t\t" \
                                    "<direccion_destinatario xsi:type=\"xsd:string\">%s</direccion_destinatario>\n\t\t" \
                                    "<telefono_destinatario xsi:type=\"xsd:string\">%s</telefono_destinatario>\n\t\t" \
                                    "<ciudad_destinatario xsi:type=\"xsd:string\">%s</ciudad_destinatario>\n\t\t\n\t\t" \
                                    "<valor_declarado xsi:type=\"xsd:float\">%s</valor_declarado>\n\t\t" \
                                    "<contenido xsi:type=\"xsd:string\">%s</contenido>\n\t\t" \
                                    "<detalle xsi:type=\"ser:ArrayOfAgw_typeGuiaDetalle\" soapenc:arrayType=\"ser:Agw_typeGuiaDetalle[]\">\n\t\t\t" \
                                        "<item>\n\t\t\t" \
                                            "<ubl xsi:type=\"xsd:int\">0</ubl>\n\t\t\t" \
                                            "<alto xsi:type=\"xsd:float\">%s</alto>\n\t\t\t" \
                                            "<ancho xsi:type=\"xsd:float\">%s</ancho>\n\t\t\t" \
                                            "<largo xsi:type=\"xsd:float\">%s</largo>\n\t\t\t" \
                                            "<peso xsi:type=\"xsd:float\">%s</peso>\n\t\t\t" \
                                            "<unidades xsi:type=\"xsd:int\">%s</unidades>\n\t\t\t" \
                                            "<referencia xsi:type=\"xsd:string\"></referencia>\n\t\t\t" \
                                            "<nombre_empaque xsi:type=\"xsd:string\"></nombre_empaque>\n\t\t\t" \
                                        "</item>\n\t\t" \
                                    "</detalle>\n\t" \
                                    "<observaciones xsi:type=\"xsd:string\">%s</observaciones>\n \t" \
                                    "<estado xsi:type=\"xsd:string\">%s</estado>\n\t\t\t\t" \
                                    "<usuario xsi:type=\"xsd:string\">%s</usuario>\n\t\t\t\t" \
                                    "<clave xsi:type=\"xsd:string\">%s</clave>\n" \
                                "</p>\n" \
                            "</Guias_generarGuia>\n" \
                        "</Body>\n" \
                  "</Envelope>\n" %(var[0],var[1],var[2],var[3],var[4],var[5],var[6],var[7],var[8],var[9],var[10],var[11],var[12],var[13],var[14],var[15],var[16],var[17],
                                    var[18],var[19],var[20],var[21],var[22])

        response = _conexion(self,payload,url)

        if response.status_code == 200:
            my_dict = xmltodict.parse(response.text)
            data = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:Guias_generarGuiaResponse']['return']
            self.write({
                'state': 'generate',
                'number_guia': data['codigo_remision']['#text'],
                'code_pdf': data['pdf_guia']['#text'],
            })

        elif response.status_code == 500:
            my_dict = xmltodict.parse(response.text)
            error = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            raise UserError('%s' %(error))

    @api.multi
    def save_to_file(self):
        name_report = 'Guia_Nacional_%s.pdf' % (self.number_guia)
        res = _print_documents(self,name_report,self.code_pdf)
        return res


