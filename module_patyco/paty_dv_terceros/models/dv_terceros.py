# -*- coding: utf-8 -*-
import string
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta, date, datetime

class Partner(models.Model):
    _inherit = "res.partner"

    name2 = fields.Char('Segundo Nombre')
    last_name = fields.Char('')
    last_name2 = fields.Char()
    dv = fields.Integer(compute='verification_code', required=True)
    vat = fields.Char(string='Tax ID', required=True,
                      help="The Tax Identification Number. Complete it if the contact is subjected to government taxes. Used in some legal statements.")

    @api.onchange('vat')
    def verification_code(self):
        if self.vat:
            factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
            rut_ajustado = str.rjust(str(self.vat), 15, '0')
            s = sum(int(rut_ajustado[14 - i]) * factores[i] for i in range(14)) % 11
            if s > 1:
                self.dv = 11 - s
            else:
                self.dv = s
