from odoo import models, api, _
from odoo.exceptions import UserError

class ReportListadoComprobante(models.AbstractModel):
    _name = 'report.paty_listado_comprobante.template_listado_comprobante'

    @api.multi
    def _get_report_values(self,docids,data=None):

        if not docids:
            raise UserError("Debe seleccionar un registro")
        data = {'form': self.env['account.journal'].browse(docids)}
        res = dict()

        return {
            'data': data['form'],
            'model': self.env['report.paty_listado_comprobante.template_listado_comprobante'],
            'lines': res,
        }


    def consulta_diario_xls(self):
        vect=self.env['account.journal'].search([])
        datos_formato = []
        for lista_account in vect:
            datos_formato.append({
                'nombre':lista_account.name;
                })
        return datos_formato