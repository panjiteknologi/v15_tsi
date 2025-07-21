from odoo import http
from datetime import datetime
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteForm(http.Controller):
    @http.route(['/crm_survey_form'], type='http', auth="public", website=True)
    def appointment(self):

        iso_standard = request.env['tsi.iso.standard'].search([('standard', 'in', ['iso', 'ispo'])])
        return request.render("v15_tsi.survey_form",{
                'iso_standard': iso_standard,
            })
       
    @http.route(['/crm_survey_form/submit'], type='http', auth="public", website=True)
    def submit(self, **post):
        
        std_iso = request.httprequest.form.getlist('iso_standardx')
        other_standard = post.get('other_standard', "").strip()
        
        if other_standard:
            other_standards = request.env['tsi.iso.standard'].sudo().search([('name', '=', other_standard)], limit=1)
            if other_standards:
                _logger.error("Standard with name '%s' already exists, raising exception.", other_standard)
            else:
                _logger.info("No existing standard found. Creating new one.")
                other_standards = request.env['tsi.iso.standard'].sudo().create({
                    'name': other_standard,
                    'standard': 'iso'
                })
                std_iso.append(str(other_standards.id))

        # partner_name = post.get('partner_id')
        # partner = request.env['res.partner'].sudo().search([('name', '=', partner_name)], limit=1)

        # if not partner:
        #     partner = request.env['res.partner'].sudo().create({
        #         'name': partner_name,
        #     })

        survey_form = request.env['crm.customer.survey'].sudo().create({
            # 'partner_id': partner.id,
            'company' : post.get('company'),
            'nama' : post.get('nama'),
            'jabatan': post.get('jabatan'),
            'email': post.get('email'),
            'no_telp': post.get('no_telp'),
            'iso_standard_ids': [(6, 0, [int(x) for x in std_iso])],
            'tanggal_audit': post.get('tanggal_audit'),
            'tanggal_input': datetime.now().date(),
            'tahap_audit': post.get('tahap_audit'),
            'question_1': post.get('question_1'),
            'saran_1': post.get('saran_1'),
            'question_2': post.get('question_2'),
            'saran_2': post.get('saran_2'),
            'star_auditor1': post.get('star_auditor1'),
            'nama_auditor1': post.get('nama_auditor1'),
            'star_auditor2': post.get('star_auditor2'),
            'nama_auditor2': post.get('nama_auditor2'),
            'star_auditor3': post.get('star_auditor3'),
            'nama_auditor3': post.get('nama_auditor3'),
            'star_auditor4': post.get('star_auditor4'),
            'nama_auditor4': post.get('nama_auditor4'),
            'question_3': post.get('question_3'),
            'saran_3': post.get('saran_3'),
            'question_4': post.get('question_4'),
            'saran_4': post.get('saran_4'),
            'question_5': post.get('question_5'),
            'score': post.get('score'),
            'saran_5': post.get('saran_5'),
        })

        return request.render("v15_tsi.survey_form_success")