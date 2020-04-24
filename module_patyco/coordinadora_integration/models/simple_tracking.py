# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError,Warning
import xmltodict
from datetime import datetime
from .functions import _conexion,_print_documents,data_general,validate_number_guide

class RastreoFormaSimple(models.Model):
    _name = 'coordinadora.simple.tracking'
    _description = "Se realiza el rastreo de forma simple"

    name = fields.Char()
    date = fields.Date('Fecha')
    state = fields.Selection([('draft', 'Borrador'), ('generate', 'Rastreo Realizado')], default='draft')
    user_id = fields.Many2one('res.users', 'Usuario')
    user_name = fields.Char('Nombre de Usuario')
    number_guia = fields.Char('Número de Guía')

    descripcion_estado = fields.Char('Estado de la guía')
    fecha_entrega = fields.Char('Fecha de entrega')
    hora_entrega = fields.Char('Hora de entrega')

    descripcion_novedad = fields.Char('Descripción de Novedad Presentada')
    fecha_novedad = fields.Char('Fecha de la novedad')
    hora_novedad = fields.Char('Hora de la novedad')

    city_origen = fields.Char('Ciudad de origen')
    city_destino = fields.Char('Ciudad de destino')

    dia_promesa_servicio = fields.Char('Cantidad de días pautados para la entrega')


    @api.model
    def name_get(self):
        res = []
        for number in self:
            if self.number_guia and self.state != 'draft':
                res.append((number.id, 'Rastreo simple de la Guía N° %s' % (number.number_guia)))
        return res

    @api.onchange('number_guia')
    def _onchange_number_guia(self):
        if self.number_guia:
            self.number_guia = validate_number_guide(self,self.number_guia)

    @api.multi
    def unlink(self):
        for order in self:
            if order.state not in ('draft'):
                raise Warning('No se puede eliminar registros que están en el estado Etiqueta Generada')
            else:
                return super(RastreoFormaSimple, order).unlink()
        return

    @api.model
    def write(self, values):
        if values.get('number_guia'):
            values['number_guia'] = validate_number_guide(self, values.get('number_guia'))
        #data_general(self,values)
        res = super(RastreoFormaSimple, self).write(values)
        return res

    @api.model
    def create(self, values):
        values['number_guia'] = validate_number_guide(self,values.get('number_guia'))
        data_general(self,values)
        res = super(RastreoFormaSimple, self).create(values)
        return res

    @api.multi
    def generate_rastreo_simple(self):
        bus = self.env['coordinadora.settings'].search([('id', '!=', 0)])
        if not bus:
            raise UserError(
                'No se pudo realizar el Rastreo simple debido a que no se a realizado la configuración del usuario de Coordinadora')
        bus = bus[-1]

        var = [
            self.number_guia,
            bus.nit_cliente,
            bus.apikey,
            bus.password_apikey,
        ]
        url = "http://sandbox.coordinadora.com/ags/1.5/server.php"
        payload = "<Envelope xmlns=\"http://schemas.xmlsoap.org/soap/envelope/\">\n" \
                    "<Body>\n" \
                        "<Seguimiento_simple xmlns=\"http://sandbox.coordinadora.com/ags/1.5/server.php\">\n" \
                            "<p xsi:type=\"ser:Seguimiento_simpleIn\">\n\t" \
                                "<codigo_remision sxsi:type=\"xsd:string\">%s</codigo_remision>\n\t" \
                                "<nit xsi:type=\"xsd:integer\">%s</nit>\n\t" \
                                "<imagen xsi:type=\"xsd:integer\">1</imagen>\n\t" \
                                "<anexo xsi:type=\"xsd:integer\">1</anexo>\n\t" \
                                "<apikey xsi:type=\"xsd:string\">%s</apikey>\n\t" \
                                "<clave xsi:type=\"xsd:string\">%s</clave>\n" \
                            "</p>\n" \
                        "</Seguimiento_simple>\n" \
                    "</Body>\n" \
                  "</Envelope>" % (var[0], var[1], var[2], var[3])

        response = _conexion(self, payload,url)

        if response.status_code == 200:
            my_dict = xmltodict.parse(response.text)
            data = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:Seguimiento_simpleResponse']['Seguimiento_simpleResult']

            fecha_entrega = datetime.strptime(data['novedad']['fecha'],'%Y-%m-%d')
            fecha_entrega = fecha_entrega.strftime('%Y-%m-%d')
            hora_entrega = datetime.strptime(data['novedad']['hora'],'%H:%M:%S.%f')
            hora_entrega = hora_entrega.strftime('%H:%M:%S')

            self.write({
                'state': 'generate',
                'descripcion_estado': data['estado']['descripcion'],
                'fecha_entrega': data['estado']['fecha_texto'],
                'hora_entrega': data['estado']['hora_ap'],

                'descripcion_novedad': data['novedad']['descripcion'],
                'fecha_novedad': fecha_entrega,
                'hora_novedad': hora_entrega,

                'city_origen':data['nombre_origen'],
                'city_destino':data['nombre_destino'],
                'dia_promesa_servicio':data['dias_promesa_servicio'],
            })
        elif response.status_code == 500:
            self.write({
                'state': 'draft',
            })
            my_dict = xmltodict.parse(response.text)
            error = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            raise UserError('%s' % (error))