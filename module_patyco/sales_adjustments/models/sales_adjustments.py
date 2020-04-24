# -*- coding: utf-8 -*-

from odoo import models, fields, api

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

class FormatAddressMixin(models.Model):
    _inherit = "res.partner"
    _description = 'sales_adjustments'

    RUT = fields.Char(domain=[('l10n_co_document_type', '=', 'rut')])
    street_rut = fields.Char()
    street2_rut = fields.Char()
    zip_rut = fields.Char(change_default=True)
    city_rut = fields.Char()
    state_id_rut = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id_rut = fields.Many2one('res.country', string='Country', ondelete='restrict')
    l10n_co_document_type = fields.Selection([('rut', 'RUT'),
                                              ('id_document', 'Cédula'),
                                              ('id_card', 'Tarjeta de Identidad'),
                                              ('passport', 'Pasaporte'),
                                              ('foreign_id_card', 'Cédula Extranjera'),
                                              ('external_id', 'ID del Exterior'),
                                              ('diplomatic_card', 'Carné Diplomatico'),
                                              ('residence_document', 'Salvoconducto de Permanencia'),
                                              ('civil_registration', 'Registro Civil'),
                                              ('national_citizen_id', 'Cédula de ciudadanía')], string='Document Type',
                                             help='Indicates to what document the information in here belongs to.')
    l10n_co_verification_code = fields.Char(compute='_compute_verification_code', string='VC',
                                            # todo remove this field in master
                                            help='Redundancy check to verify the vat number has been typed in correctly.')




class AccountInvoice (models.Model):
    _inherit = "account.invoice"




    total_discount =fields.Monetary(string='Discount Amount', store=True, readonly=True, compute='_total_amount')
    amount_undiscounted = fields.Float('Amount Before Discount', compute='_compute_amount_undiscounted', digits=0)
    amount_total_ = fields.Monetary(string='Total Cliente - Proveedor',store=True, readonly=True, compute='_compute_amount_' )

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount_(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total_ = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total_
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id
            amount_total_company_signed = currency_id._convert(self.amount_total_, self.company_id.currency_id,
                                                               self.company_id,
                                                               self.date_invoice or fields.Date.today())
            amount_untaxed_signed = currency_id._convert(self.amount_untaxed, self.company_id.currency_id,
                                                         self.company_id, self.date_invoice or fields.Date.today())
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed
        self.amount_total_signed = self.amount_total_
        self.amount_untaxed_signed = amount_untaxed_signed


    @api.one
    def _compute_amount_undiscounted(self):
        total = 0.0
        for line in self.invoice_line_ids:
            total += line.price_subtotal + line.price_unit * ((line.discount or 0.0) / 100.0) * line.quantity  # why is there a discount in a field named amount_undiscounted ??
        self.amount_undiscounted = total

    @api.one
    @api.depends('invoice_line_ids')
    def _total_amount(self):
         for line in self:
             total_discount_prueba = 0.0
             for line in self.invoice_line_ids:
                    total_discount_prueba += line.discount
             total_discount = (self.amount_undiscounted * total_discount_prueba) / 100
             self.update({
                    'total_discount': total_discount,
             })


class IrSequence(models.Model):

    _inherit = 'ir.sequence'

    dian_type = fields.Char('Formulario DIAN No.', size=14)
    dian_range_hasta = fields.Char(size=14)


class IrSequenceDateRange(models.Model):



        _inherit= 'ir.sequence.date_range'

        dian_range_hasta = fields.Char (size=14)
        #dian_range_inicial = fields.Char (size=14)




class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'





    discount = fields.Float('Descuento en %', readonly=True)
    price_unit_tax = fields.Monetary(string='Cantidad del Impuesto', store=True)
    amount_total_ = fields.Monetary(string='Total Cliente - Proveedor', store=True)





    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """, sub.discount as discount,
        sub.price_unit_tax as price_unit_tax , sub.amount_total_ as amount_total_""" #", sub.discount as discount"


    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + """, ail.discount as discount, ail.price_unit_tax as price_unit_tax , ai.amount_total_ as amount_total_"""
        # ", ail.discount as discount"


    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + """, ail.discount, ail.price_unit_tax, ai.amount_total_""" #",ail.discount"


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    price_unit_tax = fields.Monetary(string='Tax Amount', store=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True)

    @api.onchange('price_subtotal')
    def __onchange_price_tax_(self):
        for l in self:
            self.price_unit_tax = l.price_total - l.price_subtotal

        return












