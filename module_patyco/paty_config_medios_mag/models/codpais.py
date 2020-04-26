# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models

class CodigoDianPais(models.Model):
    _name = 'res.country.dian'# aqui con la instruccion _inherit le decimos a odoo que en la tabla datos.per se hara una inclucion o herencia
    pais_code=fields.Char(string='Codigo pais Dian') # campo a incluir que es la cedula
    name=fields.Many2one('res.country',string='Pais')

class CodigoDianDep(models.Model):
    _name = 'res.departamento.dian'# aqui con la instruccion _inherit le decimos a odoo que en la tabla datos.per se hara una inclucion o herencia
    departamento_code=fields.Char(string='Codigo Departamento Dian') # campo a incluir que es la cedula
    departamento=fields.Many2one('res.country.state',string='Estado o Departamento')
    pais=fields.Many2one('res.country.dian',string='Pais')

class CodigoDianMun(models.Model):
    _name = 'res.municipio.dian'# aqui con la instruccion _inherit le decimos a odoo que en la tabla datos.per se hara una inclucion o herencia
    municipio_code=fields.Char(string='Codigo Municipio Dian') # campo a incluir que es la cedula
    name=fields.Char(string='Municipio')
    pais=fields.Many2one('res.country.dian',string='Pais')
    departamento=fields.Many2one('res.departamento.dian',string='Departamento')

class CodigoMunicipio(models.Model):
    _inherit = 'res.partner'

    municipio_id=fields.Many2one('res.municipio.dian',string='Municipio')
    departamento_id=fields.Many2one('res.country.state', string='Departamento')

        