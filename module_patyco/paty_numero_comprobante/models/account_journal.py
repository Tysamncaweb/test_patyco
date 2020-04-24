# -*- coding: utf-8 -*-

from  odoo import models, fields, api, exceptions

class AccountJournalCorrelativo(models.Model):
    '''Esta clase es para agregar al Diario un número correlativo de comprobante'''
    _inherit = 'account.journal'

    correlativo = fields.Char("Comprobante")
