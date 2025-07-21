from odoo import models, fields, api, _
import odoo
from odoo.http import request

from datetime import datetime,date,timedelta

import logging
_logger = logging.getLogger(__name__)

class OWS(models.Model):
    _name           = "tsi.ows"
    _description    = "OWS"
    _order          = 'id DESC'
    _inherit        = ["mail.thread", "mail.activity.mixin"]
    
    nama_client     = fields.Many2one('res.partner',string='Client Name',readonly=True)
    no_sertifikat   = fields.Char(string='No. Certificate',readonly=True)
    scope           = fields.Char(string='Scope',readonly=True)
    sales_person    = fields.Many2one('res.users', string="Sales Person",readonly=True)
    standard        = fields.Many2one('tsi.iso.standard', string='Standards',readonly=True)
    tahapan_audit   = fields.Selection([
                        ('Stage-01','Stage 1'),
                        ('Stage-02','Stage 2'),
                        ('surveilance1', 'Surveillance 1'),
                        ('surveilance2', 'Surveillance 2'),
                        ('recertification', 'Recertification 1'),
                        ('surveilance3', 'Surveillance 3'),
                        ('surveilance4', 'Surveillance 4'),
                        # ('recertification2', 'Recertification 2'),
                        # ('surveilance5', 'Surveillance 5'),
                        # ('surveilance6', 'Surveillance 6'),
                        ('special',    'Special Audit')
                    ], string='Audit Stage',readonly=True)
    last_tahapan_audit   = fields.Selection([
                        ('Stage-01','Stage 1'),
                        ('Stage-02','Stage 2'),
                        ('surveilance1', 'Surveillance 1'),
                        ('surveilance2', 'Surveillance 2'),
                        ('recertification', 'Recertification 1'),
                        ('surveilance3', 'Surveillance 3'),
                        ('surveilance4', 'Surveillance 4'),
                        # ('recertification2', 'Recertification 2'),
                        # ('surveilance5', 'Surveillance 5'),
                        # ('surveilance6', 'Surveillance 6'),
                        ('special',    'Special Audit')
                    ], string='Last Audit Stage',readonly=True)
    ea_code         = fields.Many2many('tsi.ea_code', string="IAF Code", readonly=True)
    status_klien    = fields.Selection([
                        ('New', 'New'),
                        ('active', 'Active'),
                        ('suspend', 'Suspend'),
                        ('withdraw', 'Withdrawn'),
                        ('Re-Active', 'Re-Active'),
                        ('Double', 'Double'),
                        ('Proses', 'Proses'),
                    ],string='Status Klien',readonly=True)
    tgl_sertifikat          = fields.Date(string='Certificate Date',readonly=True)
    last_audit              = fields.Date(string='Last Audit Date',readonly=True)
    tgl_kontrak             = fields.Date(string='Contract Date',readonly=True)
    
    mandays                  = fields.Float(string='Mandays',readonly=True)
    
    mandays_next_year  = fields.Float(string='Mandays Next Year',readonly=True,store=True)
    mandays_next2_year = fields.Float(string='Mandays Next 2 Year',readonly=True,store=True)
    
    request_end        = fields.Date(string='Plan of audit date',readonly=True)
    actual_start_date  = fields.Date(string='Actual Start Date',readonly=True)
    actual_end_date    = fields.Date(string='Actual End Date',readonly=True)
    
    revenue            = fields.Integer(string='Revenue',readonly=True)
    revenue_next_year  = fields.Integer(string='Revenue Next Year',readonly=True)
    revenue_next2_year = fields.Integer(string='Revenue Next 2 Year',readonly=True)
    prediksi_revenue   = fields.Selection([
                            ('real', 'Real'),
                            ('prediction', 'prediction'),
                        ],string='Revenue Prediction',default='prediction', readonly=True)
    
    tahun              = fields.Date(string='Year',readonly=True)
    
    status_close_won   = fields.Selection([
                            ('close_won', 'Close Won'),
                            ('not_close_won', 'Not Close Won'),
                        ],string='Status Close Won',default='not_close_won', readonly=True)
    close_won_date     = fields.Date(string='Close Won Date',readonly=True)
    
    ops_reference            = fields.Many2one('audit.notification', string="Operation Audit Status Reference",readonly=True)
    ops_program_reference    = fields.Many2one('ops.program', string="Operation Program Reference",readonly=True)
    
    ops_plan_reference       = fields.Many2one('ops.plan', string="Operation Plan Reference",readonly=True)
    ops_report_reference     = fields.Many2one('ops.report', string="Operation Report Reference",readonly=True)
    
    ops_sertifikat_reference = fields.Many2one('ops.sertifikat', string="Operation Sertifikat Reference",readonly=True)
    iso_reference            = fields.Many2one('tsi.iso', string="ISO Reference",readonly=True)
    sales_order_reference    = fields.Many2one('sale.order', string="Sales Order Reference",readonly=True)
    
    crm_reference            = fields.Many2one('tsi.history_kontrak', string="CRM Reference",readonly=True)
    audit_request_reference  = fields.Many2one('tsi.audit.request',string="Audit Request Reference", readonly=True) 
    review_reference         = fields.Many2one('tsi.iso.review',string="Review Reference", readonly=True)
                
    
    def name_get(self):
        result = []
        for record in self:
            name = record.nama_client.name if record.nama_client else record.no_sertifikat
            result.append((record.id, f"{name} - {record.no_sertifikat}"))
        return result
        
    @api.model
    def load_views(self, views, options=None):
        self.create_ows_on_open()
           
        return super(OWS, self).load_views(views, options)
    
    def create_ows_on_open(self):
        # partners = self.env['res.partner'].sudo().search([("id", "=", 4137)])  #
        partners = self.env['res.partner'].sudo().search([("is_company", "=", True)])
        # partners = self.env['res.partner'].sudo().search([("id", "=", 2685)])
        # partners = self.env['res.partner'].sudo().search([("id", "=", 2012)])
        # partners = self.env['res.partner'].sudo().search([("id", "=", 4126)])# certifikat
        
        # partners = self.env['res.partner'].sudo().search([("id", "=", 2276)])# sv
        # partners = self.env['res.partner'].sudo().search([("id", "=", 4126)])# pindah value revenue
        
        current_year = fields.Date.today().year  
        min_year = current_year - 1
        max_year = current_year + 1
        
        # Code new
        for all_partner in partners: 
            tahap_audit = False
            request_end = False
            status_klien = False
            subtotal = 0
            revenue_next_year = 0
            revenue_next2_year = 0
            year_date = False  
            prediksi_revenue = False
            status_close_won = False
            
            
            for sales in self.env["sale.order"].sudo().search([('partner_id', '=', all_partner.id)]):
                # sales IA
                for app in sales:
                    audit_stage = app.iso_reference.audit_stage
                    if audit_stage == "initial":
                        tahap_audit = "Stage-01"
                        status_klien = "Proses"
                        status_close_won = "not_close_won"                    
                    scope = app.iso_reference.scope
                    sales_person = app.iso_reference.sales_person.id if app.iso_reference.sales_person else False
                    request_end = sales.tgl_perkiraan_audit_selesai
                    
                    for standard in app.iso_standard_ids:
                        # IAF Code & Mandays
                        mapping = {
                            "ISO 9001:2015": {
                                "ea_code": app.iso_reference.ea_code_9001,
                                "mandays": app.iso_reference.salesinfo_site
                            },
                            "ISO 14001:2015": {
                                "ea_code": app.iso_reference.ea_code_14001_1,
                                "mandays": app.iso_reference.salesinfo_site_14001
                            },
                            "ISO 45001:2018": {
                                "ea_code": app.iso_reference.ea_code_45001_1,
                                "mandays": app.iso_reference.salesinfo_site_45001
                            },
                            "ISO/IEC 27001:2013": {
                                "ea_code": app.iso_reference.ea_code_27001_1,
                                "mandays": app.iso_reference.salesinfo_site_27001
                            },
                            "ISO/IEC 27001:2022": {
                                "ea_code": app.iso_reference.ea_code_27001_2022_1,
                                "mandays": app.iso_reference.salesinfo_site_27001_2022
                            },
                            "ISO/IEC 27017:2015": {
                                "ea_code": app.iso_reference.ea_code_27017_1,
                                "mandays": app.iso_reference.salesinfo_site_27017
                            },
                            "ISO/IEC 27018:2019": {
                                "ea_code": app.iso_reference.ea_code_27018_1,
                                "mandays": app.iso_reference.salesinfo_site_27018
                            },
                            "ISO/IEC 27701:2019": {
                                "ea_code": app.iso_reference.ea_code_27701_1,
                                "mandays": app.iso_reference.salesinfo_site_27701
                            },
                            "ISO 22000:2018": {
                                "ea_code": app.iso_reference.ea_code_22000_1,
                                "mandays": app.iso_reference.salesinfo_site_22000
                            },
                            "HACCP": {
                                "ea_code": app.iso_reference.ea_code_haccp_1,
                                "mandays": app.iso_reference.salesinfo_site_haccp
                            },
                            "ISO 13485:2016": {
                                "ea_code": app.iso_reference.ea_code_13485_1,
                                "mandays": app.iso_reference.salesinfo_site_13485
                            },
                            "ISO 31000:2018": {
                                # "ea_code": app.iso_reference.ea_code_31000
                                "mandays": app.iso_reference.salesinfo_site_31000
                            },
                            "ISO 22301:2019": {
                                # "ea_code": app.iso_reference.ea_code_22301
                                "mandays": app.iso_reference.salesinfo_site_22301
                            },
                            "ISO 37001:2016": {
                                # "ea_code": app.iso_reference.ea_code_37001
                                "mandays": app.iso_reference.salesinfo_site_37001
                            },
                            "ISO 9994:2018": {
                                # "ea_code": app.iso_reference.ea_code_9994
                                "mandays": app.iso_reference.salesinfo_site_9994
                            },
                        
                            # "ISO 21001:2018": {"ea_code": app.iso_reference.ea_code_21001,"mandays": app.iso_reference.},
                            # "GMP": {"ea_code": app.iso_reference.ea_code_gmp"mandays": app.iso_reference.},
                            # "SMK3": {"ea_code": app.iso_reference.ea_code_smk"mandays": app.iso_reference.},
                            # "ISO 31001:2018": {"ea_code": app.iso_reference.ea_code_31001"mandays": app.iso_reference.},
                            # "ISO 37301:2021": {"ea_code": app.iso_reference.ea_code_37301"mandays": app.iso_reference.},    
                        }
                        
                        standard_name = standard.name if standard else None
                        mapping_entry = mapping.get(standard_name, {})
                        ea_code = mapping_entry.get("ea_code", False)
                        all_mandays = mapping_entry.get("mandays", False)
                        ea_code_ids = ea_code.ids if ea_code else []
                        
                        all_mandayss = [] 
                        if all_mandays: 
                            all_mandayss = all_mandays.ids

                            if all_mandayss:
                                mandays_values = {}
                                def safe_float(value):
                                    try:
                                        if isinstance(value, str):
                                            value = value.replace(",", ".")
                                        return float(value) if value else 0.0
                                    except (ValueError, TypeError):
                                        return 0.0
                                for value_mandays in self.env['tsi.iso.additional_salesinfo'].sudo().search([("id", "in", all_mandayss)]):
                                    filtered_values = {
                                        key: safe_float(value)
                                        for key, value in {
                                            "stage_1": value_mandays.stage_1,
                                            "stage_2": value_mandays.stage_2,
                                            "surveilance_1": value_mandays.surveilance_1,
                                            "surveilance_2": value_mandays.surveilance_2,
                                            "surveilance_3": value_mandays.surveilance_3,
                                            "surveilance_4": value_mandays.surveilance_4,
                                            # "recertification_1": value_mandays.recertification_1,
                                            # "recertification_2": value_mandays.recertification_2,
                                        }.items() if value is not None
                                    }

                                    if filtered_values:
                                        mandays_values[value_mandays.id] = filtered_values
                                
                        mandays_key_map = {
                            "Stage-01": "stage_1",
                            "Stage-02": "stage_2",
                            "surveilance1": "surveilance_1",
                            "surveilance2": "surveilance_2",
                            "surveilance3": "surveilance_3",
                            "surveilance4": "surveilance_4",
                            # "recertification": "recertification",
                            # "recertification_2": "recertification_2",
                        }

                        mandays_key = mandays_key_map.get(tahap_audit, None)
                        mandays = 0

                        if mandays_key and all_mandayss:
                            for mandays_id in all_mandayss:
                                if mandays_id in mandays_values and mandays_key in mandays_values[mandays_id]:
                                    mandays += mandays_values[mandays_id][mandays_key]
                          
                        # Revenue
                        data_revenue_lines = self.env["sale.order.line"].sudo().search([('order_id', '=', sales.id)])
                        for line in data_revenue_lines:
                            product_id = line.product_id
                            if product_id:
                                if standard.name == product_id.name:
                                    if tahap_audit == "Stage-01":
                                        subtotal = line.price_subtotal
                                        year = line.tahun
                                        if year and isinstance(year, str):
                                            try:
                                                year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                            except ValueError:
                                                if len(year) == 4 and year.isdigit():
                                                    year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                                    prediksi_revenue = "real"   
                                                else:
                                                    year_date = False
                                        else:
                                            year_date = False
                                            
                            else:
                                subtotal = 0
                        
                        # Prediction Revenue
                        data_surveillance_prurpose = app.iso_reference.lines_surveillance
                        for surveillance in data_surveillance_prurpose:
                            if surveillance.audit_stage == "Surveillance 1":
                                revenue_next_year = surveillance.price or 0
                                year = surveillance.tahun
                                if year and isinstance(year, str):
                                    try:
                                        year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                    except ValueError:
                                        if len(year) == 4 and year.isdigit():
                                            year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                            prediksi_revenue = "prediction"
                                        else:
                                            year_date = False
                                else:
                                    year_date = False

                            elif surveillance.audit_stage == "Surveillance 2":
                                revenue_next2_year = surveillance.price or 0
                                year = surveillance.tahun
                                if year and isinstance(year, str):
                                    try:
                                        year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                    except ValueError:
                                        if len(year) == 4 and year.isdigit():
                                            year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                            prediksi_revenue = "prediction"
                                        else:
                                            year_date = False
                                else:
                                    year_date = False
                        
                       
                            
                        existing_ows = self.env['tsi.ows'].sudo().search([
                            ('nama_client', '=', all_partner.id),
                            ('standard', '=', standard.id),
                            ('tahapan_audit', '=', tahap_audit),
                        ])

                        if existing_ows:
                            existing_ows.write({
                                "nama_client": all_partner.id,
                                "standard": standard.id,
                                "scope": scope,
                                "sales_person": sales_person, 
                                "tahapan_audit": tahap_audit,
                                "ea_code": [(6, 0, ea_code_ids)],
                                "status_klien": status_klien,
                                "mandays": mandays,
                                # "mandays_next_year": mandays_next_year,
                                # "mandays_next2_year": mandays_next2_year,

                                "request_end": request_end,

                                "revenue": subtotal,
                                "revenue_next_year": revenue_next_year,
                                "revenue_next2_year": revenue_next2_year,
                                "prediksi_revenue": prediksi_revenue,
                                
                                "status_close_won": status_close_won,
                                # "close_won_date": close_won_date,
                                "tahun": year_date,
                                
                                "iso_reference" : app.iso_reference.id,
                                "sales_order_reference": sales.id,
                            })
                        else:
                            self.env['tsi.ows'].create({
                                "nama_client": all_partner.id,
                                "standard": standard.id,
                                "scope": scope,
                                "sales_person": sales_person, 
                                "tahapan_audit": tahap_audit,
                                "ea_code": [(6, 0, ea_code_ids)],
                                "status_klien": status_klien,
                                "mandays": mandays,
                                # "mandays_next_year": mandays_next_year,
                                # "mandays_next2_year": mandays_next2_year,

                                "request_end": request_end,

                                "revenue": subtotal,
                                "revenue_next_year": revenue_next_year,
                                "revenue_next2_year": revenue_next2_year,
                                
                                "status_close_won": status_close_won,
                                # "close_won_date": close_won_date,
                                "tahun": year_date,
                                
                                "iso_reference" : app.iso_reference.id,
                                "sales_order_reference": sales.id,
                            })
            
                        # Review
                        for review in self.env["tsi.iso.review"].sudo().search([('customer', '=', all_partner.id)]):
                            status_close_won = "close_won"
                            close_won_date = review.create_date
                            
                            existing_ows = self.env['tsi.ows'].sudo().search([
                                ('nama_client', '=', all_partner.id),
                                ('standard', '=', standard.id),
                                ('tahapan_audit', '=', tahap_audit),
                            ])
                            if existing_ows:
                                existing_ows.write({
                                    "status_close_won": status_close_won,
                                    "close_won_date": close_won_date,
                                    "review_reference": review.id
                                })
                        

                        
                        # #OPS   
                        for sls in self.env["sale.order"].sudo().search([('partner_id', '=', all_partner.id)]):
                            request_end = sls.tgl_perkiraan_selesai
                            
                            for audit_notifications in self.env["audit.notification"].sudo().search([('customer', '=', all_partner.id)]):
                                for data_ops in audit_notifications:
                                    no_sertifikat = False
                                    tahap_audit = False
                                    initial_date = False
                                    mandays = 0
                                    mandays_float = 0
                                    mandays_next_year = 0
                                    mandays_next2_year = 0
                                    actual_start_date = False
                                    actual_end_date = False
                                    subtotal = 0
                                    revenue_next_year = 0
                                    revenue_next2_year = 0
                                    status_klien = "Proses"
                                    
                                    ops_reference = audit_notifications
                                    ops_program_reference = False
                                    ops_plan_reference = False
                                    ops_report_reference = False
                                    ops_sertifikat_reference = False
                                    
                                    datas_ops_line = data_ops.mapped("program_lines")
                                    datas_ops_plan_line = data_ops.mapped("plan_lines")
                                    datas_ops_report_line = data_ops.mapped("report_lines")
                                    datas_sertifikat_line = data_ops.mapped("sertifikat_lines")
                                    
                                    iso_reference = data_ops.iso_reference
                                    sales_order_reference = data_ops.sales_order_id
                                    
                                    # Audit Request
                                    for data_revenues in self.env["sale.order"].sudo().search([('id', '=', data_ops.sales_order_id.id)]):
                                        data_revenue_lines = self.env["sale.order.line"].sudo().search([('order_id', '=', data_revenues.id)])
                                        for line in data_revenue_lines:
                                            product_id = line.product_id
                                                
                                            # Audit Request 
                                            data_tahap_audit = line.audit_tahapan
                                            request_audit = False 
                                            tahap_audit = False

                                            if data_tahap_audit == "Initial Audit":
                                                for auditt in data_ops:
                                                    request_audit = auditt.create_date
                                                    tahap_audit = "Stage-01"
                                            else:
                                                crm_request_audits = self.env["tsi.audit.request"].sudo().search([('partner_id', '=', all_partner.id)])
                                                for audit in crm_request_audits:
                                                    request_audit = audit.create_date
                                                    tahap_audit = audit.audit_stage
                                                    
                                    # Cek sertifikat
                                    if datas_sertifikat_line:
                                        for sertifikat in datas_sertifikat_line:
                                            sertifikats = self.env["ops.sertifikat"].sudo().search([('name', '=', sertifikat.name)])
                                            if sertifikats:
                                                ops_sertifikat_reference = sertifikats.id
                                                no_sertifikat = sertifikats.nomor_sertifikat
                                                initial_date = sertifikats.initial_date
                                                status_klien = "active"
                                                subtotal = 0         
                                                                            
                                    # Cek program line
                                    for program in datas_ops_line:
                                        data_ops_programs = self.env["ops.program"].sudo().search([('name', '=', program.name)])
                                        scope = data_ops_programs.scope
                                        standard = data_ops_programs.iso_standard_ids
                                        ops_program_reference = data_ops_programs
                                        ea_code = data_ops_programs.ea_code_prog
                                        
                                        # Reference Form ISO
                                        data_iso_reference = data_ops_programs.iso_reference if data_ops_programs.iso_reference else None
                                        sales_person = False

                                        if data_iso_reference:
                                            sales_order = self.env["tsi.iso"].sudo().search([('name', '=', data_iso_reference.name)])
                                            if sales_order:
                                                sales_person = sales_order.sales_person.id                                  
                                                
                                                data_surveillance_prurpose = sales_order.lines_surveillance
                                                for surveillance in data_surveillance_prurpose:
                                                    if surveillance.audit_stage == "Surveillance 1":
                                                        revenue_next_year = surveillance.price or 0
                                                        year = surveillance.tahun
                                                        if year and isinstance(year, str):
                                                            try:
                                                                year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                                            except ValueError:
                                                                if len(year) == 4 and year.isdigit():
                                                                    year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                                                    prediksi_revenue = "prediction"
                                                                    # _logger.info("Data Prediksi 1 %s", prediksi_revenue)
                                                                else:
                                                                    year_date = False
                                                        else:
                                                            year_date = False
                                                        
                                                    elif surveillance.audit_stage == "Surveillance 2":
                                                        revenue_next2_year = surveillance.price or 0
                                                        year = surveillance.tahun
                                                        if year and isinstance(year, str):
                                                            try:
                                                                year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                                            except ValueError:
                                                                if len(year) == 4 and year.isdigit():
                                                                    year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                                                    prediksi_revenue = "prediction"
                                                                    # _logger.info("Data Prediksi  2 %s", prediksi_revenue)
                                                                else:
                                                                    year_date = False
                                                        else:
                                                            year_date = False
                                            else:
                                                sales_person = False
                                        
                                        for data_ops_program in data_ops_programs:
                                            ops_program_line_ids = data_ops_program.mapped("program_lines_aktual.id")
                                            
                                            if ops_program_line_ids:
                                                ops_program_lines = self.env["ops.program.aktual"].sudo().search([('id', 'in', ops_program_line_ids)])
                                                # _logger.info("Banyak adata Aktual: %s",ops_program_lines)
                                                
                                                if ops_program_lines:
                                                    # Fungsi  string menjadi float
                                                    def safe_float(val):
                                                        try:
                                                            val = str(val).replace(",", ".")
                                                            return float(val or 0)
                                                        except (ValueError, TypeError):
                                                            return 0.0
                                                    for ops_program_line_aktual in ops_program_lines:
                                                        tahap_audit       = ops_program_line_aktual.audit_type
                                                        actual_start_date = ops_program_line_aktual.date_start
                                                        actual_end_date   = ops_program_line_aktual.date_end
                                                        mandays           = ops_program_line_aktual.mandayss
                                                        mandays_float     = safe_float(mandays)
                                                        scope             = data_ops_program.scope
                                                        standard          = data_ops_program.iso_standard_ids
                                                        
                                                        # Mandays prediction
                                                        # Mandays prediction ISO 9001
                                                        # mandays_pred = sales_order.salesinfo_site.ids
                                                        # data_mandays_pred = self.env["tsi.iso.additional_salesinfo"].search([('id', 'in', mandays_pred)])
                                                        
                                                        # stage_1_total = sum(safe_float(rec.stage_1) for rec in data_mandays_pred)
                                                        # stage_2_total = sum(safe_float(rec.stage_2) for rec in data_mandays_pred)
                                                        # sv1_total = sum(safe_float(rec.surveilance_1) for rec in data_mandays_pred)
                                                        # sv2_total = sum(safe_float(rec.surveilance_2) for rec in data_mandays_pred)
                                                        # recertification_total = sum(safe_float(rec.recertification) for rec in data_mandays_pred)
                                                        
                                                        # if tahap_audit in ['Stage-01','Stage-02']:
                                                        #     mandays_next_year = sv1_total
                                                        #     mandays_next2_year = sv2_total
                                                        # elif tahap_audit == 'surveilance1':
                                                        #     mandays_next_year = sv2_total
                                                        #     mandays_next2_year = recertification_total
                                                        # elif tahap_audit == 'surveilance2':
                                                        #     mandays_next_year = recertification_total
                                                        #     mandays_next2_year = 0
                                                        # elif tahap_audit == 'recertification':
                                                        #     mandays_next_year = 0
                                                        #     mandays_next2_year = 0
                                                                                                    
                                                        # cek ops plan
                                                        if datas_ops_plan_line:
                                                            for plan in datas_ops_plan_line:
                                                                plans = self.env["ops.plan"].sudo().search([('name', '=', plan.name)])
                                                                for planss in plans:
                                                                    if planss:
                                                                        if planss.audit_stage == tahap_audit:
                                                                            ops_plan_reference = planss.id
                                                        
                                                        # cek ops report
                                                        if datas_ops_report_line:
                                                            for report in datas_ops_report_line:
                                                                reports = self.env["ops.report"].sudo().search([('name', '=', report.name)])
                                                                for reportss in reports:
                                                                    if reportss:
                                                                        if reportss.audit_stage == tahap_audit:
                                                                            ops_report_reference = reportss.id
                                                        
                                                        # Revenue                                    
                                                        for data_revenues in self.env["sale.order"].sudo().search([('id', '=', data_ops.sales_order_id.id)]):
                                                            data_revenue_lines = self.env["sale.order.line"].sudo().search([('order_id', '=', data_revenues.id)])
                                                            for line in data_revenue_lines:
                                                                product_id = line.product_id
                                                                    
                                                                if product_id:
                                                                    date_now = fields.Date.context_today(self)
                                                                    if standard.name == product_id.name:
                                                                        if tahap_audit == "Stage-01":
                                                                            # subtotal = line.price_subtotal
                                                                            subtotal = 0
                                                                            year = line.tahun
                                                                            if year and isinstance(year, str):
                                                                                try:
                                                                                    year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                                                                except ValueError:
                                                                                    if len(year) == 4 and year.isdigit():
                                                                                        year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                                                                        prediksi_revenue = "real"
                                                                                        # _logger.info("Data Real %s", prediksi_revenue)
                                                                                    else:
                                                                                        year_date = False
                                                                            else:
                                                                                year_date = False
                                                                            
                                                                        else:
                                                                            if actual_end_date and actual_end_date <= date_now:
                                                                                subtotal = line.price_subtotal
                                                                                year = line.tahun
                                                                                if year and isinstance(year, str):
                                                                                    try:
                                                                                        year_date = datetime.strptime(year, "%Y-%m-%d").date()
                                                                                    except ValueError:
                                                                                        if len(year) == 4 and year.isdigit():
                                                                                            year_date = datetime.strptime(year + "-01-01", "%Y-%m-%d").date()
                                                                                            prediksi_revenue = "real"
                                                                                            # _logger.info("Data Real %s", prediksi_revenue)
                                                                                        else:
                                                                                            year_date = False
                                                                                else:
                                                                                    year_date = False
                                                                                    
                                                                            else:
                                                                                subtotal = 0 
                                                                            
                                                                else:
                                                                    subtotal = 0
                                                                        
                                                        if request_audit and request_audit.year >= min_year and request_audit.year <= max_year:   
                                                            existing_ows = self.env['tsi.ows'].sudo().search([
                                                                ('nama_client', '=', all_partner.id),
                                                                ('standard', '=', standard.id),
                                                                ('tahapan_audit', '=', tahap_audit),
                                                            ])
                                                            
                                                            # if not (request_audit.year == current_year - 1 and tahap_audit == 'Stage-01'):
                                                            if existing_ows:
                                                                # update value mandays next year
                                                                # if current_year == request_audit.year + 1:
                                                                #     mandays_float = mandays_next_year 
                                                                #     mandays_next_year = mandays_next2_year 
                                                                #     mandays_next2_year = recertification_total
                                                                #     # _logger.info("mandays: %s", mandays_float)
                                                                #     # _logger.info("mandays_next_year: %s", mandays_next_year)
                                                                #     # _logger.info("mandays_next2_year: %s", mandays_next2_year)
                                                                # else:
                                                                #     _logger.info("Data Tidak ada")
                                                                    
                                                                # Data  Stage 1 tahun sebelum
                                                                # if  request_audit.year == current_year - 1 and tahap_audit == "Stage-01":
                                                                #     _logger.info("Data Stage 1")
                                                                # else:
                                                                #     _logger.info("Tidak ada Stage 1")
                                                                
                                                                
                                                               
                                                               
                                                                existing_ows.write({
                                                                    "no_sertifikat": no_sertifikat,
                                                                    "nama_client": all_partner.id,
                                                                    "standard": standard.id,
                                                                    "scope": scope, 
                                                                    "sales_person": sales_person,
                                                                    "tahapan_audit": tahap_audit,
                                                                    "ea_code": ea_code,
                                                                    "status_klien": status_klien,
                                                                    "tgl_sertifikat": initial_date,
                                                                    "last_audit": actual_end_date,
                                                                    "tgl_kontrak": request_audit,
                                                                    "mandays": mandays_float,
                                                                    "mandays_next_year": mandays_next_year,
                                                                    "mandays_next2_year": mandays_next2_year,
                                                                    
                                                                    "request_end": request_end,
                                                                    
                                                                    "actual_start_date": actual_start_date,
                                                                    "actual_end_date": actual_end_date,
                                                                    
                                                                    "revenue": subtotal,
                                                                    "revenue_next_year": revenue_next_year,
                                                                    "revenue_next2_year": revenue_next2_year,
                                                                    "prediksi_revenue": prediksi_revenue,
                                                                    "tahun": year_date,
                                                                    
                                                                    "ops_reference": ops_reference.id,
                                                                    "ops_program_reference": ops_program_reference.id,
                                                                    "ops_plan_reference": ops_plan_reference,
                                                                    "ops_report_reference": ops_report_reference,
                                                                    "ops_sertifikat_reference": ops_sertifikat_reference,
                                                                    
                                                                    "iso_reference": iso_reference.id,
                                                                    "sales_order_reference": sales_order_reference.id,
                                                                    
                                                                    # "audit_request_reference": audit_requests.id
                                                                })
                                                            else:
                                                                self.env['tsi.ows'].create({
                                                                    "no_sertifikat": no_sertifikat,
                                                                    "nama_client": all_partner.id,
                                                                    "standard": standard.id,
                                                                    "scope": scope,
                                                                    "sales_person": sales_person, 
                                                                    "tahapan_audit": tahap_audit,
                                                                    "ea_code": ea_code,
                                                                    "status_klien": status_klien,
                                                                    "tgl_sertifikat": initial_date,
                                                                    "last_audit": actual_end_date,
                                                                    "tgl_kontrak": request_audit,
                                                                    "mandays": mandays_float,
                                                                    "mandays_next_year": mandays_next_year,
                                                                    "mandays_next2_year": mandays_next2_year,
                                                                    
                                                                    "request_end": request_end,
                                                                    
                                                                    "actual_start_date": actual_start_date,
                                                                    "actual_end_date": actual_end_date,
                                                                    
                                                                    "revenue": subtotal,
                                                                    "revenue_next_year": revenue_next_year,
                                                                    "revenue_next2_year": revenue_next2_year,
                                                                    
                                                                    "prediksi_revenue": prediksi_revenue,
                                                                    "tahun": year_date,
                                                                    
                                                                    "ops_reference": ops_reference.id,
                                                                    "ops_program_reference": ops_program_reference.id,
                                                                    "ops_plan_reference": ops_plan_reference,
                                                                    "ops_report_reference": ops_report_reference,
                                                                    "ops_sertifikat_reference": ops_sertifikat_reference,
                                                                    
                                                                    "iso_reference": iso_reference.id,
                                                                    "sales_order_reference": sales_order_reference.id,
                                                                    
                                                                    # "audit_request_reference": audit_requests.id
                                                                })
                                                                
                                                            # Ravenue Geser
                                                            # new_year = datetime.now().year
                                                            # _logger.info("New Year %s", new_year)
                                                            # _logger.info("Old Year %s", year_date)

                                                            # # if year_date < new_year:
                                                            # if year_date and year_date.year < new_year:

                                                            #     _logger.info("Tahun %s", year_date)
                                                            #     new_revenue = revenue_next_year or 0
                                                            #     new_revenue_next_year = revenue_next2_year or 0
                                                            #     new_revenue_next2_year = 0
        
                                                            #     existing_ows.write({
                                                            #         "revenue": new_revenue,
                                                            #         "revenue_next_year": new_revenue_next_year,
                                                            #         "revenue_next2_year": revenue_next2_year,
                                                            #         "prediksi_revenue": new_revenue_next2_year,
                                                            #         # "tahun": new_year,
                                                            #     })
                                                            #     _logger.info("Data Revenue Geser %s", existing_ows)
                                                                            
                                            else:      
                                                # if request_audit and request_audit.year >= min_year and request_audit.year <= max_year:       
                                                    existing_ows = self.env['tsi.ows'].sudo().search([
                                                        ('nama_client', '=', all_partner.id),
                                                        ('standard', '=', standard.id),
                                                        ('tahapan_audit', '=', tahap_audit),
                                                    ])

                                                    # if not (request_audit.year == current_year - 1 and tahap_audit == 'Stage-01'):
                                                    if existing_ows:
                                                        existing_ows.write({
                                                            "no_sertifikat": no_sertifikat,
                                                            "nama_client": all_partner.id,
                                                            "standard": standard.id,
                                                            "scope": scope, 
                                                            "sales_person": sales_person,
                                                            "tahapan_audit": tahap_audit,
                                                            "ea_code": ea_code,
                                                            "status_klien": status_klien,
                                                            "tgl_sertifikat": initial_date,
                                                            "last_audit": actual_end_date,
                                                            "tgl_kontrak": request_audit,
                                                            "mandays": mandays,
                                                            "mandays_next_year": mandays_next_year,
                                                            "mandays_next2_year": mandays_next2_year,
                                                            
                                                            "request_end": request_end,
                                                            
                                                            "actual_start_date": actual_start_date,
                                                            "actual_end_date": actual_end_date,
                                                            
                                                            "revenue": subtotal,
                                                            "revenue_next_year": revenue_next_year,
                                                            "revenue_next2_year": revenue_next2_year,
                                                            
                                                            "prediksi_revenue": prediksi_revenue,
                                                            "tahun": year_date,
                                                            
                                                            "ops_reference": ops_reference.id,
                                                            "ops_program_reference": ops_program_reference.id,
                                                            
                                                            # "ops_plan_reference": ops_plan_reference,
                                                            # "ops_report_reference": ops_report_reference,
                                                            
                                                            "ops_sertifikat_reference": ops_sertifikat_reference,
                                                            
                                                            "iso_reference": iso_reference.id,
                                                            "sales_order_reference": sales_order_reference.id,
                                                            
                                                            # "audit_request_reference": audit_requests.id
                                                        })
                                                    else:
                                                        self.env['tsi.ows'].create({
                                                            "no_sertifikat": no_sertifikat,
                                                            "nama_client": all_partner.id,
                                                            "standard": standard.id,
                                                            "scope": scope, 
                                                            "sales_person": sales_person,
                                                            "tahapan_audit": tahap_audit,
                                                            "ea_code": ea_code,
                                                            "status_klien": status_klien,
                                                            "tgl_sertifikat": initial_date,
                                                            "last_audit": actual_end_date,
                                                            "tgl_kontrak": request_audit,
                                                            "mandays": mandays,
                                                            "mandays_next_year": mandays_next_year,
                                                            "mandays_next2_year": mandays_next2_year,
                                                            
                                                            "request_end": request_end,
                                                            
                                                            "actual_start_date": actual_start_date,
                                                            "actual_end_date": actual_end_date,
                                                            
                                                            "revenue": subtotal,
                                                            "revenue_next_year": revenue_next_year,
                                                            "revenue_next2_year": revenue_next2_year,
                                                            
                                                            "prediksi_revenue": prediksi_revenue,
                                                            "tahun": year_date,
                                                            
                                                            "ops_reference": ops_reference.id,
                                                            "ops_program_reference": ops_program_reference.id,
                                                            # "ops_plan_reference": ops_plan_reference,
                                                            # "ops_report_reference": ops_report_reference,
                                                            "ops_sertifikat_reference": ops_sertifikat_reference,
                                                            
                                                            "iso_reference": iso_reference.id,
                                                            "sales_order_reference": sales_order_reference.id,
                                                            
                                                            # "audit_request_reference": audit_requests.id
                                                        })
                                        
                                        
                                        existing_ows = self.env['tsi.ows'].sudo().search([
                                            ('nama_client', '=', all_partner.id),
                                            ('standard', '=', standard.id),
                                            ('tahapan_audit', '=', tahap_audit),
                                        ])
                                        # for ows in existing_ows:
                                        #     tgl_sertifikat = existing_ows.tgl_sertifikat
                                        # # _logger.info("tgl_sertifikat : %s",tgl_sertifikat)
                                        # year = existing_ows.tahun
                                        # _logger.info("tahun: %s", year)
                                        # if existing_ows and tgl_sertifikat:
                                        #     for ows in existing_ows:
                                                
                                        #         year_date_final = False
                                        #         try:
                                        #             if isinstance(existing_year, str):
                                        #                 existing_year = datetime.strptime(existing_year, "%Y-%m-%d").date()
                                        #             elif isinstance(existing_year, datetime):
                                        #                 existing_year = existing_year.date()
                                                        
                                        #             month = tgl_sertifikat.month
                                        #             day = tgl_sertifikat.day

                                        #             year_date_final = date(existing_year.year, month, day)
                                        #             _logger.info("data final: %s", year_date_final)

                                        #             ows.write({
                                        #                 "tahun": year_date_final,
                                        #             })
                                        #         except Exception as e:
                                        #             _logger.warning("Gagal update tahun di OWS: %s", e)
                                
        #CRM
        # for crm in partners:
        #     for crms in self.env["tsi.history_kontrak"].sudo().search([('partner_id', '=', crm.id), ('state_klien', '=', 'active')]): 
        #         scope = crms.scope
        #         sales_person = crms.sales.id    
        #         status_klien = crms.state_klien
        #         no_sertifikat = None
        #         standard_name = None
        #         standard = False
        #         tahapan = False
        #         initial_date = False
        #         ea_code = False
        #         ea_code_ids = []
        #         tgl_kontrak = False
        #         subtotal = 0
        #         revenue_next_year = 0
        #         revenue_next2_year = 0
        #         tahap_audit = False
                
        #         tahapan_order = False

        #         all_tahapan = [
        #             ("initial", crms.tahapan_ori_lines),
        #             ("sv1", crms.tahapan_ori_lines1),
        #             ("sv2", crms.tahapan_ori_lines2),
        #             ("re_1", crms.tahapan_ori_lines_re),
        #             ("sv3", crms.tahapan_ori_lines3),
        #             ("sv4", crms.tahapan_ori_lines4),
        #         ]
        #         all_tahapan = [(t, t_data) for t, t_data in all_tahapan if t_data]

        #         subtotal_sv1 = 0
        #         subtotal_sv2 = 0

        #         if all_tahapan:
        #             for tahap, tahapan in all_tahapan:
        #                 for data_crm in tahapan:
        #                     if tahap == "sv1":
        #                         subtotal_sv1 = data_crm.mandays_s1 or 0  
        #                     elif tahap == "sv2":
        #                         subtotal_sv2 = data_crm.mandays_s2 or 0

        #             for tahap, tahapan in all_tahapan:
        #                 for data_crm in tahapan:
        #                     if tahap == "initial":
        #                         tahap_audit = "Stage-02"
        #                         no_sertifikat = data_crm.nomor_ia or False
        #                         standard = data_crm.standard.id or False
        #                         initial_date = data_crm.tanggal_sertifikat1 or False
        #                         tgl_kontrak = data_crm.tanggal_kontrak_ia or False
        #                         subtotal = data_crm.mandays or 0
        #                         revenue_next_year = subtotal_sv1
        #                         revenue_next2_year = subtotal_sv2

        #                     standard_name = data_crm.standard.name if data_crm.standard else None
        #                     mapping_entry = {
        #                         "ISO 9001:2015": (crms.ea_code_9001, crms.mandays_ids),
        #                         "ISO 14001:2015": (crms.ea_code_14001, crms.mandays_ids_14001),
        #                         "ISO 45001:2018": (crms.ea_code_45001, crms.mandays_ids_45001),
        #                         "ISO 13485:2016": (crms.ea_code_13485, crms.mandays_ids_13485),
        #                         "ISO 21001:2018": (crms.ea_code_21001, crms.mandays_ids_21001),
        #                         "ISO 22000:2018": (crms.ea_code_22000, crms.mandays_ids_22000),
        #                         "HACCP": (crms.ea_code_haccp, crms.mandays_ids_haccp),
        #                         "GMP": (crms.ea_code_gmp, crms.mandays_ids_gmp),
        #                         "SMK3": (crms.ea_code_smk, crms.mandays_ids_smk),
        #                         "ISO/IEC 27001:2013": (crms.ea_code_27001, crms.mandays_ids_27001),
        #                         "ISO/IEC 27001:2022": (crms.ea_code_27001_2022, crms.mandays_ids_27001_2022),
        #                         "ISO/IEC 27701:2019": (crms.ea_code_27701, crms.mandays_ids_27701),
        #                         "ISO/IEC 27017:2015": (crms.ea_code_27017, crms.mandays_ids_27017),
        #                         "ISO/IEC 27018:2019": (crms.ea_code_27018, crms.mandays_ids_27018),
        #                         "ISO 31000:2018": (crms.ea_code_31000, crms.mandays_ids_31000),
        #                         "ISO 31001:2018": (crms.ea_code_31001, crms.mandays_ids_31001),
        #                         "ISO 22301:2019": (crms.ea_code_22301, crms.mandays_ids_22301),
        #                         "ISO 37001:2016": (crms.ea_code_37001, crms.mandays_ids_37001),
        #                         "ISO 37301:2021": (crms.ea_code_37301, crms.mandays_ids_37301),
        #                         "ISO 9994:2018": (crms.ea_code_9994, crms.mandays_ids_9994),
        #                     }.get(standard_name, (False, False))

        #                     ea_code, all_mandays = mapping_entry
        #                     ea_code_ids = ea_code.ids if ea_code else []
        #                     mandays_values = {}

        #                     if all_mandays:
        #                         for value_mandays in all_mandays:
        #                             def safe_float(value):
        #                                 try:
        #                                     return float(str(value).replace(",", ".")) if value else 0.0
        #                                 except (ValueError, TypeError):
        #                                     return 0.0
        #                             mandays_values[value_mandays.id] = {
        #                                 key: safe_float(getattr(value_mandays, key))
        #                                 for key in [
        #                                     "stage_1", "stage_2",
        #                                     "surveilance_1", "surveilance_2",
        #                                     "surveilance_3", "surveilance_4"
        #                                 ]
        #                                 if getattr(value_mandays, key) is not None
        #                             }

        #                     mandays_key = {
        #                         "Stage-02": "stage_2",
        #                         "surveilance1": "surveilance_1",
        #                         "surveilance2": "surveilance_2",
        #                         "surveilance3": "surveilance_3",
        #                         "surveilance4": "surveilance_4",
        #                     }.get(tahap_audit, None)

        #                     mandays = 0
        #                     if mandays_key:
        #                         for val in mandays_values.values():
        #                             mandays += val.get(mandays_key, 0.0)

        #                     if initial_date and min_year <= initial_date.year <= max_year:
        #                         domain = [
        #                             ('nama_client', '=', crm.id),
        #                             ('standard', '=', standard),
        #                             # ('tahapan_audit', '=', tahap_audit),
        #                             ('crm_reference', '=', crms.id),
        #                         ]
        #                         existing_ows = self.env['tsi.ows'].sudo().search(domain, limit=1)

        #                         ows_vals = {
        #                             "no_sertifikat": no_sertifikat,
        #                             "nama_client": crm.id,
        #                             "scope": scope,
        #                             "sales_person": sales_person,
        #                             "standard": standard,
        #                             "tahapan_audit": tahap_audit,
        #                             "ea_code": [(6, 0, ea_code_ids)],
        #                             "status_klien": status_klien,
        #                             "tgl_sertifikat": initial_date,
        #                             "tgl_kontrak": tgl_kontrak,
        #                             "mandays": mandays,
        #                             "revenue": subtotal,
        #                             "revenue_next_year": revenue_next_year,
        #                             "revenue_next2_year": revenue_next2_year,
        #                             "crm_reference": crms.id
        #                         }

        #                         if existing_ows:
        #                             existing_ows.write(ows_vals)
        #                         else:
        #                             self.env['tsi.ows'].sudo().create(ows_vals)

        #                     # Update last audit stage
        #                     if status_klien == 'active':
        #                         last_tahapan_audit = tahap_audit
        #                         tahapan_order = [
        #                             'Stage-01', 'Stage-02',
        #                             'surveilance1', 'surveilance2',
        #                             'recertification', 'surveilance3',
        #                             'surveilance4'
        #                         ]
        #                         existing_ows_all = self.env['tsi.ows'].sudo().search([
        #                             ('nama_client', '=', crm.id),
        #                             ('standard', '=', standard),
        #                         ])

        #                         for ows in existing_ows_all:
        #                             current_index = tahapan_order.index(ows.tahapan_audit) if ows.tahapan_audit in tahapan_order else -1

        #                             if current_index >= 0:
        #                                 latest_audit = self.env["tsi.audit.request"].sudo().search([
        #                                     ('partner_id', '=', crm.id),
        #                                     ('iso_standard_ids', '=', standard),
        #                                 ], order='create_date desc', limit=1)

        #                                 if latest_audit and latest_audit.audit_stage in tahapan_order:
        #                                     latest_index = tahapan_order.index(latest_audit.audit_stage)
        #                                     if latest_index > current_index:
        #                                         ows.write({
        #                                             "status_klien": "Proses",
        #                                             "last_tahapan_audit": last_tahapan_audit,
        #                                             "tahapan_audit": latest_audit.audit_stage,
        #                                         })

        
        