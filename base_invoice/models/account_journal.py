# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountJournal(models.Model):
    _inherit = "account.journal"

    advance_type = fields.Selection([
        ('advance', 'Advance'),
        ('proof', 'Proof of Payment Received')
    ], string="Advance Type")