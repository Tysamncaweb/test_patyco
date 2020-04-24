# -*- coding: utf-8 -*-
import locale
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime
import pytz
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class DailyReport(models.Model):
    _name = 'daily.report'
    _description = 'Comprobante de Informe Diario'

    def _default_start_date(self):
        """ Find the earliest start_date of the latests sessions """
        # restrict to configs available to the user
        config_ids = self.env['pos.config'].search([]).ids
        # exclude configs has not been opened for 2 days
        self.env.cr.execute("""
            SELECT
            max(start_at) as start,
            config_id
            FROM pos_session
            WHERE config_id = ANY(%s)
            AND start_at > (NOW() - INTERVAL '2 DAYS')
            GROUP BY config_id
        """, (config_ids,))
        latest_start_dates = [res['start'] for res in self.env.cr.dictfetchall()]
        # earliest of the latest sessions
        return latest_start_dates and min(latest_start_dates) or fields.Datetime.now()

    start_date = fields.Datetime(required=True, default=_default_start_date)
    end_date = fields.Datetime(required=True, default=fields.Datetime.now)
    pos_config_ids = fields.Many2many('pos.config', 'pos_session_detail_configs',
        default=lambda s: s.env['pos.config'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    @api.multi
    def generate_daily_report(self, data):
        day_start = format((self.start_date).day)
        mes_start = format((self.start_date).month)
        year_start = format((self.start_date).year)
        day_end = format((self.end_date).day)
        mes_end = format((self.end_date).month)
        year_end = format((self.end_date).year)
        data = {
                'ids': self.ids,
                'model': 'report.paty_pos.daily_report_pos',
                'form': {
                    'date_start': self.start_date,
                    'day_start': day_start,
                    'mes_start': mes_start,
                    'year_start': year_start,
                    'day_end': day_end,
                    'mes_end': mes_end,
                    'year_end': year_end,
                    'date_stop': self.end_date,
                    'config_ids': self.pos_config_ids.ids,
                },
                'context': self._context
        }
        return self.env.ref('paty_pos.daily_report2').report_action(self, data=data, config=False)


class DailyReportTPV(models.AbstractModel):

    _name = 'report.paty_pos.daily_report_pos'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_stop = data['form']['date_stop']
        configs = data['form']['config_ids']
        day_start = data['form']['day_start']
        mes_start = data['form']['mes_start']
        year_start = data['form']['year_start']
        day_end = data['form']['day_end']
        mes_end = data['form']['mes_end']
        year_end = data['form']['year_end']

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

        if not configs:
            configs = self.env['pos.config'].search([])

        name = []
        for a in configs:
            configs_name = self.env['pos.config'].search([('id', '=', a)])
            name.append(configs_name.name)
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
        today = today.astimezone(pytz.timezone('UTC'))

        if date_start:
            date_start = fields.Datetime.from_string(date_start)
        else:
            # start by default today 00:00:00
            date_start = today

        if date_stop:
            # set time to 23:59:59
            date_stop = fields.Datetime.from_string(date_stop)
        else:
            # stop by default today 23:59:59
            date_stop = today + timedelta(days=1, seconds=-1)

        # avoid a date_stop smaller than date_start
        date_stop = max(date_stop, date_start)

        date_start = fields.Datetime.to_string(date_start)
        date_stop = fields.Datetime.to_string(date_stop)

        orders_line_taxes1 = ''
        service = []
        service1 = []
        product = []
        product1 = []
        taxes1 = {}
        taxes = {}
        contador = 0
        amount_bruto = 0
        amount_total = 0
        discount = 0
        iva = 0
        imco = 0

        unico = []
        a = []
        c = []
        repetido = []

        name_order = []
        journal = {}
        payment = 0

        uid = self._uid
        res_users = self.env['res.users'].search([('id', '=', uid)])
        res_partner = self.env['res.partner'].search([('id', '=', res_users.partner_id.id)])
        orders = self.env['pos.order'].search([
            ('date_order', '>=', date_start),
            ('date_order', '<=', date_stop),
            ('state', 'in', ['paid', 'invoiced', 'done']),
            ('config_id', 'in', configs),
            ('user_id', '=', uid)])

        for order in orders:
            name_order.append(order.pos_reference)
            contador += 1
            base = 0
            bruto = 0
            descuento = 0
            iva1 = 0
            total = 0
            imco = 0
            bruto_ex = 0
            descuento_ex = 0
            iva_ex = 0
            total_ex = 0
            imco_ex = 0
            iva = False
            exento = False

            st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', '=', order.id)])
            cont1 = 0
            for a in st_line_ids:
                payment += a.amount
                journal.setdefault(a['journal_id'], {'journal_id': a.journal_id.name, 'amount_sale': 0.0, 'contador': 0})
                journal[a['journal_id']]['amount_sale'] += a.amount
                journal[a['journal_id']]['contador'] += 1

            order_line = self.env['pos.order.line'].search([('order_id', '=', order.id)])
            currency = order.session_id.currency_id
            for orders_line in order_line:
                amount_bruto += orders_line.price_subtotal
                discount += -(orders_line.discount)
                iva += orders_line.price_subtotal_incl - orders_line.price_subtotal
                amount_total += orders_line.price_subtotal_incl - orders_line.discount

                product_type = self.env['product.template'].search([('id', '=', orders_line.product_id.product_tmpl_id.id)])
                if orders_line.tax_ids_after_fiscal_position:
                    orders_line_taxes = orders_line.tax_ids_after_fiscal_position.compute_all(orders_line.price_unit * (1-(orders_line.discount or 0.0)/100.0), currency, orders_line.qty, product=orders_line.product_id, partner=orders_line.order_id.partner_id or False)
                    for tax in orders_line_taxes['taxes']:
                        orders_line_taxes1 = tax['name']
                        if tax['name'] == 'IVA Ventas 19%' or tax['name'] == 'IVA Compra 19%':
                            if orders_line.product_id.product_tmpl_id.type != 'service':
                                taxes1.setdefault(tax['id'], {'name': tax['name'], 'tax_amount': 0.0, 'base_amount': 0.0, 'descuento': 0.0, 'imco': 0.0, 'total': 0.0,})
                                taxes1[tax['id']]['tax_amount'] += tax['amount'] if tax['name'] != 'IMCO' else 0.0
                                taxes1[tax['id']]['base_amount'] += tax['base']
                                taxes1[tax['id']]['imco'] += tax['amount'] if tax['name'] == 'IMCO' else 0.00
                                taxes1[tax['id']]['descuento'] += -(orders_line.discount)
                                taxes1[tax['id']]['total'] += orders_line.price_subtotal_incl - orders_line.discount
                            else:
                                taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount': 0.0, 'base_amount': 0.0, 'descuento': 0.0, 'imco': 0.0, 'total': 0.0, })
                                taxes[tax['id']]['tax_amount'] += tax['amount']
                                taxes[tax['id']]['base_amount'] += tax['base']
                                taxes[tax['id']]['descuento'] += -(orders_line.discount)
                                taxes[tax['id']]['total'] += orders_line.price_subtotal_incl - orders_line.discount

                            '''taxes1.append({
                                'name': tax['name'],
                                'amount': tax['amount'],
                                'base': tax['base'],    
                            })'''
                    
                if orders_line.product_id.product_tmpl_id.type == 'service':
                    format_new = "%d/%m/%Y"
                    date = datetime.strftime(order.date_order, format_new)
                    service.append({
                        'date': date,
                        'documento': orders_line.order_id.pos_reference,
                        'cliente': order.partner_id.name,
                        'bruto': orders_line.price_subtotal,
                        'descuento': -(orders_line.discount) if orders_line.discount != 0 else orders_line.discount,
                        'iva': (orders_line.price_subtotal_incl - orders_line.price_subtotal) if base == 0.00 else (orders_line.price_subtotal_incl - orders_line.price_subtotal - base),
                        'imco': base,
                        'iva_name': orders_line_taxes1,
                        'total': orders_line.price_subtotal_incl - orders_line.discount,
                    })
                    service1 = sorted(service, key=lambda k: k['documento'])

                else:

                    if order.pos_reference == orders_line.order_id.pos_reference:
                        format_new = "%d/%m/%Y"
                        date = datetime.strftime(order.date_order, format_new)
                        if (orders_line.price_subtotal_incl - orders_line.price_subtotal) != 0:
                            date1 = date
                            reference = orders_line.order_id.pos_reference
                            cliente = order.partner_id.name
                            bruto += orders_line.price_subtotal
                            imco += base
                            descuento += -(orders_line.discount) if orders_line.discount != 0 else orders_line.discount
                            iva1 += (orders_line.price_subtotal_incl - orders_line.price_subtotal) if base == 0.00 else (orders_line.price_subtotal_incl - orders_line.price_subtotal - base)
                            total += orders_line.price_subtotal_incl - orders_line.discount
                            iva = True
                        else:
                            date_ex = date
                            reference_ex = orders_line.order_id.pos_reference
                            cliente_ex = order.partner_id.name
                            bruto_ex += orders_line.price_subtotal
                            imco_ex += base
                            descuento_ex += -(orders_line.discount) if orders_line.discount != 0 else orders_line.discount
                            iva_ex += (orders_line.price_subtotal_incl - orders_line.price_subtotal) if base == 0.00 else (
                                        orders_line.price_subtotal_incl - orders_line.price_subtotal - base)
                            total_ex += orders_line.price_subtotal_incl - orders_line.discount
                            exento = True

            if iva == True and exento == True:
                product1.append({
                        'date': date1,
                        'documento': reference,
                        'cliente': cliente,
                        'bruto': bruto,
                        'descuento': descuento,
                        'iva': iva1,
                        'imco': imco,
                        'iva_name': orders_line_taxes1,
                        'total': total,
                     })

                product1.append({
                    'date': date_ex,
                    'documento': reference_ex,
                    'cliente': cliente_ex,
                    'bruto': bruto_ex,
                    'descuento': descuento_ex,
                    'iva': iva_ex,
                    'imco': imco_ex,
                    'iva_name': orders_line_taxes1,
                    'total': total_ex,
                })
            else:
                if iva == True:
                    product1.append({
                        'date': date1,
                        'documento': reference,
                        'cliente': cliente,
                        'bruto': bruto,
                        'descuento': descuento,
                        'iva': iva1,
                        'imco': imco,
                        'iva_name': orders_line_taxes1,
                        'total': total,
                    })
                else:
                    product1.append({
                        'date': date_ex,
                        'documento': reference_ex,
                        'cliente': cliente_ex,
                        'bruto': bruto_ex,
                        'descuento': descuento_ex,
                        'iva': iva_ex,
                        'imco': imco_ex,
                        'iva_name': orders_line_taxes1,
                        'total': total_ex,
                    })


            product = sorted(product1, key=lambda k: k['documento'])

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_stop': date_stop,
            'configs_name': name,
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
            'cajero': res_partner.name,
            'service': service,
            'product': product,
            'tax_unico': list(taxes1.values()),
            'taxes': list(taxes.values()),
            'contador': contador,
            'amount_bruto': amount_bruto,
            'amount_total': amount_total,
            'iva': iva,
            'discount': discount,
            'imco': imco,
            'fact_inicial': name_order[-1],
            'fact_final': name_order[0],
            'journal': list(journal.values()),
            'payment': payment,
        }