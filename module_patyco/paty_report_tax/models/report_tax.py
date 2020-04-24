# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from io import BytesIO
import xlwt, base64

class DailyReport(models.Model):
    _name = 'tax.report'
    _description = 'Analisis de base de impuestos'


    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    company = fields.Many2one('res.company', required=True)
    target_movement = fields.Selection([
        (0, 'Todos los asientos validados'),
        (1, 'Todos los asientos')
    ], required=True, string="Movimientos Destino")
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
    def generate_tax_report(self, data):
        day_start = format((self.start_date).day)
        mes_start = format((self.start_date).month)
        year_start = format((self.start_date).year)
        day_end = format((self.end_date).day)
        mes_end = format((self.end_date).month)
        year_end = format((self.end_date).year)
        data = {
                'ids': self.ids,
                'model': 'report.paty_report_tax.tax_report',
                'form': {
                    'date_start': self.start_date,
                    'day_start': day_start,
                    'mes_start': mes_start,
                    'year_start': year_start,
                    'day_end': day_end,
                    'mes_end': mes_end,
                    'year_end': year_end,
                    'date_stop': self.end_date,
                    'target_movement': self.target_movement,
                    'company': self.company.id,
                },
                'context': self._context
        }
        return self.env.ref('paty_report_tax.tax_report2').report_action(self, data=data, config=False)

    @api.multi
    def generate_tax_xls(self, data):
        format_new = "%d/%m/%Y"
        day_end = format((self.end_date).day)
        mes_end = format((self.end_date).month)
        year_end = format((self.end_date).year)
        unico = []

        meses_abr = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        month_end = meses_abr[int(mes_end) - 1]

        self.ensure_one()
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        writer = wb.add_sheet('Nombre de hoja')

        header_content_style = xlwt.easyxf("font: name Helvetica size 40 px, bold 1, height 200; align: horiz center;")
        sub_header_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid;")
        sub_header_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170;")
        sub_header_style_bold1 = xlwt.easyxf("font: name Helvetica size 10 px, bold 1, height 170; align: horiz right;",
                                             num_format_str='#,##0.00')
        sub_header_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170;")
        line_content_style = xlwt.easyxf("font: name Helvetica size 10 px, height 170; align: horiz right;",
                                         num_format_str='#.##0,00')
        line_content_style_totales = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin; align: horiz right;",
            num_format_str='#,##0.00')

        row = 1
        col = 0
        #writer.col(col).width = 9000
        # writer.write_merge(row, row, 0, header_cols, "Información de contactos",)
        writer.write_merge(row, row, 4, 8, str(self.company.name) + '-' + str(self.company.vat), header_content_style)

        row += 1

        writer.write_merge(row, row, 4, 8, "Análisis Base de Impuestos" + '  ' + month_end + '-' + str(day_end) + '-' + str(year_end), header_content_style)

        tax = []
        move = []
        move_asc = []
        tax_asc = []
        unico = []
        repetido = []



        row += 2
        writer.write_merge(row, row, 1, 1, "Compt", sub_header_style)
        writer.write_merge(row, row, 2, 2, "Docto.", sub_header_style)
        writer.write_merge(row, row, 3, 3, "D. Ref.", sub_header_style)
        writer.write_merge(row, row, 4, 4, "Fecha", sub_header_style)
        writer.write_merge(row, row, 5, 5, "Débitos", sub_header_style)
        writer.write_merge(row, row, 6, 6, "Créditos", sub_header_style)
        writer.write_merge(row, row, 7, 7, "Base Retención", sub_header_style)
        writer.write_merge(row, row, 8, 8, "%", sub_header_style)
        writer.write_merge(row, row, 9, 9, "Nit", sub_header_style)
        writer.write_merge(row, row, 10, 10, "Nombre", sub_header_style)

        tax_name = self.env['account.tax'].search([('company_id', '=', self.company.id)])
        if self.target_movement == 0:
            move_line_tax = self.env['account.move.line'].search([('date', '>=', self.start_date),
                                                                  ('date', '<=', self.end_date),
                                                                  ('company_id', '=', self.company.id),
                                                                  ('move_id.state', '=', 'posted'),
                                                                  ('tax_line_id', '!=', False)])
        if self.target_movement == 1:
            move_line_tax = self.env['account.move.line'].search([('date', '>=', self.start_date),
                                                                  ('date', '<=', self.end_date),
                                                                  ('company_id', '=', self.company.id),
                                                                  ('tax_line_id', '!=', False)])

        for moves in move_line_tax:
            docto = moves.move_id.name
            a = len(docto)
            padding = moves.journal_id.sequence_id.padding
            b = a - padding
            documento = docto[b:a]
            move.append({
                'name': moves.partner_id.name,
                'nit': moves.partner_id.vat,
                'porcentaje': moves.tax_line_id.amount,
                'tax_id': moves.tax_line_id.id,
                'credit': moves.credit,
                'debit': moves.debit,
                'date': datetime.strftime(moves.date, format_new),
                'reference': moves.ref,
                'documento': documento,
                'compt': moves.journal_id.code,
                'base': moves.tax_base_amount,
            })
            move_asc = sorted(move, key=lambda k: k['porcentaje'])
            move_asc.reverse()

            tax.append({
                'id': moves.tax_line_id.id,
                'name': moves.tax_line_id.name,
                'code': moves.tax_line_id.account_id.code,
                'amount': moves.tax_line_id.amount,
            })

            tax_asc = sorted(tax, key=lambda k: k['amount'])
            tax_asc.reverse()

        for vars in tax_asc:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('id') == vars2.get('id')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)


        for a in unico:
            suma_debit = 0
            suma_credit = 0
            suma_base = 0
            row += 1
            writer.write_merge(row, row, 1, 2, a['code'], sub_header_style_bold)
            writer.write_merge(row, row, 3, 10, a['name'], sub_header_style_bold)
            for b in move_asc:
                if a['id'] == b['tax_id']:
                    row += 1
                    writer.write_merge(row, row, 1, 1, b['compt'], sub_header_content_style)
                    writer.write_merge(row, row, 2, 2, b['documento'], sub_header_content_style)
                    writer.write_merge(row, row, 3, 3, b['reference'], sub_header_content_style)
                    writer.write_merge(row, row, 4, 4, b['date'], sub_header_content_style)
                    writer.write_merge(row, row, 5, 5, locale.format_string("%.2f", b['debit']), line_content_style)
                    writer.write_merge(row, row, 6, 6, locale.format_string("%.2f", b['credit']), line_content_style)
                    writer.write_merge(row, row, 7, 7, locale.format_string("%.2f", b['base']), line_content_style)
                    writer.write_merge(row, row, 8, 8, b['porcentaje'], sub_header_content_style)
                    writer.write_merge(row, row, 9, 9, b['nit'], sub_header_content_style)
                    writer.write_merge(row, row, 10, 10, b['name'], sub_header_content_style)

                    suma_base += b['base']
                    suma_credit += b['credit']
                    suma_debit += b['debit']
            row += 1
            writer.write_merge(row, row, 1, 4, "Total", sub_header_style)
            writer.write_merge(row, row, 5, 5, locale.format_string("%.2f", suma_debit), line_content_style_totales)
            writer.write_merge(row, row, 6, 6, locale.format_string("%.2f", suma_credit), line_content_style_totales)
            writer.write_merge(row, row, 7, 7, locale.format_string("%.2f", suma_base), line_content_style_totales)


        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'Análisis_base_de_Impuestos.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tax.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

