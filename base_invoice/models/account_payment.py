# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    from_advance_invoice = fields.Boolean(string="From Advance Invoice", readonly=True)
    advance_invoice_id = fields.Many2one('account.move', string="Advance Invoice", readonly=True)
    proof_invoice_id = fields.Many2one('account.move', string="Proof Invoice", readonly=True)

    @api.model
    def default_get(self, default_fields):
        rec = super(AccountPayment, self).default_get(default_fields)
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        if not active_ids or active_model != 'account.move':
            return rec

        invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))

        # Check all invoices are open
        if not invoices or any(invoice.state != 'posted' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        # Check if, in batch payments, there are not negative invoices and positive invoices
        dtype = invoices[0].type
        for inv in invoices[1:]:
            if inv.type != dtype:
                if ((dtype == 'in_refund' and inv.type == 'in_invoice') or
                        (dtype == 'in_invoice' and inv.type == 'in_refund')):
                    raise UserError(_("You cannot register payments for vendor bills and supplier refunds at the same time."))
                if ((dtype == 'out_refund' and inv.type == 'out_invoice') or
                        (dtype == 'out_invoice' and inv.type == 'out_refund')):
                    raise UserError(_("You cannot register payments for customer invoices and credit notes at the same time."))

        rec.update({
            'from_advance_invoice': invoices[0].advance_invoice,
            'advance_invoice_id': invoices[0].id
        })
        return rec

    def button_proof(self):
        self.ensure_one()
        invoice_vals = self._prepare_proof_values(self.advance_invoice_id)
        proof_move = self.env['account.move'].sudo().create(invoice_vals).with_user(self.env.uid)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'target': 'current',
            'res_id': proof_move.id,
            'context': {'form_view_initial_mode': 'edit', 'force_detailed_view': 'true'},
        }

    def _prepare_proof_values(self, move):
        proof_journal = self.env['account.journal'].sudo().search([('advance_type', '=', 'proof')], limit=1)
        tax_ids = self.env['account.tax'].sudo().search([('type_tax_use', '=', 'sale'), ('amount', '=', '20.0')], limit=1)

        invoice_vals = {
            'order_advance_id': move.order_advance_id,
            'journal_id': proof_journal.id,
            'advance_invoice_id': move.id,
            'proof_invoice': True,
            'invoice_date': move.invoice_date,
            'account_delivery_date': move.account_delivery_date,
            'invoice_payment_term_id': move.invoice_payment_term_id.id,
            'invoice_date_due': move.invoice_date_due,
            'invoice_incoterm_id': move.invoice_incoterm_id.id,
            'invoice_cash_rounding_id': move.invoice_cash_rounding_id.id,
            'type': 'out_invoice',
            'invoice_origin': move.name,
            'invoice_user_id': move.user_id.id,
            'narration': move.narration,
            'partner_id': move.partner_id.id,
            'fiscal_position_id': move.fiscal_position_id.id,
            'partner_shipping_id': move.partner_shipping_id.id,
            'currency_id': move.currency_id.id,
            'invoice_payment_ref': move.invoice_payment_ref,
            'invoice_payment_term_id': move.invoice_payment_term_id.id,
            'invoice_partner_bank_id': move.invoice_partner_bank_id.id,
            'team_id': move.team_id.id,
            'campaign_id': move.campaign_id.id,
            'medium_id': move.medium_id.id,
            'source_id': move.source_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': line.name,
                'price_unit': self.amount / 1.2,
                'discount': line.discount,
                'quantity': 1.0,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'product_uom_id': line.product_uom_id.id,
                'tax_ids': [(6, 0, tax_ids.ids)],
                'analytic_tag_ids': [(6, 0, line.analytic_tag_ids.ids)],
                'analytic_account_id': line.analytic_account_id.id or False,
            }) for line in move.invoice_line_ids],
        }

        return invoice_vals