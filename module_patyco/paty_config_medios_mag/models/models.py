# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class TablaFormatos(models.Model):
    _name = "account.formatos"
    # nombre de la tabla de la base de datos o Modelo

    cod=fields.Char(string='Codigo', required=True)
    name=fields.Char(string='Nombre',required=True) # Nombre de mi campo tipo string o caracter y obligatorio
    descripcion=fields.Char(string='Descripcion')           # nombre de mi campo apellido


    
class TablaConceptos(models.Model):
    _name = "account.conceptos" # nombre de la tabla de la base de datos o Modelo

    cod=fields.Char(string='Codigo', required=True)
    name=fields.Char(string='Nombre',required=True) # Nombre de mi campo tipo string o caracter y obligatorio
    descripcion=fields.Char(string='Descripcion')
    cod_formato=fields.Many2one('account.formatos', string='Formato')


class MediosMagneticos(models.Model):
    _name = 'account.medios.magneticos'

    formatos = fields.Many2one('account.formatos', 'Formatos')
    conceptos = fields.Many2one('account.conceptos', 'Conceptos')
    cuentas_lineas = fields.One2many('account.lines.medios.magneticos', 'position_mag_id', string='Account Mapping', copy=True)

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


class CuentasMediosMagneticos(models.Model):
    _name = 'account.lines.medios.magneticos'
    _description = 'Cuentas contables de medios magneticos'
    _rec_name = 'position_mag_id'

    position_mag_id = fields.Many2one('account.medios.magneticos', string='Fiscal Position')
    account_src_id = fields.Many2one('account.account', string='Cuentas Medios Magneticos',
        domain=[('deprecated', '=', False)], required=True)
    tipo_movimiento = fields.Selection([('NCD', 'NetoCD'),
                                        ('NDC', 'NetoDC'),
                                        ('saldo', 'Saldo')],
                                       string='Tipo movimiento')
    tipo_ret = fields.Many2one('account.tax', string="Tipo de Retención")

