# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResCompanyInit(models.Model):
    _inherit = 'res.company'

    vat_payer = fields.Boolean(related='partner_id.vat_payer', string=_("VAT payer"), readonly=False)
    vat = fields.Char(related='partner_id.vat', string=_("Tax ID"), readonly=False, help="IČ DPH")
    vat_id = fields.Char(related='partner_id.vat_id', string=_('Vat ID'), readonly=False, help="DIČ")
    company_registry = fields.Char(related='partner_id.company_registry', string=_('Company Registry'), readonly=False, help="IČO")
