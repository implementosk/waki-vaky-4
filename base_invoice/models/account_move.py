# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _get_default_delivery_date(self):
        return fields.Date.today() if self._context.get('default_type', 'entry') in (
            'in_invoice', 'in_refund', 'in_receipt') else False

    advance_invoice = fields.Boolean(string="Advance Invoice", readonly=True)
    order_advance_id = fields.Many2one('sale.order', string="Advance From Order", readonly=True)
    proof_invoice = fields.Boolean(string="Proof of Payment", readonly=True)
    proof_invoice_ids = fields.Many2many('account.move', string="Proof Invoices", readonly=True, relation='advance_proof_ids', column1='advance_id', column2='proof_id')
    advance_invoice_id = fields.Many2one('account.move', string="Advance Invoice", readonly=True)
    account_delivery_date = fields.Date(string=_('Delivery Date'), default=_get_default_delivery_date)

    def post(self):
        res = super(AccountMove, self).post()

        for move in self:
            if not move.account_delivery_date and move.is_invoice(include_receipts=True):
                move.account_delivery_date = fields.Date.context_today(self)
            if move.proof_invoice and move.advance_invoice_id:
                move.advance_invoice_id.proof_invoice_ids = [(4, move.id)]
            if move.proof_invoice and move.order_advance_id:
                for line in move.order_advance_id.order_line:
                    if line.is_downpayment:
                        if move.id in line.invoice_lines.move_id.proof_invoice_ids.ids:
                            line.order_id.state = 'sale'
                            line.is_proof = True
                            line.price_unit = 0
                            for proof in line.invoice_lines.move_id.proof_invoice_ids:
                                line.price_unit += proof.invoice_line_ids[0].price_unit
                            line.tax_id = self.env['account.tax'].sudo().search(
                                [('type_tax_use', '=', 'sale'), ('amount', '=', '20.0')], limit=1)

        return res
