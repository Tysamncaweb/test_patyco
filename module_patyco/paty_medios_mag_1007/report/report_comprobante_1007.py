 # -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.exceptions import UserError

class ReportComprobante1007(models.AbstractModel):
    _name = 'report.paty_medios_mag_1007.reporte_templete_1007'

    @api.multi
    def _get_report_values(self,docids,data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        res_all_comprobante= self.get_datos_por_comprobante(date_start,date_end)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            #'type_report': type_report,
            'datos': res_all_comprobante
        }

    @api.multi  # una funcion propia de odoo
    def get_datos_por_comprobante(self):
        res_all_comprobantes = []

        self.env.cr.execute('''SELECT * FROM account_invoice WHERE type='out_invoice' AND state='open';''')
        res_all_comprobantes = self.env.cr.fetchall()

        return res_all_comprobantes