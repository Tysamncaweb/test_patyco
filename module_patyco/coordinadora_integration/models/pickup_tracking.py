# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,Warning
import xmltodict
from .functions import _conexion,_print_documents,data_general,validate_number_guide

class PickupTracking(models.Model):
    _name = 'coordinadora.pickup.tracking'
    _description = "Seguimientos de Recogidas"

    name = fields.Char()
    date = fields.Date('Fecha')
    state = fields.Selection([('draft', 'Borrador'), ('generate', 'Consulta Realizada')], default='draft')
    user_id = fields.Many2one('res.users', 'Usuario')
    user_name = fields.Char('Nombre de Usuario')
    id_recogida = fields.Char('Id de la recogida')
    div_cliente = fields.Integer(size=2)

    @api.model
    def name_get(self):
        res = []
        for number in self:
            if self.number_guia:
                res.append((number.id, 'ID %s' % (number.number_guia)))
            else:
                res.append((number.id, 'ID '))
        return res

    @api.onchange('id_recogida')
    def _onchange_number_guia(self):
        if self.number_guia:
            self.number_guia = validate_number_guide(self,self.number_guia)

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise Warning('No se puede eliminar registros que están en el estado Etiqueta Generada')
            else:
                return super(PickupTracking, order).unlink()
        return

    @api.model
    def write(self, values):
        if values.get('id_recogida'):
            values['id_recogida'] = validate_number_guide(self, values.get('id_recogida'))
            self.validate_exitencia(values.get('id_recogida'))
        res = super(PickupTracking, self).write(values)
        return res

    @api.model
    def create(self, values):
        values['id_recogida'] = validate_number_guide(self,values.get('id_recogida'))
        data_general(self,values)
        res = super(PickupTracking, self).create(values)
        return res

    @api.multi
    def generate_etiqueta(self):
        id_rotulo = '55'

        bus = self.env['coordinadora.settings'].search([('id', '!=', 0)])
        if not bus:
            raise UserError(
                'No se pudo Generar la Etiqueta debido a que no se a realizado la configuración del usuario de Coordinadora')
        bus = bus[-1]

        var = [
            id_rotulo,
            self.number_guia,
            bus.user,
            bus.password_sha256,
        ]
        url = "http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php"
        payload =   "<Envelope xmlns=\"http://schemas.xmlsoap.org/soap/envelope/\">\n" \
                    "<Body>\n" \
                        "<Guias_imprimirRotulos xmlns=\"http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php\">\n" \
                            "<p xsi:type=\"ser:Agw_reimprimirRotulosIn\">\n\t" \
                                "<id_rotulo xsi:type=\"xsd:string\">%s</id_rotulo>\n\t" \
                                "<codigos_remisiones sxsi:type=\"xsd:soapenc:Array\">\n\t\t" \
                                    "<item>%s</item>\n\t" \
                                "</codigos_remisiones>\n\t" \
                                "<usuario xsi:type=\"xsd:string\">%s</usuario>\n\t" \
                                "<clave  xsi:type=\"xsd:string\">%s</clave>\n" \
                            "</p>\n" \
                        "</Guias_imprimirRotulos>\n" \
                    "</Body>\n</Envelope>\n" % (var[0], var[1], var[2], var[3])

        response = _conexion(self, payload,url)

        if response.status_code == 200:
            my_dict = xmltodict.parse(response.text)
            data = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:Guias_imprimirRotulosResponse']['return']
            if data['error']['#text'] == 'false':
                self.write({
                    'state': 'generate',
                    'code_pdf': data['rotulos']['#text'],
                })
            else:
                error = data['errorMessage']['#text']
                raise UserError('%s' % (error))

        elif response.status_code == 500:
            my_dict = xmltodict.parse(response.text)
            error = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            raise UserError('%s' % (error))

    @api.multi
    def save_to_file(self):
        name_report = 'Etiqueta_de_la_Guía_N°_%s.pdf' % (self.number_guia)
        res = _print_documents(self,name_report,self.code_pdf)
        return res