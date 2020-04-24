from odoo import models, fields, api
from odoo.exceptions import UserError,Warning,ValidationError
import xmltodict
from ..models import functions

class UpdateSettingsCodesDanesWizard(models.TransientModel):
    _name = "coordinadora.settings.update.codes.danes.wizard"

    name = fields.Char('Nombre')
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')

    @api.multi
    def generate_update_code_danes(self):
        bus = self.env['coordinadora.settings'].search([('id', '!=', 0)])
        if not bus:
            raise UserError(
                'No se pudo Generar la Etiqueta debido a que no se a realizado la configuración del usuario de Coordinadora')
        bus = bus[-1]
        var = [
            bus.user,
            bus.password_sha256,
        ]
        url = "http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php"
        payload = "<Envelope xmlns=\"http://schemas.xmlsoap.org/soap/envelope/\">\n" \
                    "<Body>\n" \
                        "<Guias_ciudades xmlns=\"http://sandbox.coordinadora.com/agw/ws/guias/1.6/server.php\">\n" \
                            "<p xsi:type=\"ser:Agw_ciudadesIn\">\n\t" \
                                "<usuario xsi:type=\"xsd:string\">%s</usuario>\n\t" \
                                "<clave  xsi:type=\"xsd:string\">%s</clave>\n" \
                            "</p>\n" \
                        "</Guias_ciudades>\n" \
                    "</Body>\n" \
                  "</Envelope>" % (var[0], var[1])

        response = functions._conexion(self, payload,url)

        if response.status_code == 200:
            envio = {}
            codes = []
            #prueba = []
            my_dict = xmltodict.parse(response.text)
            datas = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ns1:Guias_ciudadesResponse']['return']['item']
            for data in datas:
                codes.append({
                    'code_dane':data['codigo']['#text'],
                    'name':data['nombre']['#text'],
                    'name_department':data['nombre_departamento']['#text'],
                })
            #prueba.append({
             #       'code_dane':'52224000',
              #      'name':'CARLOSAMA CUASPUD (NAR)',
               #     'name_department':'Nariño',
                #})
            object = self.env['coordinadora.settings.codes.danes']
            for code in codes:
                verifs = object.search([('code_dane','=',code['code_dane']),('name','ilike',code['name'])]) #para pruebas '!='
                if verifs:
                    verifs.write({
                        'states':'available',
                    })
                    print(code)
                else:
                    bus_depart = self.env['coordinadora.settings.department'].search([('name','=',code['name_department'])])
                    if bus_depart:
                        envio.update({
                            'code_dane' : code['code_dane'],
                            'name': code['name'],
                            'department_id' : bus_depart.id,
                            'states' : 'available',
                        })
                        print(code)
                        object.create(envio)

            self.write({
                'state': 'get',
                'name':'La actualización fue Exitosa, vayaa al menú Códigos Danes para verificarlos.',
            })

            return {
                'name': ('Actualización Exitosa'),
                'res_id': self.id,
                'res_model': 'coordinadora.settings.update.codes.danes.wizard',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('coordinadora_integration.update_codes_danes_wizard_view').id,
                'view_mode': 'form',
                'view_type': 'form',
            }

        elif response.status_code == 500:
            my_dict = xmltodict.parse(response.text)
            error = my_dict['SOAP-ENV:Envelope']['SOAP-ENV:Body']['SOAP-ENV:Fault']['faultstring']
            raise UserError('%s' % (error))

