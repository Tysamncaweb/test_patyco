# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from io import BytesIO
import xlwt, base64

class DailyReport_2(models.Model):
    _name = 'auxiliar.report'
    _description = 'reporte auxiliar'


    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    cuenta = fields.Many2one('account.account', required=True)
    '''Imprimir XLS'''
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_auxiliar_report(self, data):
        data = {
                'ids': self.ids,
                'model': 'report.paty_reports_vari.auxiliar_report',
                'form': {
                    'fecha_inicio': self.start_date,
                    'fecha_fin': self.end_date,
                    'cuenta': self.cuenta.id,

                },
                'context': self._context
        }
        return self.env.ref('paty_reports_vari.auxiliar_report2').report_action(self, data=data, config=False)

    @api.multi
    def generate_auxiliar_xls(self, data):

        self.ensure_one()
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        writer = wb.add_sheet('Nombre de hoja')

        header_content_style = xlwt.easyxf("font: name Helvetica size 40 px, bold 1, height 200; align: horiz center;")
        sub_header_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz center;") #color pattern: pattern solid,fore_colour blue;
        sub_header_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        sub_header_style_bold1 = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; align: horiz right;",
                                             num_format_str='#,##0.00')
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170; align: horiz right;",
                                         num_format_str='#.##0,00')
        line_content_style_totales = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right;",
            num_format_str='#,##0.00')

        fecha_inicio = datetime.strptime(str(self.start_date), '%Y-%m-%d')
        fecha_fin = datetime.strptime(str(self.end_date), '%Y-%m-%d')
        mes_ini = format((fecha_inicio).month)
        mes_fin = format((fecha_fin).month)
        meses_abr = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        mes_ini = meses_abr[int(mes_ini) - 1]
        mes_fin = meses_abr[int(mes_fin) - 1]
        fecha_inicio = fecha_inicio.strftime(str(mes_ini) + '-' + '%d-%Y')
        fecha_fin = fecha_fin.strftime(str(mes_fin) + '-' + '%d-%Y')

        row = 1
        col = 0
        #writer.col(col).width = 9000
        # writer.write_merge(row, row, 0, header_cols, "Información de contactos",)
        row += 1

        writer.write_merge(row, row, 5, 7, 'PATYCO S.A.S - 900.672.558-5', header_content_style)
        row += 1
        writer.write_merge(row, row, 4, 8, 'Auxiliar General - Histórico '+ str(fecha_inicio) + ' A ' + str(fecha_fin), header_content_style)

        row += 2
        writer.write_merge(row, row, 1, 1,  "Cuenta", sub_header_style)
        writer.write_merge(row, row, 2, 3,  "Nombre Cuenta", sub_header_style)
        writer.write_merge(row, row, 4, 4,  "Nit", sub_header_style)
        writer.write_merge(row, row, 5, 6,  "Nombre Nit", sub_header_style)
        writer.write_merge(row, row, 7, 8,  "Documento ref", sub_header_style)
        writer.write_merge(row, row, 9, 9,  "Fecha", sub_header_style)
        writer.write_merge(row, row, 10, 10, "Comprobante", sub_header_style)
        writer.write_merge(row, row, 11, 11, "Documento", sub_header_style)
        writer.write_merge(row, row, 12, 12, "Detalle", sub_header_style)
        writer.write_merge(row, row, 13, 13, "Saldo Anterior", sub_header_style)
        writer.write_merge(row, row, 14, 14, "Débitos", sub_header_style)
        writer.write_merge(row, row, 15, 15, "Créditos", sub_header_style)
        writer.write_merge(row, row, 16, 16, "Nuevo Saldo", sub_header_style)


        #///////////////////LINEAS DE DATA//////////////////////////////////
        cuenta = self.cuenta.id
        cuenta2 = self.env['account.account'].search([('id', '=', cuenta)])
        clientes = self.env['res.partner'].search(
            ['|', ('property_account_receivable_id', '=', cuenta), ('property_account_payable_id', '=', cuenta)])
        for client in clientes:
            facturas = self.env['account.invoice'].search(
                [('partner_id', '=', client.id), ('date_invoice', '>=', self.start_date), ('date_invoice', '<=', self.end_date),
                 ('state', '!=', 'daft')])
            for fact in facturas:
                monto_pagos = 0
                pagos = self.env['account.payment'].search([('communication', '=', fact.reference)])
                for pago in pagos:
                    monto_pagos += pago.amount
                row += 1
                writer.write_merge(row, row, 1, 1,   cuenta2.code, sub_header_style)
                writer.write_merge(row, row, 2, 3,   cuenta2.name, sub_header_style)
                writer.write_merge(row, row, 4, 4,   client.vat, sub_header_style)
                writer.write_merge(row, row, 5, 6,   client.name, sub_header_style)
                writer.write_merge(row, row, 7, 8,   fact.number, sub_header_style)
                writer.write_merge(row, row, 9, 9,   str(fact.date_invoice), sub_header_style)
                writer.write_merge(row, row, 10, 10, fact.journal_id.sequence, sub_header_style)
                writer.write_merge(row, row, 11, 11, fact.move_id.ref, sub_header_style)
                writer.write_merge(row, row, 12, 12, fact.name, sub_header_style)
                writer.write_merge(row, row, 13, 13,  self.formato_cifras(fact.amount_total), sub_header_style)
                writer.write_merge(row, row, 14, 14,  self.formato_cifras(monto_pagos), sub_header_style)
                writer.write_merge(row, row, 15, 15,  self.formato_cifras(fact.amount_total), sub_header_style)
                writer.write_merge(row, row, 16, 16,  self.formato_cifras(fact.residual), sub_header_style)

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'Auxiliar General-Histórico.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'auxiliar.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

    def formato_cifras(self, valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return monto
class DailyReportTPV(models.AbstractModel):

    _name = 'report.paty_reports_vari.auxiliar_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        fecha_inicio = data['form']['fecha_inicio']
        fecha_fin = data['form']['fecha_fin']
        date_from = fecha_inicio
        date_to = fecha_fin
        cuenta = data['form']['cuenta']
        #Reestructurando formato de fechas
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        mes_ini = format((fecha_inicio).month)
        mes_fin = format((fecha_fin).month)
        meses_abr = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        mes_ini = meses_abr[int(mes_ini) - 1]
        mes_fin = meses_abr[int(mes_fin) - 1]
        fecha_inicio = fecha_inicio.strftime(str(mes_ini)+'-'+'%d-%Y')
        fecha_fin = fecha_fin.strftime(str(mes_fin)+'-'+'%d-%Y')
        docs = []
        #/////////////////////////////////////////////////////////////////////////////////////////////////
        cuenta2 = self.env['account.account'].search([('id', '=', cuenta)])
        clientes = self.env['res.partner'].search(['|',('property_account_receivable_id', '=', cuenta), ('property_account_payable_id', '=', cuenta)])
        for client in clientes:
            facturas = self.env['account.invoice'].search([('partner_id', '=', client.id),('date_invoice','>=',date_from),('date_invoice','<=',date_to),('state','!=','daft')])
            for fact in facturas:
                monto_pagos = 0
                pagos = self.env['account.payment'].search([('communication','=',fact.reference)])
                for pago in pagos:
                    monto_pagos += pago.amount
                docs.append({
                    'cuenta' : cuenta2.code,
                    'name_cuenta': cuenta2.name,
                    'nit': client.vat,
                    'name_nit': client.name,
                    'documento_ref': fact.number,
                    'fecha': fact.date_invoice,
                    'comprobante': fact.journal_id.sequence,
                    'documento': fact.move_id.ref,
                    'detalle': fact.name,
                    'saldo_anterior': self.formato_cifras(fact.amount_total),
                    'debitos': self.formato_cifras(monto_pagos) ,
                    'creditos': self.formato_cifras(fact.amount_total),
                    'nuevo_saldo': self.formato_cifras(fact.residual),

                })
                saldos = self.env['account.payment'].search([('communication', '=', fact.reference)])
                #for sal in saldos:


        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'docs': docs,

        }
    def formato_cifras(self, valor):
        monto = '{0:,.2f}'.format(valor).replace('.', '-')
        monto = monto.replace(',', '.')
        monto = monto.replace('-', ',')
        return monto