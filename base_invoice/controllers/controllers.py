# -*- coding: utf-8 -*-
# from odoo import http


# class BaseInvoice(http.Controller):
#     @http.route('/base_invoice/base_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_invoice/base_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_invoice.listing', {
#             'root': '/base_invoice/base_invoice',
#             'objects': http.request.env['base_invoice.base_invoice'].search([]),
#         })

#     @http.route('/base_invoice/base_invoice/objects/<model("base_invoice.base_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_invoice.object', {
#             'object': obj
#         })
