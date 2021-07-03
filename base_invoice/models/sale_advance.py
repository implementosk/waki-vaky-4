# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _get_advance_details(self, order):
        if self.advance_payment_method == 'percentage':
            amount = order.amount_total * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount
            name = _('Down Payment')

        return amount, name

    def _prepare_invoice_values(self, order, name, amount, so_line):
        invoice_vals = super()._prepare_invoice_values(order, name, amount, so_line)

        advance_journal = self.env['account.journal'].sudo().search([('advance_type', '=', 'advance')], limit=1)
        invoice_vals['journal_id'] = advance_journal.id
        invoice_vals['advance_invoice'] = True
        invoice_vals['order_advance_id'] = order.id

        return invoice_vals