# coding: utf-8 #

from odoo import models, fields, api
from io import BytesIO
import xlwt, base64


class WizardFormato1005(models.TransientModel):
    _name = 'wizard.formato.1005'
    _description = "Wizard Formato Medios Magneticos"

    date_start = fields.Date("Fecha desde")
    date_end = fields.Date("Fecha hasta")
    report = fields.Binary('Descargar xls', filters='.xls', readonly=True)
    name = fields.Char('File Name', size=32)
    #cuenta_contable = fields.Many2one('account.account')

    def print_1005_xls(self):

        datos_formato = self.get_datos_por_comprobante(self.date_start, self.date_end)
        fp = BytesIO()
        wb = xlwt.Workbook(encoding='utf-8')
        sheet_formato_1005 = wb.add_sheet('Formato 1005')

        # formato del reporte
        title_format = xlwt.easyxf("font: name Tahoma size 14 px, bold 1;")
        sub_title_style = xlwt.easyxf(
            "font: name Helvetica size 10 px, bold 1, height 170; borders: left thin, right thin, top thin, bottom thin;")

        sub_title_style_bold = xlwt.easyxf("font: name Helvetica size 10 px, height 170, bold 1;",
                                           num_format_str='#,##0.00')
        line_content_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;",
                                         num_format_str='#,##0')
        line_content_amount_style = xlwt.easyxf("font: name Helvetica, height 170; align: horiz right;",
                                         num_format_str='#,##0.00')
        row = 1
        col = 0
        # Lineas del Reporte###############################
        row += 2
        col = 1
        sheet_formato_1005.write_merge(row, row, 0, 0, "Tipo de Documento", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 1, 1, "Nro Identificación del informado", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 2, 2, "DV" , sub_title_style)
        sheet_formato_1005.write_merge(row, row, 3, 3, "Primer apellido del informado", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 4, 4, "Segundo apellido del informado", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 5, 5, "Primer nombre del informado", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 6, 6, "segundo nombre del informado", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 7, 7, "Razón social del informado", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 8, 8, "Impuesto descontable", sub_title_style)
        sheet_formato_1005.write_merge(row, row, 9, 9, "IVA resultante por devoluciones en ventas anuladas, rescindidas o resueltas", sub_title_style)
        for a in datos_formato:
            row += 1
            sheet_formato_1005.write_merge(row, row, 0, 0, a['tipodoc'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 1, 1, a['numiden'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 2, 2, a['dv'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 3, 3, a['primerap'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 4, 4, a['segundoap'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 5, 5, a['primernom'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 6, 6, a['segundonom'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 7, 7, a['razonsocial'], line_content_style)
            sheet_formato_1005.write_merge(row, row, 8, 8, a['impuestodescontable'], line_content_amount_style)
            sheet_formato_1005.write_merge(row, row, 9, 9, a['iva_resultante'], line_content_amount_style)

        wb.save(fp)

        out = base64.encodestring(fp.getvalue())
        self.write({'state': 'get', 'report': out, 'name': 'formato_medios_mag_1005.xls'})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.formato.1005',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
    def get_cuentas_contables(self):
        lista_cuentas = []
        iva_descontable_lineas = self.env['account.config.formato.1005.lines'].search([])

        for linea in iva_descontable_lineas:
            lista_cuentas.append(linea.account_src_id.id)

        return lista_cuentas

    def get_datos_por_comprobante(self,date_start, date_end):

        lista_cuentas_iva_descontable = self.get_cuentas_contables()

        lista_position = []
        datos_formato = []
        lista_move_line = self.env['account.move.line'].search([
                                                ('date','>=',date_start),
                                                ('date','<=',date_end),
                                                ('account_id','in',lista_cuentas_iva_descontable)])
        if lista_move_line:
            for move_line in lista_move_line:
                lista_move = self.env['account.move'].search([('id','=', move_line.move_id.id),
                                                              ('state','=','posted')])
                for move in lista_move:
                    tipo_movimiento = self.env['account.config.formato.1005.lines'].search([('account_src_id','=',move_line.account_id.id)])

                    tipo_iva = self.env['account.config.formato.1005'].search([('id','=',tipo_movimiento.config_id.id)])
                    iva_desc = tipo_iva.tipo_iva

                    if iva_desc == 'iva_descontable':
                        var = move_line.balance
                        var2 = 0
                    else:
                        var2 = move_line.balance #self.get_iva_por_devoluciones(move)
                        var = 0
                    if move.partner_id.company_type == 'person':
                        datos_formato.append({
                        'tipodoc': self.get_tipo_documento(move.partner_id),
                        'numiden': move.partner_id.vat,
                        'dv': self.get_dv_code(move.partner_id.vat),
                        'primerap': move.partner_id.last_name or "",
                        'segundoap' : move.partner_id.last_name2 or "",
                        'primernom' : move.partner_id.name or "",
                        'segundonom' : move.partner_id.name2 or "",
                        'razonsocial' : "",
                        'impuestodescontable' : var,
                        'iva_resultante' : var2,
                        })
                    else:
                        datos_formato.append({
                            'tipodoc': self.get_tipo_documento(move.partner_id),
                            'numiden': move.partner_id.vat,
                            'dv': self.get_dv_code(move.partner_id.vat),
                            'primerap': "",
                            'segundoap': "",
                            'primernom': "",
                            'segundonom': "",
                            'razonsocial': move.partner_id.name or "",
                            'impuestodescontable' : var,
                            'iva_resultante' : var2,
                        })

        return datos_formato

    def get_tipo_documento(self,partner_id):
        tipo_documento = ''
        partner = partner_id

        if partner.l10n_co_document_type == 'civil_registration': # Registro civil de nacimiento
           tipo_documento = 11
        elif partner.l10n_co_document_type == 'id_card': # Tarjeta de identidad
            tipo_documento = 12
        elif partner.l10n_co_document_type == 'national_citizen_id': #Cédula de ciudadania
            tipo_documento = 13
        elif partner.l10n_co_document_type == 'id_document': #Tarjeta de extranjeria
            tipo_documento = 21
        elif partner.l10n_co_document_type == 'foreign_id_card': #cedula de extranjeria
            tipo_documento = 22
        elif partner.l10n_co_document_type == 'rut': #Nit
            tipo_documento= 31
        elif partner.l10n_co_document_type == 'passport': #pasaporte
            tipo_documento = 41
        elif partner.l10n_co_document_type == 'external_id': #tipo de documento extranjero
            tipo_documento = 42
        elif partner.l10n_co_document_type == 'residence_document': #Sin identificacion del exterior o para uso definido por la DIAN
            tipo_documento = 43

        return tipo_documento

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
        return dv

    def get_cod_pais(self,partner_id):
        var = self.env['res.country.dian'].search([('name','=',partner_id.country_id.id)])
        return var.pais_code

    def get_iva_por_devoluciones(self,move):

        obj_iva_devolucion = self.env['account.invoice'].search([
            ('move_id', '=', move.id),
            ('type', '=', 'out_refund')])

        return obj_iva_devolucion.amount_tax