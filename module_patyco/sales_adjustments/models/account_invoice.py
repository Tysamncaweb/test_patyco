# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Modulo que permite la anulacion de cheques antes de ser emitidos
#    autor: Tysamnca.
#
##############################################################################

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime

class Salesadjustments(models.AbstractModel):

    _name = 'report.sales_adjustments.custom_invoice_template'

    @api.multi
    def _get_report_values(self, docids, data=None):
        data = {'form': self.env['account.invoice'].browse(docids)}
        invoices =[]
        invoice_lines = []
        invoices = self.env['account.invoice'].browse(docids)
        invoice_lines = self.env['account.invoice.line'].search([('invoice_id','=',docids)])
        order_lines = self.env['sale.order'].search([('order_line', '=', docids)])
        sequence_lines = self.env['ir.sequence.date_range'].search([('date_range_ids', '=', docids)])
        return {
            'doc_ids': docids,
            'doc_model': 'account.invoice',
            'docs': invoices[0],
            'docs_line':invoice_lines,
            'order_line': order_lines,
            'sequence_lines': sequence_lines[0],
        }
