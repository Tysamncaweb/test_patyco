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


class WizardReport1007(models.TransientModel): # aqui declaro las variables del wizar que se usaran para el filtro del pdf
    _name = 'wizard.report.1007'
    _description = "Wizard Report Comprobante 1007"

    date_start = fields.Date('Fecha Desde')
    date_end = fields.Date('Fecha Hasta')    
    #concepto=fields.Many2one('account.conceptos',string='Concepto')  
    formato=fields.Many2one('account.formatos',string='Formatos') 
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)# para el xls

    def print_1007_pdf(self):

        datas = []
        ids = []
        data = {
            'ids': ids,
            'model': 'paty_medios_mag_1007.reporte_templete_1007',  # id del templete del archivo para el pdf, aqui paso las variables al xml
            'form': {
                'datas': datas,
                'date_start': self.date_start,
                'date_end': self.date_end,
                'date_formato': self.formato,                
                },
        }
        return self.env.ref('paty_medios_mag_1007.action_report_pdf_1007').report_action(docids=ids, data=data, config=False)# llama a la accion del boton pdf
    
       ############################################## codigo para excel ####################################################  

    def print_1007_xls(self):

        report_obj = self.env['report.paty_medios_mag_1007.reporte_templete_1007']
        datos_formato = report_obj.get_datos_por_comprobante_xls(self.date_start, self.date_end)
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_formato_1007 = wb.add_sheet('Formato 1007')

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
        sheet_formato_1007.write_merge(row, row, 0, 0, "concepto", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 1, 1, "Tipo de Documento", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 2, 2, "Nro Identificación del informado", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 3, 3, "Primer apellido del informado", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 4, 4, "Segundo apellido del informado", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 5, 5, "Primer nombre del informado", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 6, 6, "segundo nombre del informado", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 7, 7, "Razón social del informado", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 8, 8, "Pais de residencia o domicilio", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 9, 9, "Ingresos brutos recibidos", sub_title_style)
        sheet_formato_1007.write_merge(row, row, 10, 10, "(Total) Devoluciones, rebajas y descuentos", sub_title_style)

        for a in datos_formato:
            row += 1
            
            sheet_formato_1007.write_merge(row, row, 0, 0, a['concepto'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 1, 1, a['tipodoc'], line_content_style)
            sheet_formato_1007.write_merge(row, row, 2, 2, a['numiden'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 3, 3, a['primerap'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 4, 4, a['segundoap'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 5, 5, a['primernom'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 6, 6, a['segundonom'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 7, 7, a['razonsocial'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 8, 8, a['pais'], sub_title_style_bold)
            sheet_formato_1007.write_merge(row, row, 9, 9, a['ingresosbrutos'], sub_title_style_bold)  
            sheet_formato_1007.write_merge(row, row, 10, 10, a['devoluciones'], sub_title_style_bold)  

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'formato_medios_mag_1007.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.report.1007',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }


      ##############################################################################################################  
class ReportComprobante1007(models.AbstractModel):
    _name = 'report.paty_medios_mag_1007.reporte_templete_1007'

    @api.multi
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        res_all_comprobante = self.get_datos_por_comprobante(date_start, date_end)
        #----------------------
        lis = []
        lis_concepto = []
        lis_vat = []
        lis_dev_desc = []
        lis_tipo_doc =[]
        for comp in res_all_comprobante:
            var=self.env['res.country.dian'].search([('name','=',comp.partner_id.country_id.id)])            
            lis.append(var.pais_code)# append sirve para incluir datos en la lista

            var_line=self.env['account.lines.medios.magneticos'].search([('account_src_id','=',comp.account_id.id)])
            lis_concepto.append(var_line.position_mag_id.conceptos.name)# append sirve para incluir datos en la lista

            var_vat=self.env['res.partner'].search([('id','=',comp.partner_id.id)])
            lis_vat.append(var_vat.vat)
            lis_tipo_doc.append(self.get_tipo_documento(var_vat.l10n_co_document_type)) 
                      
            lis_dev_desc.append(self.get_dev_desc(comp.id))

            
        #-------------------------
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            #'type_report': type_report,
            'datos': res_all_comprobante,
            'pais_code':lis,
            'conceptos':lis_concepto,
            'cedula':lis_vat,
            'descuento':lis_dev_desc,
            'tipodocumento':lis_tipo_doc
        }

    @api.multi  # una funcion propia de odoo
    def get_datos_por_comprobante(self,date_start, date_end):
       var=self.env['account.invoice'].search([('type','in',('out_invoice','out_refund')),('state','=','open'),('date_invoice','>=',date_start),('date_invoice','<=',date_end)])
       return var

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

    def get_dev_desc(self,account_line):
        acom=0
        var_dev=self.env['account.invoice.line'].search([('invoice_id','=',account_line)])
        for vec in var_dev:
            acom=acom+vec.price_subtotal
        acom =round(acom,2)
        return acom
        #return var_dev.price_subtotal
        #return account_line

    def get_datos_por_comprobante_xls(self,date_start, date_end):
        vect=self.env['account.invoice'].search([('type','in',('out_invoice','out_refund')),('state','=','open'),('date_invoice','>=',date_start),('date_invoice','<=',date_end)])
        datos_formato = []
        for det in vect:
            account_line=self.env['account.lines.medios.magneticos'].search([('account_src_id','=',det.account_id.id)])
            var_cedula=self.env['res.partner'].search([('id','=',det.partner_id.id)])
            var_cod_pais=self.env['res.country.dian'].search([('name','=',det.partner_id.country_id.id)]) 
            var_descuento=self.get_dev_desc(det.id) 
            doc_tipo=self.get_tipo_documento(var_cedula.l10n_co_document_type)           

            datos_formato.append({
                'ingresosbrutos':det.amount_untaxed_signed, 
                'concepto':account_line.position_mag_id.conceptos.cod,
                'tipodoc':var_cedula.vat or "",
                'numiden':doc_tipo,
                'primerap':det.partner_id.last_name or "",
                'segundoap':det.partner_id.last_name2 or "",
                'primernom':det.partner_id.name or "",
                'segundonom':det.partner_id.name2 or "",
                'razonsocial':det.partner_id.last_name or "",
                'pais':var_cod_pais.pais_code,
                'devoluciones':var_descuento, 

                })

        return datos_formato