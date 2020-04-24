# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,Warning,ValidationError
import xmltodict
from ..models import functions

class PrintGuideWizard(models.TransientModel):
    _name = "coordinadora.print.guide.wizard"

    name = fields.Char('Nombre')
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    number_guia = fields.Char('Número de Guía')

    @api.multi
    def print_guide(self):
        bus = self.env['coordinadora.settings'].search([('id', '!=', 0)])
        if not bus:
            raise UserError(
                'No se pudo Imprimir la Guía debido a que no se a realizado la configuración del usuario de Coordinadora')
        bus = bus[-1]
        var = [
            self.number_guia,
            bus.user,
            bus.password_sha256,
        ]
        url = "http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php"
        payload = "<Envelope xmlns=\"http://schemas.xmlsoap.org/soap/envelope/\">\n" \
                      "<Body>\n" \
                        "<Guias_reimprimirGuia xmlns=\"http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php\">\n" \
                            "<p xsi:type=\"ser:Agw_typeReimprimirGuiaIn\">\n\t" \
                                "<codigo_remision sxsi:type=\"xsd:string\">%s</codigo_remision>\n\t" \
                                "<usuario xsi:type=\"xsd:string\">%s</usuario>\n\t" \
                                "<clave xsi:type=\"xsd:string\">%s</clave>\n" \
                            "</p>\n" \
                        "</Guias_reimprimirGuia>\n" \
                      "</Body>\n" \
                  "</Envelope>" % (var[0], var[1], var[2])

        response = functions._conexion(self, payload,url)

        if response.status_code == 200:
            my_dict = xmltodict.parse(response.text)
            data = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:Guias_reimprimirGuiaResponse']['return']
            code_pdf = data['pdf']['#text']

            if len(code_pdf) > 1000:
                name_report = 'Guia_N°_%s.pdf' % (self.number_guia)
                res = functions._print_documents(self, name_report, code_pdf)
                return res
            else:
                raise UserError(
                    'El número de Guía no existe, por favor ingrese uno valido')

        elif response.status_code == 500:
            my_dict = xmltodict.parse(response.text)
            error = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            raise UserError('%s' % (error))

