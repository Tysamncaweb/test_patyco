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
    _name = 'wizard.report.1008'
    _description = 'Wizard Reporte comprobante 1008'

    date_start = fields.Date('Fecha Desde')
    date_end = fields.Date('Fecha Hasta') 
    formato_id = fields.Many2one('account.formatos', string='Formatos',required=True)
    #id_account = fields.Many2one('account.account', string='Cuentas',
        #domain=[('deprecated', '=', False)], required=True)
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)# para el xls


      ########################## FIN AREA DEL WIZARD #################################################

      ############################################## codigo para excel ####################################################  

    def print_1008_xls(self):

        #report_obj = self.env['report.paty_medios_mag_1008.reporte_templete_1008']
        datos_formato = self.get_datos_saldo_por_cobrar(self.date_start, self.date_end, self.formato_id)
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_formato_1008 = wb.add_sheet('Formato 1008')

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
        sheet_formato_1008.write_merge(row, row, 0, 0, "Descripcion", sub_title_style)
        sheet_formato_1008.write_merge(row, row, 1, 1, "Concepto", sub_title_style)    
        sheet_formato_1008.write_merge(row, row, 2, 2, "Tipo de Documento", sub_title_style)   
        sheet_formato_1008.write_merge(row, row, 3, 3, "Número de identificación deudor", sub_title_style)  
        sheet_formato_1008.write_merge(row, row, 4, 4, "Div", sub_title_style)  
        sheet_formato_1008.write_merge(row, row, 5, 5, "Primer apellido dudor", sub_title_style)
        sheet_formato_1008.write_merge(row, row, 6, 6, "Segundo apellido dudor", sub_title_style)
        sheet_formato_1008.write_merge(row, row, 7, 7, "Primer nombre dudor", sub_title_style)
        sheet_formato_1008.write_merge(row, row, 8, 8, "segundo nombre dudor", sub_title_style)  
        sheet_formato_1008.write_merge(row, row, 9, 9, "Razón Social deudor", sub_title_style)  
        sheet_formato_1008.write_merge(row, row, 10, 10, "Dirección", sub_title_style) 
        sheet_formato_1008.write_merge(row, row, 11, 11, "Código dpto.", sub_title_style) 
        sheet_formato_1008.write_merge(row, row, 12, 12, "Código mcp.", sub_title_style)   
        sheet_formato_1008.write_merge(row, row, 13, 13, "Páis de recidencia o domicilio.", sub_title_style) 
        sheet_formato_1008.write_merge(row, row, 14, 14, "Saldos cuentas por cobrar al 31-12.", sub_title_style) 


        for a in datos_formato:
            row += 1
            
            sheet_formato_1008.write_merge(row, row, 0, 0, a['descripcion'], sub_title_style_bold)
            sheet_formato_1008.write_merge(row, row, 1, 1, a['concepto'], sub_title_style_bold)  
            sheet_formato_1008.write_merge(row, row, 2, 2, a['tipodoc'], sub_title_style_bold)     
            sheet_formato_1008.write_merge(row, row, 3, 3, a['numiden'], sub_title_style_bold)   
            sheet_formato_1008.write_merge(row, row, 4, 4, a['div'], sub_title_style_bold)  
            sheet_formato_1008.write_merge(row, row, 5, 5, a['primerap'], sub_title_style_bold) 
            sheet_formato_1008.write_merge(row, row, 6, 6, a['segundoap'], sub_title_style_bold) 
            sheet_formato_1008.write_merge(row, row, 7, 7, a['primernom'], sub_title_style_bold) 
            sheet_formato_1008.write_merge(row, row, 8, 8, a['segundonom'], sub_title_style_bold)  
            sheet_formato_1008.write_merge(row, row, 9, 9, a['razonsocial'], sub_title_style_bold) 
            sheet_formato_1008.write_merge(row, row, 10, 10, a['direccion'], sub_title_style_bold) 
            sheet_formato_1008.write_merge(row, row, 11, 11, a['cod_dep'], sub_title_style_bold)  
            sheet_formato_1008.write_merge(row, row, 12, 12, a['cod_mcp'], sub_title_style_bold)
            sheet_formato_1008.write_merge(row, row, 13, 13, a['pais'], sub_title_style_bold) 
            sheet_formato_1008.write_merge(row, row, 14, 14, a['saldos'], sub_title_style_bold) 

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'formato_medios_mag_1008.xls'})

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

    @api.multi
    def get_datos_saldo_por_cobrar(self, date_start,date_end,formato_id):
        vect=self.env['account.move.line'].search([('date_maturity','>=',date_start),('date_maturity','<=',date_end)])
        datos_formato = []
        for det in vect:
            #account_det=self.env['']
            account_line=self.env['account.lines.medios.magneticos'].search([('account_src_id','=',det.account_id.id)])
            tipo_formato=account_line.position_mag_id.formatos.id # aqui busca el id del formato para compararlo luego
            tipo_movimiento=account_line.tipo_movimiento # aqui busca el tipo de movimiento si es NDC O NCD 
            
            if tipo_formato == formato_id.id:
                var_cedula=self.env['res.partner'].search([('id','=',det.partner_id.id)])
                doc_tipo=self.get_tipo_documento(var_cedula.l10n_co_document_type)
                dep_cod=self.env['res.departamento.dian'].search([('departamento','=',var_cedula.state_id.id)])
                mcp_cod=self.env['res.municipio.dian'].search([('id','=',var_cedula.municipio_id.id)])
                var_cod_pais=self.env['res.country.dian'].search([('name','=',det.partner_id.country_id.id)])
                saldo_credit=det.credit
                saldo_debit=det.debit
                if tipo_movimiento=='NDC':
                    saldo=(saldo_debit-saldo_credit)
                else:
                    saldo=(saldo_credit-saldo_debit)

                datos_formato.append({
                    'descripcion':det.name, 
                    'concepto':account_line.position_mag_id.conceptos.cod,  
                    'tipodoc':doc_tipo,   
                    'numiden':var_cedula.vat or "", 
                    'div':self.get_dv_code(var_cedula.vat) or "",  
                    'primerap':det.partner_id.last_name or "",
                    'segundoap':det.partner_id.last_name2 or "",
                    'primernom':det.partner_id.name or "",
                    'segundonom':det.partner_id.name2 or "",   
                    'razonsocial':det.partner_id.last_name or "", 
                    'direccion':var_cedula.street or "",
                    'cod_dep':dep_cod.departamento_code or "",
                    'cod_mcp':mcp_cod.municipio_code or "",
                    'pais':var_cod_pais.pais_code,
                    'saldos':saldo,
                    })
        return datos_formato

    def get_dv_code(self,vat):
        dv = 0
        if vat:
            factores = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
            rut_ajustado = str.rjust(str(vat), 15, '0')
            s = sum(int(rut_ajustado[14 - i]) * factores[i] for i in range(14)) % 11
            if s > 1:
                dv = 11 - s
            else:
                dv = s
            dv=str(dv)
        return dv