class DailyReportTPV(models.AbstractModel):

    _name = 'report.paty_report_tax.tax_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_stop = data['form']['date_stop']
        target_movement = data['form']['target_movement']
        company = data['form']['company']
        day_start = data['form']['day_start']
        mes_start = data['form']['mes_start']
        year_start = data['form']['year_start']
        day_end = data['form']['day_end']
        mes_end = data['form']['mes_end']
        year_end = data['form']['year_end']

        format_new = "%d/%m/%Y"
        tz = pytz.timezone('America/Bogota')
        today = datetime.now(tz)
        hora = today.hour
        month = format(today.month)
        year = format(today.year)
        day = format(today.day)

        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        meses_abr = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        mes = meses[int(mes_start) - 1]
        month_end = meses[int(mes_end) - 1]
        mes_abr = meses_abr[int(month) - 1]

        if hora >= 13:
            horas = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            hora = horas[hora - 13]
            mt = 'PM'
        else:
            mt = 'AM'
        if hora == 12:
            mt = 'PM'

        minute = today.minute
        if minute < 10:
            time = str(hora) + ':' + '0' + str(minute) + ' ' + mt
        else:
            time = str(hora) + ':' + str(minute) + ' ' + mt


        tax = []
        move = []
        move_asc = []
        tax_asc = []
        unico = []
        repetido = []

        uid = self._uid
        tax_name = self.env['account.tax'].search([('company_id', '=', company)])
        if target_movement == 0:
            move_line_tax = self.env['account.move.line'].search([('date', '>=', date_start),
                                                                  ('date', '<=', date_stop),
                                                                  ('company_id', '=', company),
                                                                  ('move_id.state', '=', 'posted'),
                                                                  ('tax_line_id', '!=', False)])
        if target_movement == 1:
            move_line_tax = self.env['account.move.line'].search([('date', '>=', date_start),
                                                                  ('date', '<=', date_stop),
                                                                  ('company_id', '=', company),
                                                                  ('tax_line_id', '!=', False)])

        for moves in move_line_tax:
            docto = moves.move_id.name
            a = len(docto)
            padding = moves.journal_id.sequence_id.padding
            b = a - padding
            documento = docto[b:a]
            move.append({
                'name': moves.partner_id.name,
                'nit': moves.partner_id.vat,
                'porcentaje': moves.tax_line_id.amount,
                'tax_id': moves.tax_line_id.id,
                'credit': moves.credit,
                'debit': moves.debit,
                'date': datetime.strftime(moves.date, format_new),
                'reference': moves.ref,
                'documento': documento,
                'compt': moves.journal_id.code,
                'base': moves.tax_base_amount,
            })
            move_asc = sorted(move, key=lambda k: k['porcentaje'])
            move_asc.reverse()

            tax.append({
                'id': moves.tax_line_id.id,
                'name': moves.tax_line_id.name,
                'code': moves.tax_line_id.account_id.code,
                'amount': moves.tax_line_id.amount,
            })

            tax_asc = sorted(tax, key=lambda k: k['amount'])
            tax_asc.reverse()

        for vars in tax_asc:
            if unico:
                cont = 0
                for vars2 in unico:
                    if (vars.get('id') == vars2.get('id')):
                        repetido.append(vars)
                        cont += 1
                if cont == 0:
                    unico.append(vars)
            else:
                unico.append(vars)




        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_stop': date_stop,
            'today': today,
            'hora': time,
            'mes': mes,
            'month_end': month_end,
            'ano': year,
            'year_end': year_end,
            'year_start': year_start,
            'day': day,
            'day_start': day_start,
            'day_end': day_end,
            'mes_abr': mes_abr,
            'tax': unico,
            'tax_line': move_asc,
        }