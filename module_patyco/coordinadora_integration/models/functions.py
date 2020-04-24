from odoo.exceptions import UserError,Warning
import re
import requests
import base64
import time

## Validaciones ##

#Validación de Nombre completo
def validate_full_name(self ,full_name):
    if full_name:
        val_name_o = full_name
        if (val_name_o.replace(" ", "")).isalpha():
            return full_name.title()
        else:
            raise UserError('Introduzca solo letras para el nombre completo')
    else:
        raise UserError('El campo "Nombre Completo" esta vacío')

#Validación de Cedula
def validate_ci(self ,ci):
    if ci:
        if ci.isdigit():
            return True
        else:
            raise UserError('Introduzca solo número en la cedula')
    else:
        raise UserError('El campo "Cédula" esta vacío')

#Validación de Email
def validate_email(self ,email):
    exp_regular = r"[\w.%+-]+@[\w.-]+\.+[a-zA-Z]{2,3}"
    res = re.compile(exp_regular)
    res = res.match(email.lower())
    if res and len(email) == res.regs[0][1]:
        return email.lower()
    else:
        raise UserError('Introduzca un correo valido')

#Validación de telefono
def validate_telephone(self ,telephone):
    if telephone:
        if telephone.isdigit():
            return True
        else:
            raise UserError('Introduzca solo número en el telefono')
    else:
        raise UserError('El campo "Teléfono" esta vacío')

def validate_number_guide(self,number_guide):
    if number_guide:
        number_guide = number_guide.replace(' ', '')
        if number_guide.isdigit():
            return number_guide
        else:
            raise UserError('Introduzca solo números para la guía')
    else:
        raise UserError('El campo "Número de guía" esta vacío')



#Conexión con la api
def _conexion(self ,payload,url):

    headers = {
        'Content-Type': "text/xml",
        'cache-control': "no-cache",
        'Postman-Token': "caf8573a-a866-4501-9718-e1be84f2623e"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    return response

#Imprimir pdf codificados
def _print_documents(self,name_report,code_pdf):
    with open(name_report, 'wb') as theFile:
        theFile.write(base64.b64decode(code_pdf))

    r = base64.b64encode(open(name_report, 'rb').read())
    my_file = self.env['save.file.wizard'].create({
        'file_name': name_report,
        'my_file': r,
    })

    return {
        'name': ('Descarga de archivo'),
        'res_id': my_file.id,
        'res_model': 'save.file.wizard',
        'target': 'new',
        'type': 'ir.actions.act_window',
        'view_id': self.env.ref('coordinadora_integration.save_file_wizand_view_done').id,
        'view_mode': 'form',
        'view_type': 'form',
    }


def data_general(self, values):
    """Permite introducción información general como, fecha de generación, id y nombre de usuario"""
    if values:
        values['date'] = time.strftime('%Y-%m-%d')
        context = self._context
        current_uid = context.get('uid')
        var = self.env['res.users'].browse(current_uid)
        values['user_id'] = current_uid
        values['user_name'] = var.display_name
        return