# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError,Warning
import time

class LiquidarGuia(models.Model):
    _name = 'liquidar.guia'
    _description = "Guias liquidadas"

    name = fields.Char()
    state = fields.Selection([('draft', 'Borrador'), ('liquidado', 'Liquidado',)], default='draft')
    numero = fields.Char('N° de Guía', size=15)
    date = fields.Date('Fecha')
    user_id = fields.Many2one('res.users', 'Usuario')
    user_name = fields.Char('Nombre de Usuario')
    var = fields.Char('N° de Guía')

    _defaults = {
        'state': 'draft'}

    @api.model
    def name_get(self):
        res = []
        for number in self:
            res.append((number.id, 'Guía: %s' % (number.numero)))

        return res

    @api.multi
    def generate_guide(self):
        self.write({
            'state':'liquidado',
        })



    @api.multi
    def obtener_fecha(self,values):
        if values:
            values['date'] = time.strftime('%Y-%m-%d')
            context = self._context
            current_uid = context.get('uid')
            var = self.env['res.users'].browse(current_uid)
            values['user_id'] = current_uid
            values['user_name'] = var.display_name
            values['var'] = values.get('numero')
            return


    @api.model
    def write(self, values):
        self.obtener_fecha(values)
        res = super(LiquidarGuia, self).write(values)
        return res

    @api.model
    def create(self,values):
        self.obtener_fecha(values)
        res = super(LiquidarGuia, self).create(values)
        return res
