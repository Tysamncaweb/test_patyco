# coding: utf-8 #
from odoo.osv import  osv
from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from datetime import datetime, date
from odoo.exceptions import ValidationError
from io import BytesIO
import xlwt, base64
from decimal import *

class WizardListadoMovimiento(models.TransientModel):
    _name = 'wizard.listado.movimiento'
    _description = "Wizard Listado de Movimiento por Comprobante y Fecha"

    date_start = fields.Date("Fecha desde")
    date_end = fields.Date("Fecha hasta")
    comprobante = fields.Many2one('account.journal', string="Comprobante")
    type_report = fields.Selection(selection=[('fecha','Fecha'),
                                              ('comprobante','Comprobante')],
                                   required=True,
                                   default='fecha',
                                   help="Selccione el tipo de filetro para el reporte")
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)# para el xls


    def print_listado_movimiento_pdf(self):
        datas = []
        ids = []
        data = {
            'ids': ids,
            'model':'report.paty_listado_movimiento_comp.template_listado_mov_id',
            'form':{
                'date_start':self.date_start,
                'date_end': self.date_end,
                'comprobante': self.comprobante.id,
                'type_report': self.type_report
                },

        }
        return self.env.ref('paty_listado_movimiento_comp.action_template_listado_mov').report_action(self, data=data,config=False)

    def print_analitico_xls(self):

        report_obj = self.env['report.paty_listado_movimiento_comp.template_listado_mov_id']
        datos_formato = report_obj.get_datos_por_comprobante_xls(self.date_start, self.date_end, self.type_report,self.comprobante)
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_formato_comprobante = wb.add_sheet('Mov. por Comprobante')

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
        sheet_formato_comprobante.write_merge(row, row, 0, 0, "Fecha", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 1, 1, "Nro Registro", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 2, 2, "Cuenta", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 3, 3, "Comprobante", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 4, 4, "Documento", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 5, 5, "Docto. Referencia", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 6, 6, "Detalle", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 7, 7, "Id", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 8, 8, "Nit", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 9, 9, "Valor", sub_title_style)
        sheet_formato_comprobante.write_merge(row, row, 10, 10, "Valor Base", sub_title_style)       

        for a in datos_formato:
            row += 1
            
            sheet_formato_comprobante.write_merge(row, row, 0, 0, str(a['fecha']), sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 1, 1, a['nro_registro'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 2, 2, a['cuenta'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 3, 3, a['comprobante'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 4, 4, a['documento'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 5, 5, a['doc_ref'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 6, 6, a['detalle'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 7, 7, a['id'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 8, 8, a['nit'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 9, 9, a['valor'], sub_title_style_bold)
            sheet_formato_comprobante.write_merge(row, row, 10, 10, a['Valor_Base'], sub_title_style_bold)
            
        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'Reporte_mov_comprobante.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.listado.movimiento',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

class Reportlistadomovimiento(models.AbstractModel):
    _name = 'report.paty_listado_movimiento_comp.template_listado_mov_id'

    @api.multi
    def _get_report_values(self,docids,data=None):

        ids = data['ids']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        comprobante = data['form']['comprobante']
        type_report = data['form']['type_report']



        res_all_comprobante, res_all_fecha = self.get_datos_por_comprobante(date_start,date_end,type_report,comprobante)

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'comprobante': comprobante,
            'type_report': type_report,
            'datos': res_all_comprobante,
            'datos_fecha': res_all_fecha
        }

    @api.multi
    def get_datos_por_comprobante(self,date_start, date_end, type_report, comprobante):
        res_all_comprobantes = []

        if type_report == 'comprobante':
            self.env.cr.execute('''SELECT j.correlativo, j.name AS Nombre, m.name AS Nro_Registro, a.code AS Cuenta, l.date AS Fecha, m.name AS Documento,
                    m.ref AS Docto_Referencia, l.name, debit, credit, p.vat AS NIT, 0 AS Valor_Base
                    FROM public.account_move_line l
                        LEFT JOIN public.account_journal j ON (l.journal_id=j.id)
                        LEFT JOIN public.account_account a ON (l.account_id=a.id)
                        LEFT JOIN public.res_partner p ON (l.partner_id=p.id)
                        LEFT JOIN public.account_move m ON (l.move_id=m.id)
                    WHERE l.journal_id = %s
                    GROUP BY m.id,j.correlativo,j.name,a.code,l.date,l.ref,l.name,debit, credit, p.vat;''',(comprobante,))

            res_all_comprobantes = self.env.cr.fetchall()

        else:

            sql_fecha = '''SELECT l.date AS Fecha, m.name AS Nro_Registro, a.code AS Cuenta, j.correlativo, 
                                    m.name AS Documento,m.ref AS Docto_Referencia,l.name AS Detalle, debit, credit, p.vat AS NIT, 0 AS Valor_Base
                        FROM public.account_move_line l
                            LEFT JOIN public.account_journal j ON (l.journal_id=j.id)
                            LEFT JOIN public.account_account a ON (l.account_id=a.id)
                            LEFT JOIN public.res_partner p ON (l.partner_id=p.id)
                            LEFT JOIN public.account_move m ON (l.move_id=m.id)
                        WHERE (l.date >= %s and l.date <= %s)
                        GROUP BY m.id,j.correlativo,j.name,a.code,l.date,l.ref,l.name,debit, credit, p.vat;'''
            fechas = (date_start,date_end)
            self.env.cr.execute(sql_fecha,fechas)
            res_all_fecha = self.env.cr.fetchall()

        return res_all_comprobantes, res_all_fecha

    def get_datos_por_comprobante_xls(self,date_start, date_end, type_report, comprobante):
    	if type_report=="fecha":
    		vect=self.env['account.move.line'].search([('date','>=',date_start),('date','<=',date_end)])
    	if type_report=="comprobante":
    		vect=self.env['account.move.line'].search([('journal_id','=',comprobante.id)])
    	datos_formato = []
    	for det in vect:
    		#fecha=str.(det.date)
    		lista_cuenta=self.env['account.account'].search([('id','=',det.account_id.id)])
    		lista_account_move=self.env['account.move'].search([('id','=',det.move_id.id)])
    		#lista_partner=self.env['res.partner'].search([('id','=',det.partner_id.id)])
    		aux=det.credit
    		if aux==0:
    			tipo_bal="Db"
    			valores=det.debit
    		else:
    			tipo_bal="Cd"
    			valores=det.credit
    		datos_formato.append({
    			'fecha':det.date,
    			'nro_registro':lista_account_move.name,
    			'cuenta':lista_cuenta.code,
    			'comprobante':det.journal_id.correlativo,
    			'documento':lista_account_move.name or "",
    			'doc_ref':det.ref or "",
    			'detalle':det.name,
    			'id':tipo_bal,
    			'nit':det.partner_id.vat,
    			'valor':valores,
    			'Valor_Base':"0",
    			})
    	return datos_formato
    	doc_ref