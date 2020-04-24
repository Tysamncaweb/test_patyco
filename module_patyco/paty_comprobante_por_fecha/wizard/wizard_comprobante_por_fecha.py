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


class WizardReportComprobante(models.TransientModel):
    _name = 'wizard.comprobante.contable.fecha'
    _description = "Wizard Report Comprobante Contable por Fecha"

    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    journal = fields.Many2one('account.journal')
    company = fields.Many2one('res.company')
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)


    def print_analitico_pdf(self):

        datas = []
        ids = []
        data = {
            'ids': ids,
            'model': 'paty_comprobante_por_fecha.report_comprobante_contable',
            'form': {
                'datas': datas,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'empresa': self.company.id,
                },
        }
        return self.env.ref('paty_comprobante_por_fecha.action_report_comprobante_por_fecha').report_action(docids=ids, data=data, config=False)

class ReportComprobanteContable(models.AbstractModel):

    _name = 'report.paty_comprobante_por_fecha.report_comprobante_contable'

    @api.multi
    def _get_report_values(self, docids, data=None):



        ids = data['ids']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end
        }