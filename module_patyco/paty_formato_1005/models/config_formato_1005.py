# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class ConfigFormato1005(models.Model):
    _name = 'account.config.formato.1005'
    _description = 'Configuracion las cuentas contables del formato 1005'

    tipo_iva = fields.Selection([('iva_descontable', 'Iva Descontable'),
                                ('iva_devolucion', 'Iva por devolución')],
                                string='Tipo de IVA')
    cuentas_lineas = fields.One2many('account.config.formato.1005.lines','config_id',string='Cuentas contables')

    @api.model
    def map_account(self, account):
        for pos in self.cuentas_lineas:
            if pos.account_src_id == account:
                return pos.account_dest_id
        return account

    @api.model
    def map_accounts(self, accounts):
        """ Receive a dictionary having accounts in values and try to replace those accounts accordingly to the fiscal position.
        """
        ref_dict = {}
        for line in self.cuentas_lineas:
            ref_dict[line.account_src_id] = line.account_dest_id
        for key, acc in accounts.items():
            if acc in ref_dict:
                accounts[key] = ref_dict[acc]
        return accounts


class ConfigFormato1005Lines(models.Model):
    _name = 'account.config.formato.1005.lines'
    _description = 'Cuentas contables de formato 1005'

    config_id = fields.Many2one('account.config.formato.1005',string='Id lineas')
    account_src_id = fields.Many2one('account.account',string="Cuentas Contables")