# coding: utf-8

###############################################################################

from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date
from odoo.exceptions import ValidationError
from io import BytesIO
import xlwt, base64
from decimal import *


class WizardReport1007(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _name = 'wizard.report.1007'
    _description = "Wizard Report Comprobante 1007"

    date_start = fields.Date('Fecha Desde')
    date_end = fields.Date('Fecha Hasta')    
    #concepto=fields.Many2one('account.conceptos',string='Concepto')  
    formato=fields.Many2one('account.formatos',string='Formatos') 
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)

    def print_1007_pdf(self):

        datas = []
        ids = []
        data = {
            'ids': ids,
            'model': 'paty_medios_mag_1007.reporte_templete_1007',  # id del templete del archivo para el pdf, aqui paso las variables al xml
            'form': {
                'datas': datas,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'date_formato': self.formato,                
                },
        }
        return self.env.ref('paty_medios_mag_1007.action_report_pdf_1007').report_action(docids=ids, data=data, config=False)# llama a la accion del boton pdf
    
    
class ReportComprobante1007(models.AbstractModel):
    _name = 'report.paty_medios_mag_1007.reporte_templete_1007'

    @api.multi
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        res_all_comprobante = self.get_datos_por_comprobante(date_start, date_end)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            #'type_report': type_report,
            'datos': res_all_comprobante
        }

    @api.multi  # una funcion propia de odoo
    def get_datos_por_comprobante(self,date_start, date_end):
        res_all_comprobantes = []

        self.env.cr.execute('''SELECT * FROM account_invoice WHERE type='out_invoice' AND state='open';''')
        res_all_comprobantes = self.env.cr.fetchall()

        return res_all_comprobantes

class FuncionesAdicionales(models.Model):
    
    _inherit ='res.partner'
    _columns = {

        }

    _defaults = {
        }
    def nb_cliente(selft,id_partner):
        nb_nombre='Darrell'
        return nb_nombre