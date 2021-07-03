# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _

class ComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        res = super(ComposeMessage, self).action_send_mail()

        if 'proforma' in self._context:
            if self._context['proforma'] == True and self.model == 'sale.order':
                order = self.env['sale.order'].search([('id', '=', self.res_id)])
                order.sudo().write({'pro_forma_sent': True})

        return res

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_proof = fields.Boolean(string=_('Is Proof Of Payment'), default=False)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pro_forma_sent = fields.Boolean(string=_('Pro-Forma Sent'), readonly=True, tracking=True, copy=False)