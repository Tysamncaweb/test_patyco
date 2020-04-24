# -*- coding: utf-8 -*-
from odoo import http

# class Submodules/salesAdjustments(http.Controller):
#     @http.route('/submodules/sales_adjustments/submodules/sales_adjustments/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/submodules/sales_adjustments/submodules/sales_adjustments/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('submodules/sales_adjustments.listing', {
#             'root': '/submodules/sales_adjustments/submodules/sales_adjustments',
#             'objects': http.request.env['submodules/sales_adjustments.submodules/sales_adjustments'].search([]),
#         })

#     @http.route('/submodules/sales_adjustments/submodules/sales_adjustments/objects/<model("submodules/sales_adjustments.submodules/sales_adjustments"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('submodules/sales_adjustments.object', {
#             'object': obj
#         })