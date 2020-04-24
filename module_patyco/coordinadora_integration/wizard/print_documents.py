# -*- coding: utf-8 -*-
from odoo import models, fields, api

class GetFile(models.TransientModel):

    _name = "save.file.wizard"
    file_name = fields.Char('File name', readonly=True)
    my_file = fields.Binary('File data', readonly=True, help = 'Archivo (jpg, csv, xls, exe, cualquier formato binario o de texto)')