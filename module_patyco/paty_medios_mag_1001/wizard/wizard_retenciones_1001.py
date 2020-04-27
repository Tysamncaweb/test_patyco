# coding: utf-8
from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date
from odoo.exceptions import ValidationError
from io import BytesIO
import xlwt, base64
from decimal import *

################################################# AREA DEL WIZARD ############################
class WizardReport1008(models.TransientModel):
    _name = 'wizard.report.1001'
    _description = 'Wizard Reporte Nro 1001'

    date_start = fields.Date('Fecha Desde')
    date_end = fields.Date('Fecha Hasta') 
    concepto_id = fields.Many2one('account.conceptos', string='Conceptos',required=True)
    #id_account = fields.Many2one('account.account', string='Cuentas',#domain=[('deprecated', '=', False)], required=True)
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)# para el xls


    def print_1001_xls(self):

        #report_obj = self.env['report.paty_medios_mag_1008.reporte_templete_1008']
        datos_formato = self.get_datos_account_invoice(self.date_start, self.date_end, self.concepto_id)
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_formato_1001 = wb.add_sheet('Formato 1001')

         # formato del reporte
        title_format = xlwt.easyxf("font: name Tahoma size 14 px, bold 1;")
        sub_title_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")

        sub_title_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, height 170, bold 1;",
                                           num_format_str='#,##0.00')
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;",
                                         num_format_str='#,##0')

        row = 1
        col = 0
        # Lineas del Reporte###############################
        #row += 2
        #col = 1
        sheet_formato_1001.write_merge(row, row, 0, 0, "Concepto", sub_title_style) 
        sheet_formato_1001.write_merge(row, row, 1, 1, "Tipo de Documento", sub_title_style) 
        sheet_formato_1001.write_merge(row, row, 2, 2, "Número identificación del informado", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 3, 3, "Primer apellido del informado", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 4, 4, "Segundo apellido del informado", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 5, 5, "Primer nombre del informado", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 6, 6, "Otros nombres del informado", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 7, 7, "Razon social informado", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 8, 8, "Direccion", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 9, 9, "Código Departamento", sub_title_style)      
        sheet_formato_1001.write_merge(row, row, 10, 10, "Código Municipio", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 11, 11, "País de residencia o domicilio", sub_title_style)

        sheet_formato_1001.write_merge(row, row, 12, 12, "Pago o abono en cuenta deducible", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 13, 13, "Pago o abono en cuenta NO deducible", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 14, 14, "Iva mayor valor del costo o gasto deducible", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 15, 15, "Iva mayor valor del costo o gasto no deducible", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 16, 16, "Retención en la fuente practicada en renta", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 17, 17, "Retención en la fuente asumida en renta", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 18, 18, "Retención en la fuente practicada IVA régimen común", sub_title_style)
        sheet_formato_1001.write_merge(row, row, 19, 19, "Retención en la fuente practicada IVA no domiciliados", sub_title_style)
      
        for a in datos_formato:
            row += 1
            
            sheet_formato_1001.write_merge(row, row, 0, 0, a['concepto'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 1, 1, a['tipo_doc'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 2, 2, a['nro_identificacion'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 3, 3, a['last_name'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 4, 4, a['last_name2'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 5, 5, a['name'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 6, 6, a['name_two'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 7, 7, a['razon'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 8, 8, a['direccion'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 9, 9, a['cod_dep'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 10, 10, a['cod_mun'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 11, 11, a['cod_pais'], sub_title_style_bold)

            sheet_formato_1001.write_merge(row, row, 12, 12, a['pago_deducible'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 13, 13, a['pago_no_deducible'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 14, 14, a['iva_gasto_deducible'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 15, 15, a['iva_gasto_no_deducible'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 16, 16, a['retencion_p_renta'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 17, 17, a['retencion_a_renta'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 18, 18, a['retencion_p_comun'], sub_title_style_bold)
            sheet_formato_1001.write_merge(row, row, 19, 19, a['retencion_p_no_domici'], sub_title_style_bold)

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'formato_1001.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.report.1008',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }


      ##############################################################################################################

    def get_tipo_documento(self,doc_type):
        tipo_documento = ''
        #partner = partner_id

        if doc_type == 'civil_registration': # Registro civil de nacimiento
           tipo_documento = 11
        elif doc_type == 'id_card': # Tarjeta de identidad
            tipo_documento = 12
        elif doc_type == 'national_citizen_id': #Cédula de ciudadania
            tipo_documento = 13
        elif doc_type == 'id_document': #Tarjeta de extranjeria
            tipo_documento = 21
        elif doc_type == 'foreign_id_card': #cedula de extranjeria
            tipo_documento = 22
        elif doc_type == 'rut': #Nit
            tipo_documento= 31
        elif doc_type == 'passport': #pasaporte
            tipo_documento = 41
        elif doc_type == 'external_id': #tipo de documento extranjero
            tipo_documento = 42
        elif doc_type == 'residence_document': #Sin identificacion del exterior o para uso definido por la DIAN
            tipo_documento = 43
        tipo_documento=str(tipo_documento)
        return tipo_documento

    def cod_pais(self,pais_id):
    	pais_code=0
    	lista_pais=self.env['res.country.dian'].search([('name','=',pais_id)])
    	for det_pais in lista_pais:
    		pais_code=det_pais.pais_code
    	return pais_code

    def cod_departamento(self,departamento_id):
    	dep_code=0
    	lista_dep=self.env['res.departamento.dian'].search([('departamento','=',departamento_id)])
    	for det_dep in lista_dep:
    		dep_code=det_dep.departamento_code
    	return dep_code

    def concepto(self,id_account):
        lista_lineas=self.env['account.lines.medios.magneticos'].search([('account_src_id','=',id_account)])
        for det_lineas in lista_lineas:
            position_mag=det_lineas.position_mag_id.conceptos.cod
        return position_mag

    @api.multi
    def get_datos_account_invoice(self, date_start,date_end,concepto_id):
        vect=self.env['account.invoice'].search([('date_invoice','>=',date_start),('date_invoice','<=',date_end)])
        datos_formato = []
        for det in vect:
            #raise exceptions.UserError(('No ha iniciado sesion de cajero %s'),% concepto_id)
        	datos_formato.append({
                'concepto':self.concepto(det.account_id.id),
        		'tipo_doc':self.get_tipo_documento(det.partner_id.l10n_co_document_type),
        		'nro_identificacion':det.partner_id.vat,
        		'last_name':det.partner_id.last_name or "",
        		'last_name2':det.partner_id.last_name2 or "",
        		'name':det.partner_id.name or "",
        		'name_two':det.partner_id.name2 or "",
        		'razon':det.partner_id.name,
        		'direccion':det.partner_id.street,
        		'cod_dep':self.cod_departamento(det.partner_id.state_id.id) or "No asignado",
        		'cod_mun':det.partner_id.municipio_id.municipio_code or "No asignado",
        		'cod_pais':self.cod_pais(det.partner_id.country_id.id) or "No asignado",
        		'pago_deducible':det.amount_total,
        		'pago_no_deducible':"0",
        		'iva_gasto_deducible':det.amount_tax,
        		'iva_gasto_no_deducible':"0",
        		'retencion_p_renta':"0",
        		'retencion_a_renta':"0",
        		'retencion_p_comun':"0",
        		'retencion_p_no_domici':"0",
        		})
        return datos_formato