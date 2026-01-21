# -*- coding: utf-8 -*-
# from odoo import http


# class MdaHr(http.Controller):
#     @http.route('/mda_hr/mda_hr', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mda_hr/mda_hr/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('mda_hr.listing', {
#             'root': '/mda_hr/mda_hr',
#             'objects': http.request.env['mda_hr.mda_hr'].search([]),
#         })

#     @http.route('/mda_hr/mda_hr/objects/<model("mda_hr.mda_hr"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mda_hr.object', {
#             'object': obj
#         })

