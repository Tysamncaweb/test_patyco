# -*- coding: utf-8 -*-


import itertools

from odoo.addons import decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression
from odoo.tools import pycompat


# class submodules/sales_adjustments(models.Model):
#     _name = 'submodules/sales_adjustments.submodules/sales_adjustments'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class ProductTemplate(models.Model):
    _inherit = "product.template"


    company_id = fields.Many2one('res.company', string='Company')
    Packaging_unit_id = fields.Integer( string='Unidad de empaque', default=0)
    measurements = fields.Char(string='Medidas', size=5)
    measurements_campoa = fields.Char(string='Medidas', size=5)
    measurements_campob = fields.Char(string='Medidas', size=5)
    type_of_packaging_id = fields.Many2one('product.attribute.value.prueba', string='Tipo de Empaque')
    Quantity_for_Freight = fields.Char(string='Cantidad para Flete', size=20)
    freight_value_main_city_id =fields.Float(string='Valor de Flete Ciudad Principal', digits=(5, 2))
    suggested_price_without_freight = fields.Float(string='Precio Sugerido sin Flete', digits=(5, 2))
    code_prudct_patyco = fields.Char(string='Codigo de Producto')



class ProductAttributeValuePrueba(models.Model):
    _name = "product.attribute.value.prueba"
    _rec_name = 'type_of_packaging_id'

    type_of_packaging_id = fields.Char(string='Tipo de Empaque')
    code_prudct_patyco_id = fields.Char(string='Codigo de Producto')



