from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteForm(http.Controller):
    @http.route(['/tsi_iso_form'], type='http', auth="public", website=True)
    def appointment(self):
        # companies = request.env['res.partner'].sudo().search([('is_company', '=', True)])

        iso_standard    = request.env['tsi.iso.standard'].search([('standard','=', 'iso')])
        return request.render("v15_tsi.online_appointment_form",{
                'iso_standard': iso_standard,
                # 'iso_doctype': 'iso',
                # 'company_names': companies
            })
       
    @http.route(['/tsi_iso_form/submit'], type='http', auth="public", website=True)
    def submit(self, **post):
        company_name = post.get('company_name').strip()
        pic_name = post.get('contact_person').strip()
        std_iso = request.httprequest.form.getlist('iso_standardx')
         
        other_standard = post.get('other_standard')
        if other_standard:
            other_standard = other_standard.strip() 
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
            
        show_14001 = False
        show_45001 = False
        show_27001 = False
        show_haccp = False
        show_22000 = False
        show_salesinfo =False

        iso_standard_model = request.env['tsi.iso.standard'].sudo()
        
        for standard_id in std_iso:
            standard = iso_standard_model.browse(int(standard_id))
            
            if standard.name == "ISO 14001":
                show_14001 = True
            elif standard.name == "ISO 45001":
                show_45001 = True
            elif standard.name == "ISO 27001":
                show_27001 = True
            elif standard.name.upper() == "HACCP":
                show_haccp = True
            elif standard.name == "ISO 22000":
                show_22000 = True
            elif standard.name == "ISO 9001":
                show_salesinfo = True
        
        partner = request.env['res.partner'].sudo().search([('name', '=', company_name)], limit=1)
        if partner:
            _logger.error("Partner with name '%s' already exists, raising exception.", company_name)
        else:
            _logger.info("No existing partner found. Creating new one.")
            partner = request.env['res.partner'].sudo().create({
                'name': company_name,
                'company_type': 'company',
                'invoice_address': post.get('invoicing_address'),
                'office_address': post.get('office_address'),
                'phone': post.get('telepon'),
                'email': post.get('email'),
                'website': post.get('website'),
            })
            
        pic = request.env['res.partner'].sudo().search([('name', '=', pic_name)], limit=1)
        if pic:
            _logger.error("Partner with name '%s' already exists, raising exception.", pic_name)
        else:
            _logger.info("No existing partner found. Creating new one.")
            pic = request.env['res.partner'].sudo().create({
                'name': pic_name,
                'company_type': 'person'
            })
            
        types = request.httprequest.form.getlist('type[]')
        addresses = request.httprequest.form.getlist('address[]')
        products = request.httprequest.form.getlist('product[]')
        total_active_temps = request.httprequest.form.getlist('total_active_temporary[]')
        total_effective_emps = request.httprequest.form.getlist('total_effective_emp[]')
        permanents = request.httprequest.form.getlist('permanent[]')
        subcontractors = request.httprequest.form.getlist('subcontractor[]')
        others = request.httprequest.form.getlist('others[]')
        remarks = request.httprequest.form.getlist('remark[]')
        non_shifts = request.httprequest.form.getlist('non_shift[]')
        shift_1s = request.httprequest.form.getlist('shift_1[]')
        shift_2s = request.httprequest.form.getlist('shift_2[]')
        shift_3s = request.httprequest.form.getlist('shift_3[]')
        processes = request.httprequest.form.getlist('process[]')

        personnel_situations = []
        for i in range(len(types)):
            personnel_situations.append((0, 0, {
                'type': types[i] if i < len(types) else '',
                'address': addresses[i] if i < len(addresses) else '',
                'product': products[i] if i < len(products) else '',
                'total_active': total_active_temps[i] if i < len(total_active_temps) else 0,
                'total_emp': total_effective_emps[i] if i < len(total_effective_emps) else 0,
                'permanent': permanents[i] if i < len(permanents) else '',
                'subcon': subcontractors[i] if i < len(subcontractors) else '',
                'other': others[i] if i < len(others) else '',
                'remarks': remarks[i] if i < len(remarks) else '',
                'non_shift': non_shifts[i] if i < len(non_shifts) else '',
                'shift1': shift_1s[i] if i < len(shift_1s) else '',
                'shift2': shift_2s[i] if i < len(shift_2s) else '',
                'shift3': shift_3s[i] if i < len(shift_3s) else '',
                'differs': processes[i] if i < len(processes) else '',
            }))
            

        iso_form = request.env['tsi.iso'].sudo().create({
            'doctype': 'iso',
            'company_name': company_name,
            'invoicing_address': post.get('invoicing_address'),
            'pic_id': pic.id,
            'telepon': post.get('telepon'),
            'email': post.get('email'),
            'office_address': post.get('office_address'),
            'jabatan': post.get('jabatan'),
            'fax': post.get('fax'),
            'website': post.get('website'),
            'customer': partner.id,
            
            'scope': post.get('scope'),
            'boundaries': post.get('boundaries'),
            
            'iso_standard_ids': [(6, 0, [int(x) for x in std_iso])],
            'show_14001': show_14001,
            'show_45001': show_45001,
            'show_27001': show_27001,
            'show_haccp': show_haccp,
            'show_22000': show_22000,
            'show_salesinfo' : show_salesinfo,
            
            'certification': post.get('certification'),
            'tx_remarks': post.get('remarks'),
            'audit_stage': post.get('audit_stage'),
            'tx_site_count': post.get('number_of_site'),
            
            'partner_site': personnel_situations,
            'outsourced_activity': post.get('outsourced_activity'),
            
            'start_implement': post.get('start_of_implementation'),
            'mat_consultancy': post.get('use_of_consultants'),
            'txt_mat_consultancy': post.get('use_of_consultants_input'),
            'mat_certified': post.get('certified_system'),
            'txt_mat_certified': post.get('certified_system_input'),
            'other_system': post.get('other_system'),
            
            'integreted_audit': post.get('integrated_audit'),
            'int_planning': post.get('manual'),
            'int_policy': post.get('risk_opportunity_management'),
            'int_instruction': post.get('procedures'),
            'int_review': post.get('management_review'),
            'int_internal': post.get('internal_audit'),
            'int_system': post.get('responsibilities'),
            'int_improvement': post.get('work_instructions'),
        })

        return request.render("v15_tsi.online_appointment_form_success")
