# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPickingAdaptation(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    var_id = fields.Char()

    @api.onchange('var_id')
    def assign_string(self):
        if self._context.get('default_picking_type_id'):
            var = self._context.get('default_picking_type_id')
            self.var_id = var

    @api.model
    def create(self,vals):
        vals['var_id'] = vals.get('picking_type_id')
        return super(StockPickingAdaptation, self).create(vals)


