from base64 import standard_b64decode
from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime, timedelta, date
from num2words import num2words
import logging
import roman
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
import requests
import json
_logger = logging.getLogger(__name__)


class ISO(models.Model):
    _name           = "tsi.iso"
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = "Application Form"
    _order          = 'id DESC'

    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', index=True, )
    user_id = fields.Many2one(
        'res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]"
        )
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    sales_person    = fields.Many2one('res.users', string="Sales Person", tracking=True)
    name            = fields.Char(string="Document No",  readonly=True, tracking=True)
    customer        = fields.Many2one('res.partner', string="Company Name", domain="[('is_company', '=', True)]", tracking=True)
    alamat          = fields.Char(string="Alamat", tracking=True)
    issue_date      = fields.Date(string="Issued Date", default=datetime.now(), tracking=True)    
    multisite       = fields.Text(string="Permohonan Multisite", tracking=True)
    contact_name    = fields.Many2one('res.partner', string="Nama Contact", tracking=True)
    
    company_name        = fields.Char(string="Company", tracking=True)
    office_address      = fields.Char(string="Office Address", tracking=True)
    invoicing_address   = fields.Char(string="Invoicing Address", tracking=True)
    contact_person      = fields.Char(string="Contact Person", tracking=True)
    pic_id              = fields.Many2one('res.partner', string="Existing Contact Person", domain="[('is_company', '=', False)]", tracking=True) 
    
    
    
    
    jabatan         = fields.Char(string="Position", tracking=True)
    telepon         = fields.Char(string="Telephone", tracking=True)
    fax             = fields.Char(string="Fax", tracking=True)
    email           = fields.Char(string="Email", tracking=True)
    website         = fields.Char(string="Website", tracking=True)
    cellular        = fields.Char(string="Celular", )
    certification   = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, tracking=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True, domain="[('standard', 'in', ['iso'])]")
    iso_standard_other   = fields.Char(string="Other Standards", tracking=True)

    outsourced_activity = fields.Text(string="Outsourced Activity", tracking=True)

    state_sales = fields.Selection([
        ('draft', 'Quotation'),
        ('cliennt_approval', 'Client Approval'),
        ('waiting_verify_operation', 'Waiting Verify Operation'),
        ('create_kontrak', 'Create Kontrak'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('application_form', 'Application Form'),
    ], string='Status Sales', compute='_compute_state', store=True, tracking=True, related="sale_order_id.state")

    is_associate        = fields.Boolean(string='Associate')    
    associate_id        = fields.Many2one('res.partner', "Associate Name", domain = [('is_company','=',False)], tracking=True)
    email_associate     = fields.Char(string='Email', tracking=True)
    phone_associate     = fields.Char(string='No Telp', tracking=True)

    #Frenchise
    is_franchise        = fields.Boolean(string='Frenchise')    
    franchise_id        = fields.Many2one('res.partner', "Frenchise Name", domain = [('is_company','=',True)], tracking=True)
    email_franchise     = fields.Char(string='Email', tracking=True)
    phone_franchise     = fields.Char(string='No Telp', tracking=True)

    #Leads
    is_leads        = fields.Boolean(string='Leads')
    leads_selection = fields.Selection([
        ('eksternal', 'Eksternal'),
        ('internal', 'Internal'),
    ], string='Tipe', tracking=True)
    leads_description = fields.Text(string="Keterangan Leads")
    show_leads_description = fields.Boolean(compute="_compute_show_leads_description")

    iso_hazard_ids      = fields.Many2many('tsi.hazard', string='Hazards')
    iso_hazard_other    = fields.Char(string="Other Hazard", tracking=True)

    iso_env_aspect_ids  = fields.Many2many('tsi.env_aspect', string='Environmental Aspect')
    iso_aspect_other    = fields.Char(string="Other Aspect", tracking=True)

    ea_code             = fields.Many2one('tsi.ea_code', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    ea_code_9001        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_9001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )

    ea_code_14001           = fields.Many2one('tsi.ea_code', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    ea_code_14001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_14001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_14001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_14001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_14001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id2', string="Additional Info", index=True)

    #ISO27001:2013
    ea_code_27001           = fields.Many2one('tsi.ea_code', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    ea_code_27001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27001', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    accreditation_27001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id3', string="Additional Info", index=True)

    #ISO27001:2022
    ea_code_27001_2022           = fields.Many2one('tsi.ea_code', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    ea_code_27001_2022_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27001_2022', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    accreditation_27001_2022     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27001_2022        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27001_2022    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id12', string="Additional Info", index=True)

    #ISO27017
    ea_code_27017           = fields.Many2one('tsi.ea_code', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    ea_code_27017_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27017', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    accreditation_27017     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27017        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27017    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id13', string="Additional Info", index=True)

    #ISO27018
    ea_code_27018           = fields.Many2one('tsi.ea_code', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    ea_code_27018_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27018', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    accreditation_27018     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27018        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27018    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id14', string="Additional Info", index=True)

    #ISO27701
    ea_code_27701           = fields.Many2one('tsi.ea_code', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    ea_code_27701_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_27701', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    accreditation_27701     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_27701        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_27701    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id15', string="Additional Info", index=True)

    ea_code_45001           = fields.Many2one('tsi.ea_code', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    ea_code_45001_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_45001', string="IAF Code Existing", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_45001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_45001        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_45001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id4', string="Additional Info", index=True)

    ea_code_22000           = fields.Many2one('tsi.ea_code', string="IAF Code", domain="[('iso_standard_ids.name', 'in', 'ISO 22000:2018')]")
    ea_code_22000_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_22000', string="Food Category", domain="[('iso_standard_ids.name', 'in', ['ISO 22000:2018', 'HACCP', 'FSCC 22000'])]")
    accreditation_22000     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_22000        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_22000    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id5', string="Additional Info", index=True)

    ea_code_haccp           = fields.Many2one('tsi.ea_code', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'HACCP')]")
    ea_code_haccp_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_haccp', string="IAF Code Existing", domain="[('iso_standard_ids.name', '=', 'HACCP')]")
    accreditation_haccp     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_haccp        = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_haccp    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id6', string="Additional Info", index=True)

    show_gdp        = fields.Boolean(string='Show GDP', default=False)
    ea_code_gdp        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_gdp', string="IAF Code Existing", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_gdp       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_gdp          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_gdp    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id17', string="Additional Info", index=True)

    show_56001        = fields.Boolean(string='Show 56001', default=False)
    ea_code_56001        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_56001', string="IAF Code Existing", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_56001       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_56001          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    salesinfo_site_56001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id18', string="Additional Info", index=True)

    # scope 
    scope       = fields.Text('Scope',tracking=True)
    boundaries  = fields.Text('Boundaries',tracking=True, default="All related area, department & functions within scope")
    cause       = fields.Text('Mandatory SNI',tracking=True)
    isms_doc    = fields.Text('ISMS Document',tracking=True)

    # personnel
    head_office     = fields.Char(string="Head Office", tracking=True)
    site_office     = fields.Char(string="Site Office", tracking=True)
    off_location    = fields.Char(string="Off Location", tracking=True)
    part_time       = fields.Char(string="Part Time", tracking=True)
    subcon          = fields.Char(string="Sub Contractor", tracking=True)
    unskilled       = fields.Char(string="Unskilled", tracking=True)
    seasonal        = fields.Char(string="Seasonal", tracking=True)
    total_emp       = fields.Char(string="Total Employee", tracking=True)
    shift_number    = fields.Char(string="Shift", tracking=True)
    number_site     = fields.Char(string="Number Site", tracking=True)
    outsource_proc  = fields.Text('Outsourcing Process', tracking=True)

    # management 
    last_audit      = fields.Text('Last Audit', tracking=True)
    last_review     = fields.Text('Last Review', tracking=True)


    tx_site_count   = fields.Integer('Number of Site', tracking=True)
    upload_file     = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    tx_remarks      = fields.Char('Remarks', tracking=True)

    # maturity
    start_implement     = fields.Char(string="Start of Implementation", tracking=True)

    mat_consultancy     = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Use of Consultants", tracking=True)
    mat_certified       = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified System", tracking=True)
    other_system         = fields.Char(string='Other System', tracking=True)
    # mat_certified_cb    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified CB", )
    # mat_tools           = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Continual Improvement", )
    # mat_national        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="National Certified", )
    # mat_more            = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Setup More Standard", )

    txt_mat_consultancy = fields.Char(string="Tx Consultancy", tracking=True)
    txt_mat_certified   = fields.Char(string="Tx Certified", tracking=True)
    # txt_mat_certified_cb    = fields.Char(string="Tx Certified CB", )
    # txt_mat_tools       = fields.Char(string="Tx Continual Improvement", )
    # txt_mat_national    = fields.Char(string="Tx National Certified", )
    # txt_mat_more        = fields.Char(string="Tx Setup More Standard", )

     # integrated audit
    show_integreted_yes = fields.Boolean(string='Show YES', default=False)
    show_integreted_no  = fields.Boolean(string='Show NO', default=False)
    integreted_audit    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Integrated Audit",tracking=True)
    int_review          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Management Review", tracking=True)
    int_internal        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Internal Audit", tracking=True)
    int_policy          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Risk & Opportunity Management", tracking=True)
    int_system          = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Responsibilities", tracking=True)
    int_instruction     = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Procedures", tracking=True)
    int_improvement     = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Work Instructions", tracking=True)
    int_planning        = fields.Selection([('YES', 'YES'),('PARTIAL', 'PARTIAL'),('NO', 'NO')], string="Manual", tracking=True)
    # int_support         = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Supports", )

    # additional iso 14001
    iso_14001_environmental = fields.Text(string="Significant Enviornmental Aspects", tracking=True, default="Limbah Kantor, Kimia, Oli\nKonsumsi listrik, air, solar\nEmisi gas buang, Panas" )
    iso_14001_legal         = fields.Text(string="Specific Relevant Obligations", tracking=True, default="PerMenLHK no.6 / 2021 ttg Limbah B3\nPP No. 22 / 2021 ttg Penyelenggaraan Perlindungan dan Pengelolaan LH")
    # additional iso 45001
    iso_45001_ohs           = fields.Text(string="Significant Hazard / OHS Risks", tracking=True)
    iso_45001_legal         = fields.Text(string="45001 Legal Obligations", tracking=True)

    # additional iso 27001
    iso_27001_total_emp     = fields.Char(string='Total Employee', )
    iso_27001_bisnistype    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    # additional iso 27001:2022
    iso_27001_bisnistype_2022    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_2022       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_2022   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_2022= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_2022         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_2022      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_2022 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_2022    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_2022         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_2022           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    
    # additional iso 27018
    iso_27001_bisnistype_27018    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_27018       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_27018   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_27018= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_27018         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_27018      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_27018 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_27018    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_27018         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_27018           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    
    # additional iso 27017
    iso_27001_bisnistype_27017    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_27017       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_27017   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_27017= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_27017         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_27017      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_27017 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_27017    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_27017         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_27017           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )
    
    # additional iso 27701
    iso_27001_bisnistype_27701    = fields.Selection([
                                ('A', 'Organization works in non-critical business sectors and non-regulated sectors'),
                                ('B', 'Organization has customers in critical business sectors'),
                                ('C', 'Organization works in critical business sectors')
                                ], string='Business type and regulatory requirements', )
    iso_27001_process_27701       = fields.Selection([
                                ('A', 'Standard processes with standard and repetitive tasks; lots of persons doing work under the organization control carrying out the same tasks; few products or services'),
                                ('B', 'Standard but non-repetitive processes, with high number of products or services'),
                                ('C', 'Complex processes, high number of products and services, many business units included in the scope of certification')
                                ], string='Process and Task', )
    iso_27001_mgmt_system_27701   = fields.Selection([
                                ('A', 'ISMS is already well established and/or other management systems are in place'),
                                ('B', 'Some elements of other management systems are implemented, others not'),
                                ('C', 'No other management system implemented at all, the ISMS is new and not established')
                                ], string='Management system establishment level', )
    iso_27001_number_process_27701= fields.Selection([
                                ('A', 'Only one key business process with few interfaces and few business units involved'),
                                ('B', '2–3 simple business processes with few interfaces and few business units involved'),
                                ('C', 'More than 2 complex processes with many interfaces and business units involved')
                                ], string='Number of processes and services', )
    iso_27001_infra_27701         = fields.Selection([
                                ('A', 'Few or highly standardized IT platforms, servers, operating systems, databases, networks, etc'),
                                ('B', 'Several different IT platforms, servers, operating systems, databases, networks'),
                                ('C', 'Many different IT platforms, servers, operating systems, databases, networks')
                                ], string='IT infrastructure complexity', )
    iso_27001_sourcing_27701      = fields.Selection([
                                ('A', 'Little or no dependency on outsourcing or suppliers'),
                                ('B', 'Some dependency on outsourcing or suppliers, related to some but not all important business activities'),
                                ('C', 'High dependency on outsourcing or suppliers, large impact on important business activities')
                                ], string='Dependency on outsourcing and suppliers, including cloud services', )
    iso_27001_itdevelopment_27701 = fields.Selection([
                                ('A', 'None or a very limited in-house system/application development'),
                                ('B', 'Some in-house or outsourced system/application development for some important business purposes'),
                                ('C', 'Extensive in-house or outsourced system/application development for important business purposes')
                                ], string='Information System development', )
    iso_27001_itsecurity_27701    = fields.Selection([
                                ('A', 'Only little sensitive or confidential information, low availability requirements'),
                                ('B', 'Higher availability requirements or some sensitive / confidential information'),
                                ('C', 'Higher amount of sensitive or confidential information or high availability requirements')
                                ], string='	Information security requirements confidentiality, integrity and availability(CIA)')
    iso_27001_asset_27701         = fields.Selection([
                                ('A', 'Few critical assets (in terms of CIA)'),
                                ('B', 'Some critical assets'),
                                ('C', 'Many critical assets')
                                ], string='Number of critical assets', )
    iso_27001_drc_27701           = fields.Selection([
                                ('A', 'Low availability requirements and no or one alternative DR site'),
                                ('B', 'Medium or High availability requirements and no or one alternative DR site'),
                                ('C', 'High availability requirements e.g. 24/7 services, Several alternative DR sites,Several Data Centers')
                                ], string='Number of sites and number of Disaster Recovery (DR) sites', )

    # additional iso 22000:2018 
    iso_22000_hazard_no     = fields.Char(string='Total No of Hazard', tracking=True)
    iso_22000_hazard_desc   = fields.Text(string='Hazard Description', tracking=True)
    iso_22000_process_no    = fields.Char(string='Total No of Process', tracking=True)
    iso_22000_process_desc  = fields.Text(string='Process Description', tracking=True)
    iso_22000_tech_no       = fields.Char(string='Total No of Tech', tracking=True)
    iso_22000_tech_desc     = fields.Text(string='Tech Description', tracking=True)
    
    # multisite 
    site_name               = fields.Char(string='Site Name', tracking=True)
    site_address            = fields.Text(string='Site Address', tracking=True)
    site_emp_total          = fields.Char(string='Total Site Employee', tracking=True)
    site_activity           = fields.Text(string='Site Activity', tracking=True)


    state           =fields.Selection([
                            ('new',         'New'),
                            ('review',      'Review'),
                            ('waiting',     'Waiting Verify'),
                            ('approved',    'Verify Head'),
                            ('approved_head',    'Verify Head'),
                            ('reject',      'Reject'),
                            ('quotation',   'Quotation'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')
    audit_stage = fields.Selection([
                            ('initial',         'Initial Assesment'),
                            ('recertification', 'Recertification'),
                            ('transfer_surveilance',    'Transfer Assesment from Surveilance'),
                            ('transfer_recert',         'Transfer Assesment from Recertification'),
                        ], string='Audit Stage', index=True, tracking=True)

    audit_status = fields.Selection([
        ('program', 'Program'),
        ('Stage-1', 'Stage-1'),
        ('Stage-2', 'Stage-2'),
        ('Surveillance1', 'Surveillance1'),
        ('Surveillance2', 'Surveillance2'),
        ('Recertification', 'Recertification'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status', related="sale_order_id.audit_status", store=True)

    audit_similarities = fields.Selection([
                            ('similar',         'Similar Activities processes'),
                            ('diferences',      'Diferences between Activities'),
                        ], string='Multisite Similarities', index=True, tracking=True)

    lingkup = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, tracking=True)
    kepemilikan = fields.Selection([
                            ('bumn',    'BUMN'),
                            ('individu','INDIVIDU'),
                            ('swasta',  'SWASTA'),
                            ('kud',     'KUD'),
                        ], string='Kepemilikan', index=True, tracking=True)

    count_review        = fields.Integer(string="Count Review", compute="compute_state", store=True,tracking=True)
    count_quotation     = fields.Integer(string="Count Quotation", compute="compute_state", store=True,tracking=True)
    count_sales         = fields.Integer(string="Count Sales", compute="compute_state", store=True,tracking=True)
    count_invoice       = fields.Integer(string="Count Invoice", compute="compute_state", store=True,tracking=True)

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of attached documents",tracking=True)


# ISPO RELATED fields
    permohonan     = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, tracking=True)
    lingkup = fields.Selection([
                            ('kebun',   'KEBUN'),
                            ('pabrik', 'Pabrik'),
                            ('integrasi',  'Integrasi'),
                        ], string='Ruang Lingkup', index=True, tracking=True)
    tipe_tanah = fields.Selection([
                            ('tidak_gambut',   'Tidak Bergambut'),
                            ('gambut', 'Gambut'),
                        ], string='Tipe Tanah', index=True, tracking=True)
    sebaran_tanah = fields.Selection([
                            ('tidak',       'Tidak berbatasan langsung dengan lahan negara/ masyarakat'),
                            ('berbatasan',  'Berbatasan dengan lahan negara/  Kawasan lindung namun terdapat Batasan alam yang jelas'),
                            ('lindung',     'Sebagian atau seluruhnya berada pada Kawasan Linding'),
                        ], string='Sebaran Geografis', index=True, tracking=True)
    tipe_kegiatan = fields.Selection([
                            ('tidak',       'Tidak ada peremajaan'),
                            ('ada',  'Ada peremajaan'),
                        ], string='Tipe Kegiatan', index=True, tracking=True)
    topografi = fields.Selection([
                            ('datar',       'Datar'),
                            ('bukit',  'Berbukit'),
                        ], string='Topografi Tanah', index=True, tracking=True)

    is_kebun_pabrik     = fields.Boolean(string='Kebun / Pabrik', tracking=True)
                        
    legal_lokasi        = fields.Char(string='Ijin Lokasi', tracking=True)
    legal_iup           = fields.Char(string='Ijin IUP', tracking=True)
    legal_spup          = fields.Char(string='Ijin SPUP', tracking=True)
    legal_itubp         = fields.Char(string='Ijin ITBUP', tracking=True)
    legal_prinsip       = fields.Char(string='Ijin Prinsip', tracking=True)
    legal_menteri       = fields.Char(string='Ijin Menteri', tracking=True)
    legal_bkpm          = fields.Char(string='Ijin BKPM', tracking=True)

    perolehan_a         = fields.Char(string='APL', tracking=True)
    perolehan_b         = fields.Char(string='HPK', tracking=True)
    perolehan_c         = fields.Char(string='Tanah Adat', tracking=True)
    perolehan_d         = fields.Char(string='Tanah Lain', tracking=True)

    legal_hgu           = fields.Char(string='HGU / HGB', tracking=True)
    legal_amdal         = fields.Char(string='Izin Lingkungan - AMDAL', tracking=True)

    is_plasma_swadaya   = fields.Boolean(string='Plasma / Swadaya', tracking=True)

    kebun_sertifikat    = fields.Char(string='Sertifikat Tanah', tracking=True)
    kebun_penetapan     = fields.Char(string='Penetapan', tracking=True)
    kebun_std           = fields.Char(string='Surat Tanda Daftar', tracking=True)
    kebun_pembentukan   = fields.Char(string='Pembentukan', tracking=True)
    kebun_konversi      = fields.Char(string='Konversi', tracking=True)
    kebun_kesepakatan   = fields.Char(string='Kesepakatan', tracking=True)

    sertifikat_ispo     = fields.Text(string='Sertifikat ISPO', tracking=True)

    tani_nama           = fields.Char(string='Nama Kelompok Tani', tracking=True)
    tani_adrt           = fields.Char(string='Akta Pendirian', tracking=True)
    tani_pembentukan    = fields.Char(string='Pembentukan Kelompok Tani', tracking=True)
    tani_rko            = fields.Char(string='Rencana Kegiatan', tracking=True)
    tani_kegiatan       = fields.Char(string='Laporan Kegiatan', tracking=True)
    tani_jumlah         = fields.Char(string='Jumlah Petani', tracking=True)
    tani_area           = fields.Char(string='Total Area', tracking=True)
    tani_tertanam       = fields.Char(string='Area Tertanam', tracking=True)
    tani_tbs            = fields.Char(string='Produksi TBS', tracking=True)

    peta_lokasi         = fields.Char(string='Peta Lokasi', tracking=True)

    add_nama_perusahaan = fields.Char(string='Perusahaan Konsultan', tracking=True)
    add_sertifikasi     = fields.Char(string='Sertifikasi Lain', tracking=True)
    add_pic             = fields.Char(string='Personal Perusahaan Yang sudah pelatihan Auditor ISPO', tracking=True)
    add_kendali         = fields.Boolean(string='Tim Kendali Internal', tracking=True)
    add_kendali_jml     = fields.Integer(string='Tim Kendali Internal Jumlah', tracking=True)
    add_auditor         = fields.Boolean(string='Auditor Internal', tracking=True)
    add_auditor_jml     = fields.Integer(string='Auditor Internal Jumlah', tracking=True)

    ispo_kebun          = fields.One2many('tsi.ispo.kebun', 'reference', string="Kebun", index=True, tracking=True)
    ispo_pabrik         = fields.One2many('tsi.ispo.pabrik', 'reference', string="Pabrik", index=True, tracking=True)
    ispo_pemasok        = fields.One2many('tsi.ispo.pemasok', 'reference', string="Pemasok", index=True, tracking=True)
    ispo_sertifikat     = fields.One2many('tsi.ispo.sertifikat', 'reference', string="Sertifikat", index=True, tracking=True)


    mandays_ori_lines   = fields.One2many('tsi.iso.mandays_app', 'reference_id', string="Mandays Original", index=True, tracking=True)
    lines_initial       = fields.One2many('tsi.iso.initial', 'reference_id', string="Lines Initial", index=True, tracking=True)
    lines_surveillance  = fields.One2many('tsi.iso.surveillance', 'reference_id', string="Lines SUrveillance", index=True, tracking=True)
    mandays_pa          = fields.One2many('tsi.iso.mandays.pa_app', 'reference_id', string="PA", index=True, tracking=True)
    mandays_justify     = fields.One2many('tsi.iso.mandays.justification_app', 'reference_id', string="Justification", index=True, tracking=True)

    partner_site        = fields.One2many('tsi.iso.site', 'reference_id', string="Personnel Situation", index=True)

    show_salesinfo      = fields.Boolean(string='Additional Info', default=False)
    salesinfo_site      = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id', string="Additional Info", index=True)
    
    show_14001          = fields.Boolean(string='Show 14001', default=False)    
    iso_14001_env_aspect    = fields.Text(string='Environmental Aspects', tracking=True)
    iso_14001_obligation    = fields.Text(string='14001 Legal Obligation', tracking=True)

    show_45001          = fields.Boolean(string='Show 45001', default=False)    
    iso_45001_key_hazard    = fields.Text(string='Significant Hazard / OHS Risks', tracking=True, default="Bahan Mekanik, Elektrik\nBahaya Api, Ketinggian, Ledakan, Kimia")
    iso_45001_obligation    = fields.Text(string='Specific Relevant Obligations', tracking=True, default="PerMenNaker No.5/2018 ttg K3 Lingkungan Kerja\nPerMenNaker No.8/2020 ttg K3 Pesawat Angkut & Angkat")

    show_27001          = fields.Boolean(string='Show 27001', default=False)
    show_27701          = fields.Boolean(string='Show 27701', default=False) 
    show_27017          = fields.Boolean(string='Show 27017', default=False) 
    show_27018          = fields.Boolean(string='Show 27018', default=False)   
    show_27001_2022          = fields.Boolean(string='Show 27001', default=False)    
    additional_27001    = fields.One2many('tsi.iso.additional_27001', 'reference_id', string="Additional Info for ISO 27001", index=True)
    additional_27701    = fields.One2many('tsi.iso.additional_27001', 'reference_id3', string="Additional Info for ISO 27701", index=True)
    additional_27017    = fields.One2many('tsi.iso.additional_27001', 'reference_id1', string="Additional Info for ISO 27017", index=True)
    additional_27018    = fields.One2many('tsi.iso.additional_27001', 'reference_id2', string="Additional Info for ISO 27018", index=True)

    show_31000          = fields.Boolean(string='Show 31000', default=False)    
    salesinfo_site_31000    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id7', string="Additional Info", index=True)

    show_9994          = fields.Boolean(string='Show 9994', default=False)
    salesinfo_site_9994    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id8', string="Additional Info", index=True)
    
    show_13485        = fields.Boolean(string='Show 13485', default=False)
    show_37301        = fields.Boolean(string='Show 13485', default=False)
    show_smk        = fields.Boolean(string='Show 13485', default=False)
    show_smeta        = fields.Boolean(string='Show SMETA', default=False)
    show_19649        = fields.Boolean(string='Show 19649', default=False)
    show_ce        = fields.Boolean(string='Show CE', default=False)
    show_19650        = fields.Boolean(string='Show 19650', default=False)
    show_196502        = fields.Boolean(string='Show 19650', default=False)
    show_196503        = fields.Boolean(string='Show 19650', default=False)
    show_196504        = fields.Boolean(string='Show 19650', default=False)
    show_196505        = fields.Boolean(string='Show 19650', default=False)
    show_21000        = fields.Boolean(string='Show 13485', default=False)
    show_21001        = fields.Boolean(string='Show 21001', default=False)
    salesinfo_site_13485    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id11', string="Additional Info", index=True)
    salesinfo_site_smeta    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id27', string="Additional Info", index=True)
    salesinfo_site_21001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id26', string="Additional Info", index=True)
    salesinfo_site_19649    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id25', string="Additional Info", index=True)
    salesinfo_site_ce    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id19', string="Additional Info", index=True)
    salesinfo_site_19650    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id20', string="Additional Info", index=True)
    salesinfo_site_196502    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id21', string="Additional Info", index=True)
    salesinfo_site_196503    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id22', string="Additional Info", index=True)
    salesinfo_site_196504    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id23', string="Additional Info", index=True)
    salesinfo_site_196505    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id24', string="Additional Info", index=True)
    ea_code_13485             = fields.Many2one('tsi.ea_code', string="IAF Code", domain=[('name', '=', 'Not Applicable')])
    ea_code_13485_1        = fields.Many2many('tsi.ea_code', 'rel_tsi_iso_ea_13485', string="IAF Code Existing", domain=[('name', '=', 'Not Applicable')])
    accreditation_13485       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_smeta       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_21001       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_19649       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_ce       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_19650       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196502       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196503       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196504       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    accreditation_196505       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    complexity_13485          = fields.Selection([
                            ('Na',  'NA'),
                            ('Limited',   'Limited'),
                            ('Low',   'Low'),
                            ('Medium',   'Medium'),
                            ('High',   'High'),
                        ], string='Complexity', index=True, )
    cause_13485       = fields.Text('Mandatory SNI',)
    notes_13485       = fields.Text('Notes', )
    notes_smeta       = fields.Text('Notes', )
    notes_21001       = fields.Text('Notes', )
    notes_19649       = fields.Text('Notes', )
    notes_ce       = fields.Text('Notes', )
    notes_19650       = fields.Text('Notes', )
    notes_196502      = fields.Text('Notes', )
    notes_196503      = fields.Text('Notes', )
    notes_196504       = fields.Text('Notes', )
    notes_196505       = fields.Text('Notes', )
    show_37001        = fields.Boolean(string='Show 31000', default=False)
    salesinfo_site_37001    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id9', string="Additional Info", index=True)
    accreditation_37001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    notes_37001     = fields.Char('Notes')

    show_22301        = fields.Boolean(string='Show 22301', default=False)
    salesinfo_site_22301    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id16', string="Additional Info", index=True)
    accreditation_22301     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    notes_22301     = fields.Char('Notes')

    akre            = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    specific        = fields.Char(string='Specific Requirements')
    additional      = fields.Char(string='Additional Notes')

    show_haccp          = fields.Boolean(string='Show HACCP', default=False)    
    additional_haccp    = fields.One2many('tsi.iso.additional_haccp', 'reference_id', string="Additional HACCP", index=True)
    #additional HCCp
    hazard_number_site1      = fields.Char(string='Number of hazard', tracking=True)
    hazard_number_site2       = fields.Char(string='Number of hazard', tracking=True)
    hazard_number_site3       = fields.Char(string='Number of hazard', tracking=True)
    hazard_describe_site1     = fields.Char(string='Describe Hazard', tracking=True)
    hazard_describe_site2     = fields.Char(string='Describe Hazard', tracking=True)
    hazard_describe_site3     = fields.Char(string='Describe Hazard', tracking=True)
    process_number_site1      = fields.Char(string='Number of process', tracking=True)
    process_number_site2      = fields.Char(string='Number of process', tracking=True)
    process_number_site3      = fields.Char(string='Number of process', tracking=True)
    process_describe_site1    = fields.Char(string='Describe Process', tracking=True)
    process_describe_site2    = fields.Char(string='Describe Process', tracking=True)
    process_describe_site3    = fields.Char(string='Describe Process', tracking=True)
    tech_number_site1         = fields.Char(string='Number of technology', tracking=True)
    tech_number_site2         = fields.Char(string='Number of technology', tracking=True)
    tech_number_site3         = fields.Char(string='Number of technology', tracking=True)
    tech_describe_site1       = fields.Char(string='Describe Technology', tracking=True)
    tech_describe_site2       = fields.Char(string='Describe Technology', tracking=True)
    tech_describe_site3       = fields.Char(string='Describe Technology', tracking=True)

    show_22000           = fields.Boolean(string='Show 22000', default=False)
    show_fscc           = fields.Boolean(string='Show 22000', default=False)     

    segment_id      = fields.Many2many('res.partner.category', string='Segment', tracking=True)
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Category', index=True, tracking=True)
    declaration     = fields.Text(string='Declaration', tracking=True)
    user_signature  = fields.Binary(string='Signature')

    # Field Selection untuk Legalitas
    legalitas_type = fields.Selection([
        ('integrasi', 'Integrasi'),
        ('kebun', 'Kebun'),
        ('pabrik', 'Pabrik'),
        ('swadaya_plasma', 'Swadaya/Plasma'),
    ], string='Tipe Legalitas')

    # Field-field tambahan untuk Integrasi
    hgu = fields.Char(string='Hak Guna Usaha (HGU)')
    hgb = fields.Char(string='Hak Guna Bangunan (HGB)')
    iup = fields.Char(string='IUP / IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    pup = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun')
    izin_lingkungan_integrasi = fields.Char(string='Izin Lingkungan (Integrasi)')
    luas_lahan = fields.Float(string='Luas Lahan')
    kapasitas_pabrik = fields.Float(string='Kapasitas Pabrik')
    izin_lokasi = fields.Char(string='Izin Lokasi')
    apl = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat')
    risalah_panitia = fields.Char(string='Risalah Panitia A/B')
    lahan_gambut = fields.Char(string='Lahan Gambut / Mineral')
    peta = fields.Char(string='Peta – Peta')

    # Field-field tambahan untuk Kebun
    hgu_kebun = fields.Char(string='Hak Guna Usaha (HGU)')
    iupb = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP')
    izin_lingkungan_kebun = fields.Char(string='Izin Lingkungan')

    # Field-field tambahan untuk Pabrik
    hgb_pabrik = fields.Char(string='Hak Guna Bangunan (HGB)')
    kapasitas_pabrik_pabrik = fields.Float(string='Kapasitas Pabrik')

    # Field-field tambahan untuk Swadaya/Plasma
    shm = fields.Char(string='SHM/Kepemilikan Lahan Yang diakui Pemerintah')
    stdb = fields.Char(string='STDB')
    sppl = fields.Char(string='SPPL')
    akta_pendirian = fields.Char(string='Akta Pendirian dan SK Kemenhumkam')
    kebun_lines       = fields.One2many('tsi.kebun', 'reference', string="Kebun")
    pabrik_lines       = fields.One2many('tsi.pabrik', 'reference', string="Pabrik")
    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    nomor_kontrak = fields.Char(string='Nomor Kontrak', readonly=True)
    status_klien = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='State', store=True, default="New")

    global_status = fields.Char(string="Status Project", compute="_compute_global_status", store=True)
    transport_by        = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Transport By')
    hotel_by            = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Akomodasi Hotel By')

    @api.depends('state')
    def _compute_global_status(self):
        for record in self:
            iso_review = self.env['tsi.iso.review'].search([('reference', '=', record.id)], limit=1)
            audit_notification = self.env['audit.notification'].search([('iso_reference', '=', record.id)], limit=1)

            final_status = False  # Default jika tidak ada kondisi yang cocok

            if not iso_review and not audit_notification:
                if record.state in ['new', 'waiting', 'approved']:
                    final_status = "Application Form or Request"

            elif iso_review and not audit_notification:
                if record.state in ['new', 'waiting', 'approved']:
                    if iso_review.state == 'new':
                        final_status = "Review Penugasan"
                    elif iso_review.state == 'approved':
                        final_status = "Pengiriman Notifikasi"

            elif iso_review and audit_notification:
                status_map = {
                    'draft': "Persetujuan Notifikasi",
                    'plan': "Pengiriman Audit Plan",
                    'program': "Pelaksanaan Audit",
                    'report': "Penyelesaian CAPA",
                    'recommendation': "Pengiriman Draft Sertifikat",
                    'certificate': "Persetujuan Draft Sertifikat",
                    'done': "Kirim Sertifikat",
                }
                final_status = status_map.get(audit_notification.audit_state, False)

            # Simpan status global di model lain
            record.global_status = final_status
            if iso_review:
                iso_review.global_status = final_status
            if audit_notification:
                audit_notification.global_status = final_status

    def compute_state(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.nomor_kontrak:
                rec.nomor_kontrak = rec.sale_order_id.nomor_kontrak
    
    def compute_state(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.state_sales:
                rec.state = rec.sale_order_id.state_sales

    def compute_state(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.audit_status:
                rec.audit_status = rec.sale_order_id.audit_status

    @api.onchange('certification')
    def _onchange_certification(self):
        if self.certification == 'Single Site':
            self.tx_site_count = 1
        elif self.certification == 'Multi Site':
            self.tx_site_count = 0 

    @api.onchange('customer')
    def _onchange_customer(self):
        if self.customer:
            if self.customer.office_address:
                self.office_address = self.customer.office_address;
            if self.customer.contact_person:
                self.contact_person = self.customer.contact_person;
            if self.customer.invoice_address:
                self.invoicing_address = self.customer.invoice_address;
            if self.customer.phone:
                self.telepon = self.customer.phone;
            if self.customer.email:
                self.email = self.customer.email;
            if self.customer.website:
                self.website = self.customer.website;
    
    @api.onchange('show_integreted_yes', 'show_integreted_no')
    def onchange_show_integreted(self):
        if self.integreted_audit == 'YES' and not self.show_integreted_yes:
            self.integreted_audit = False
        elif self.integreted_audit == 'NO' and not self.show_integreted_no:
            self.integreted_audit = False

    @api.onchange('integreted_audit')
    def onchange_integreted_audit(self):
        if self.integreted_audit == 'YES':
            self.show_integreted_yes = True
            self.show_integreted_no = False
        elif self.integreted_audit == 'NO':
            self.show_integreted_yes = False
            self.show_integreted_no = True
    
    # @api.onchange('iso_standard_ids')
    # def _onchange_standards(self):
    #     for obj in self:
    #         if obj.iso_standard_ids :
    #             obj.show_14001 = False
    #             obj.show_45001 = False
    #             obj.show_27001 = False
    #             obj.show_haccp = False
    #             obj.show_22000 = False
    #             obj.show_37001 = False    
    #             obj.show_37301 = False  
    #             obj.show_13485 = False           
    #             obj.show_salesinfo = False
    #             for standard in obj.iso_standard_ids :
    #                 if standard.name == 'ISO 14001' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_14001 = True
    #                 if standard.name == 'ISO 45001' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_45001 = True
    #                 if standard.name == 'ISO 27001' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_27001 = True
    #                 if standard.name == 'ISO 22000' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_22000 = True
    #                 if standard.name == 'ISO 37001' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_37001 = True
    #                 if standard.name == 'ISO 13485' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_13485 = True
    #                 if standard.name == 'ISO 37301:2021' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_37301 = True
    #                 if standard.name == 'HACCP' :
    #                     if obj.show_salesinfo != True :
    #                         obj.show_salesinfo = False
    #                     obj.show_haccp = True
    #                 elif standard.name == 'ISO 9001' :
    #                     obj.show_salesinfo = True

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :
                obj.show_14001 = False
                obj.show_45001 = False
                obj.show_27001 = False
                obj.show_27701 = False
                obj.show_27017 = False
                obj.show_27018 = False
                obj.show_27001_2022 = False
                obj.show_haccp = False
                obj.show_22000 = False
                obj.show_fscc = False
                obj.show_22301 = False
                obj.show_31000 = False
                obj.show_37001 = False
                obj.show_13485 = False
                obj.show_smk = False
                obj.show_smeta = False
                obj.show_19649 = False
                obj.show_ce = False
                obj.show_19650 = False
                obj.show_196502 = False
                obj.show_196503 = False
                obj.show_196504 = False
                obj.show_196505 = False
                obj.show_21000 = False  
                obj.show_21001 = False  
                obj.show_37301 = False
                obj.show_9994 = False
                obj.show_gdp = False
                obj.show_56001 = False
                # obj.show_ispo = False               
                obj.show_salesinfo = False
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISO 14001:2015' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_14001 = True
                    if standard.name == 'ISO 45001:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_45001 = True
                    if standard.name == 'ISO/IEC 27001:2013' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001 = True
                    if standard.name == 'ISO/IEC 27001:2022' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001_2022 = True
                    if standard.name == 'ISO/IEC 27701:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27701 = True
                    if standard.name == 'ISO/IEC 27017:2015' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27017 = True
                    if standard.name == 'ISO/IEC 27018:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27018 = True
                    if standard.name == 'ISO 22000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22000 = True
                    if standard.name == 'FSCC 22000' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_fscc = True
                    if standard.name == 'ISO 22301:2019' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22301 = True
                    if standard.name == 'HACCP' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_haccp = True
                    if standard.name == 'ISO 31000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_31000 = True
                    if standard.name == 'ISO 13485:2016' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_13485 = True
                    if standard.name == 'ISO 37301:2021' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_37301 = True
                    if standard.name == 'ISO 9994:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_9994 = True
                    if standard.name == 'GDP' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_gdp = True
                    if standard.name == 'ISO 56001:2024' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_56001 = True
                    if standard.name == 'ISO 37001:2016' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_37001 = True
                    if standard.name == 'SMK3' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_smk = True
                    if standard.name == 'IATF 16949' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_19649 = True
                    if standard.name == 'CE Marking' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_ce = True
                    if standard.name == 'ISO 19650:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_19650 = True
                    if standard.name == 'ISO 19650-2:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196502 = True
                    if standard.name == 'ISO 19650-3:2020' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196503 = True
                    if standard.name == 'ISO 19650-4:2022' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196504 = True
                    if standard.name == 'ISO 19650-5:2020' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_196505 = True
                    if standard.name == 'ISO 21000:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_21000 = True
                    if standard.name == 'ISO 21001:2018' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_21001 = True
                    if standard.name == 'SMETA' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_smeta = True
                    # if standard.name == 'ISPO' :
                    #     if obj.show_ispo != True :
                    #         obj.show_ispo = False
                    #     obj.show_ispo = True
                    elif standard.name == 'ISO 9001:2015' :
                        obj.show_salesinfo = True
                    #else :
                    #    obj.show_salesinfo = True

    # @api.depends('name')
    # def _compute_state(self):
    #     for record in self:
    #         if record.id:
    #             sale_order = self.env['sale.order'].search([
    #                 ('iso_reference', '=', record.name)
    #             ], limit=1)

    #             if sale_order:
    #                 record.state_sales = sale_order.state
    #             else:
    #                 record.state_sales = False

    @api.depends('leads_selection')
    def _compute_show_leads_description(self):
        for record in self:
            record.show_leads_description = record.leads_selection in ['eksternal', 'internal']

    # @api.depends('name')
    # def _compute_audit_status(self):
    #     for record in self:
    #         if record.id:
    #             sale_order = self.env['sale.order'].search([
    #                 ('iso_reference', '=', record.name),
    #                 ('state', '=', 'sale')
    #             ], limit=1)

    #             record.audit_status = sale_order.audit_status if sale_order else False

    def _compute_attached_docs_count(self):
        attachment_obj = self.env['ir.attachment']
        for task in self:
            task.doc_count = attachment_obj.search_count([
                '&', ('res_model', '=', 'tsi.iso'), ('res_id', '=', task.id)
            ])

    def attached_docs_view_action(self):
        self.ensure_one()
        domain = [
            '&', ('res_model', '=', 'tsi.iso'), ('res_id', 'in', self.ids),
        ]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks of your project.</p>
                    '''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.depends('customer')
    def compute_state(self):
        for obj in self:
            if obj.id :
                review = self.env['tsi.iso.review'].search_count([('reference.id', '=', obj.id)])
                if review :
                    obj.count_review = review

                # count_quotation = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'draft')])
                # if count_quotation :
                #     obj.count_quotation = count_quotation

                obj.count_quotation = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id), ('state', '=', 'draft')]) 

                count_sales     = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'sale')])
                if count_sales :
                    obj.count_sales = count_sales

                count_invoice   = self.env['account.move'].search_count([('iso_reference.id', '=', obj.id)])
                if count_invoice :
                    obj.count_invoice = count_invoice


                # obj.count_review    = self.env['tsi.iso.review'].search_count([('reference.id', '=', obj.id)])
                # obj.count_quotation = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id)])
                # obj.count_sales     = self.env['sale.order'].search_count([('iso_reference.id', '=', obj.id),('state', '=', 'sale')])
                # obj.count_invoice   = self.env['account.move'].search_count([('iso_reference.id', '=', obj.id)])

                # obj.count_patrol = self.env['kontrak.checkpoint'].search_count([('id', 'in', obj.check_lines.ids)])

    def get_iso_review(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Review',
                'view_mode': 'tree,form',
                'res_model': 'tsi.iso.review',
                'domain': [('reference', '=', self.id)],
                'context': "{'create': True}"
            }

    def get_iso_quotation(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Quotation',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': [('iso_reference', '=', self.id)],
                'context': "{'create': True}"
            }

    def get_iso_sales(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sales',
                'view_mode': 'tree,form',
                'res_model': 'sale.order',
                'domain': [('iso_reference', '=', self.id),('state', '=', 'sale')],
                'context': "{'create': True}"
            }

    def get_iso_invoice(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Review',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('iso_reference', '=', self.id)],
                'context': "{'create': True}"
            }

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.iso')
        vals['name'] = sequence or _('New')

        if 'customer' not in vals:
            partner = self.env['res.partner'].search([('name', '=', vals.get('company_name'))])
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': vals['company_name'],
                    'company_type': 'company'
                })
            vals['customer'] = partner.id

  
        record = super(ISO, self).create(vals)
        record.update_pic()
        record.update_franchise_contacts()
        record.update_associate_contacts()
        record.update_to_contact()
        return record

    def write(self, vals):
        res = super(ISO, self).write(vals)
        self.update_pic()
        self.update_franchise_contacts()
        self.update_associate_contacts()
        self.update_to_contact()
        return res
    
    def unlink(self):
        for record in self:
            record.delete_franchise_contacts()
            record.delete_associate_contacts()
            record.delete_pic()
        return super(ISO, self).unlink()

    def update_pic(self):
        for record in self:
            if record.pic_id:
                update_pic_vals = {
                    'partner_id': record.customer.id,
                    'name_client': record.pic_id.id,
                    'address_client': record.pic_id.office_address,
                    'phone_client': record.pic_id.phone,
                    'email_client': record.pic_id.email,
                    'jabatan': record.pic_id.function,
                }
                update_pic_customer = self.env['res.partner.contact.client'].search([
                    ('partner_id', '=', record.customer.id),
                    ('name_client', '=', record.pic_id.id),
                ], limit=1)
                if update_pic_customer:
                    update_pic_customer.write(update_pic_vals)
                    
                else:
                    self.env['res.partner.contact.client'].create(update_pic_vals)
    
    def update_associate_contacts(self):
        for record in self:
            if record.associate_id:
                contact_vals = {
                    'partner_ids': record.associate_id.id,
                    'name_associates': record.customer.id,
                    'address_associates': record.customer.office_address,
                    'phone_associates': record.phone_associate,
                    'email_associates': record.email_associate,
                }
                contact_associate = self.env['res.partner.custom.contacts'].search([
                    ('partner_ids', '=', record.associate_id.id),
                    ('name_associates', '=', record.customer.id),
                ], limit=1)

                if contact_associate:
                    contact_associate.write(contact_vals)
                else:
                    # self.env['res.partner.custom.contacts'].create(contact_vals)
                    contact_associate = self.env['res.partner.custom.contacts'].create(contact_vals)
                    
                update_contact_vals = {
                    'partner_ids': record.customer.id,
                    'name_associates': record.associate_id.id,
                    'address_associates': record.associate_id.office_address,
                    'phone_associates': record.phone_associate,
                    'email_associates': record.email_associate,
                }
                update_contact_customer = self.env['res.partner.custom.contacts'].search([
                    ('partner_ids', '=', record.customer.id),
                    ('name_associates', '=', record.associate_id.id),
                ], limit=1)
                if update_contact_customer:
                    update_contact_customer.write(update_contact_vals)
                    
                else:
                    self.env['res.partner.custom.contacts'].create(update_contact_vals)


    def update_franchise_contacts(self):
        for record in self:
            if record.franchise_id:
                contact_vals = {
                    'partner_id': record.franchise_id.id,
                    'name_franchise': record.customer.id,
                    'address_franchise': record.customer.office_address,
                    'phone_franchise': record.phone_franchise,
                    'email_franchise': record.email_franchise,
                }
                self.customer.write({'contact_client': True})
                self.customer.write({'is_franchise': True})
                self.customer.write({'is_associate': True})
                self.customer.write({'pic_id': True})
                self.franchise_id.write({'contact_client': False})
                
                contact_franchise = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.franchise_id.id),
                    ('name_franchise', '=', record.customer.id),
                ], limit=1)

                if contact_franchise:
                    contact_franchise.write(contact_vals)
                    
                else:
                    self.env['res.partner.contact.franchise'].create(contact_vals)
                    
                update_contact_vals = {
                    'partner_id': record.customer.id,
                    'name_franchise': record.franchise_id.id,
                    'address_franchise': record.franchise_id.office_address,
                    'phone_franchise': record.phone_franchise,
                    'email_franchise': record.email_franchise,
                }
                update_contact_customer_fr = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.customer.id),
                    ('name_franchise', '=', record.franchise_id.id),
                ], limit=1)

                if update_contact_customer_fr:
                    update_contact_customer_fr.write(update_contact_vals)
                else:
                    self.env['res.partner.contact.franchise'].create(update_contact_vals)
                    
    def delete_associate_contacts(self):
        for record in self:
            if record.associate_id:
                contact_associate = self.env['res.partner.custom.contact'].search([
                    ('partner_id', '=', record.associate_id.id),
                    ('name_associate', '=', record.customer.id),
                ], limit=1)
                if contact_associate:
                    contact_associate.unlink()

    def delete_franchise_contacts(self):
        for record in self:
            if record.franchise_id:
                contact_franchise = self.env['res.partner.contact.franchise'].search([
                    ('partner_id', '=', record.franchise_id.id),
                    ('name_franchise', '=', record.customer.id),
                ], limit=1)
                if contact_franchise:
                    contact_franchise.unlink()

    def delete_pic(self):
        for record in self:
            if record.pic_id:
                pic = self.env['res.partner.contact.client'].search([
                    ('partner_id', '=', record.pic_id.id),
                    ('name_client', '=', record.customer.id),
                ], limit=1)
                if pic:
                    pic.unlink()

    def create_open_iso(self):
        if self.iso_standard_ids :
            for standard in self.iso_standard_ids :

                self.env['tsi.iso.review'].create({
                    'reference'         : self.id,
                    'certification'     : self.certification,
                    'doctype'           : self.doctype,
                    'iso_standard_ids'  : standard,
                    # 'total_emp'         : self.total_emp,          
                    # 'site_office'       : self.site_office,     
                    # 'off_location'      : self.off_location,   
                    # 'head_office'       : self.head_office,        
                    # 'number_site'       : self.number_site,
                    # 'scope'             : self.scope,
                    'website'           : self.website,
                    'office_address'    : self.office_address,
                    'invoicing_address' : self.invoicing_address,
                    'contact_person'    : self.contact_person,
                    'jabatan'           : self.jabatan,
                    'telepon'           : self.telepon,
                    'fax'               : self.fax,
                    'tx_site_count'     : self.tx_site_count,
                    'tx_remarks'        : self.tx_remarks,
                    'email'             : self.email,
                    'cellular'          : self.cellular,
                    # 'boundaries'        : self.boundaries,
                    'cause'             : self.cause,
                    'stage_audit'       : self.audit_stage,
                    'part_time'         : self.part_time,
                    'subcon'            : self.subcon,
                    'unskilled'         : self.unskilled,
                    'seasonal'          : self.seasonal,
                    'shift_number'      : self.shift_number,
                    'outsource_proc'    : self.outsource_proc,
                    'outsourced_activity': self.outsourced_activity,
                    'start_implement'   : self.start_implement,
                    'mat_consultancy'   : self.mat_consultancy,
                    'mat_certified'     : self.mat_certified,
                    'other_system'     : self.other_system,
                    # 'mat_certified_cb'  : self.mat_certified_cb,
                    # 'mat_tools'         : self.mat_tools,
                    # 'mat_national'      : self.mat_national,
                    # 'mat_more'          : self.mat_more,
                    'txt_mat_consultancy': self.txt_mat_consultancy,
                    'txt_mat_certified' : self.txt_mat_certified,
                    # 'txt_mat_certified_cb': self.txt_mat_certified_cb,
                    # 'txt_mat_tools'     : self.txt_mat_tools,
                    # 'txt_mat_national'  : self.txt_mat_national,
                    # 'txt_mat_more'      : self.txt_mat_more,
                    'int_review'        : self.int_review,
                    'int_internal'      : self.int_internal,
                    'int_policy'        : self.int_policy,
                    'int_system'        : self.int_system,
                    'int_instruction'   : self.int_instruction,
                    'int_improvement'   : self.int_improvement,
                    'int_planning'      : self.int_planning,
                    # 'int_support'       : self.int_support,
                    'ea_code'           : self.ea_code.id,
                    'accreditation'     : self.accreditation.id,
                    'ea_code_14001'     : self.ea_code_14001.id,
                    'accreditation_14001' : self.accreditation_14001.id,
                    'ea_code_27001'           : self.ea_code_27001.id,
                    'accreditation_27001'     : self.accreditation_27001.id,
                    'ea_code_45001'           : self.ea_code_45001.id,
                    'accreditation_45001'     : self.accreditation_45001.id,
                    'ea_code_22000'           : self.ea_code_22000.id,
                    'accreditation_22000'     : self.accreditation_22000.id,
                    'ea_code_haccp'           : self.ea_code_haccp.id,
                    'accreditation_haccp'     : self.accreditation_haccp.id,
                    'complexity_22000'  : self.complexity_22000,
                    'complexity'        : self.complexity,
                    'complexity_14001'  : self.complexity_14001,
                    'complexity_27001'  : self.complexity_27001,
                    'complexity_45001'  : self.complexity_45001,
                    'complexity_haccp'  : self.complexity_haccp,
                    'show_salesinfo'    : self.show_salesinfo,
                    'show_14001'        : self.show_14001,
                    'show_45001'        : self.show_45001,
                    'show_27001'        : self.show_27001,
                    'show_haccp'        : self.show_haccp,
                    'show_22000'        : self.show_22000,
                    'show_37001'        : self.show_37001,
                    # 'iso_27001_bisnistype' : self.iso_27001_bisnistype,
                    # 'iso_27001_process' : self.iso_27001_process,
                    # 'iso_27001_mgmt_system' : self.iso_27001_mgmt_system,
                    # 'iso_27001_number_process' : self.iso_27001_number_process,
                    # 'iso_27001_infra'  : self.iso_27001_infra,
                    # 'iso_27001_sourcing'  : self.iso_27001_sourcing,
                    # 'iso_27001_itdevelopment'  : self.iso_27001_itdevelopment,
                    # 'iso_27001_itsecurity'  : self.iso_27001_itsecurity,
                    # 'iso_27001_asset'  : self.iso_27001_asset,
                    # 'iso_27001_drc'  : self.iso_27001_drc,
                    'iso_14001_env_aspect' : self.iso_14001_env_aspect,
                    'iso_14001_obligation' : self.iso_14001_obligation,
                    'iso_45001_key_hazard' : self.iso_45001_key_hazard,
                    'iso_45001_obligation' : self.iso_45001_obligation,
                    'show_integreted_yes'  : self.show_integreted_yes,
                    'integreted_audit'    : self.integreted_audit

                })
        self.compute_state()

    def create_open_quotation(self):

        self.env['sale.order'].create({
            'iso_reference' : self.id,
            'partner_id' : self.customer.id,
        })
        self.compute_state()

    	# return {
        #     'res_model':'tsi.iso.review',
        #     'res_id':self.id,
        #     'type':'ir.actions.act_window',
        #     'view_mode':'form',
        #     'view_id':self.env.ref('v15_tsi.tsi_iso_review_view_form').id,
        # }



    
        
        
    def update_to_contact(self):
        # Calculate total_emp from partner_site
        total_emp = sum(int(site.total_emp) for site in self.partner_site)

        # Determine EA Codes to use
        ea_codes = []
        if self.ea_code:
            ea_codes.append(self.ea_code.id)
        if self.ea_code_14001:
            ea_codes.append(self.ea_code_14001.id)
        if self.ea_code_27001:
            ea_codes.append(self.ea_code_27001.id)
        if self.ea_code_45001:
            ea_codes.append(self.ea_code_45001.id)

        # Update contact information in self.customer
        self.customer.write({
            'phone': self.telepon,
            'office_address': self.office_address,
            'invoice_address': self.invoicing_address,
            'website': self.website,
            'email': self.email,
            'boundaries': self.boundaries,
            'scope': self.scope,
            'number_site': self.tx_site_count,
            'kategori': self.kategori,
            # 'jabatan': self.jabatan,
            'is_associate': self.is_associate,
            'is_franchise': self.is_franchise,
            'category_id': self.segment_id,
            'total_emp': total_emp,
            'contact_person': self.contact_person,
            'user_id': self.sales_person.id,
            'ea_code_ids': [(6, 0, ea_codes)],  # Set many2many field
            'status_klien': self.status_klien,
        })

        # Update or create site lines in tsi.site_partner
        site_partner_obj = self.env['tsi.site_partner']
        for site in self.partner_site:
            existing_site = site_partner_obj.search([('partner_id', '=', self.customer.id), ('jenis', '=', site.type)])
            values = {
                'partner_id': self.customer.id,
                'jenis': site.type,
                'alamat': site.address,
                'telp': site.reference_id.telepon,
                'jumlah_karyawan': int(site.total_emp or 0),
            }
            if existing_site:
                existing_site.write(values)
            else:
                site_partner_obj.create(values)

        return True

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_quotation.app',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_quotation_app_view').id,
            'target': 'new'
        }
    
    def set_to_running(self):
        self.write({'state': 'waiting'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
        })
        return action

    # def set_to_head(self):
    #     self.write({'state': 'waiting'})
    #     self.ensure_one()
    #     action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
    #     action.update({
    #         'context': {'default_customer': self.customer.id},
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
    #         'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
    #     })
    #     return action

    def set_to_closed(self):
        # self.create_open_iso()
        self.write({'state': 'approved'}) 
        # self.ensure_one()
        # action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
        # action.update({
        #     'context': {'default_customer': self.customer.id},
        #     'view_mode': 'form',
        #     'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
        #     'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
        # })
        return True

    def set_to_draft(self):
        self.write({'state': 'reject'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_view_tree').id, 'tree')],
        })
        return action
    
    def send_whatsapp_status_review_revice(self):
        data_revice = self.env['tsi.iso.review'].sudo().search([("reference", "=", self.id)], limit=1)
        dokumen_id = data_revice.ids
        nama_dokumen = data_revice.name
        nama_customer = data_revice.customer.name
        standard = data_revice.iso_standard_ids.name
        stage_audit_map = {
            'initial': 'Initial Assesment',
            'recertification': 'Recertification',
            'transfer_surveilance': 'Transfer Assesment from Surveilance',
            'transfer_recert': 'Transfer Assesment from Recertification',
        }

        tahap_audit = data_revice.stage_audit
        tahap_audit_label = stage_audit_map.get(tahap_audit, 'Unknown')
        
        user = self.env['res.users'].search([("id", "=", 18)])
        nomor = user.sudo().employee_ids.phone_wa 
        
        url = "web#id=%s&menu_id=751&action=985&model=tsi.iso.review&view_type=form" % (dokumen_id)
        payload = {
                "messaging_product": "whatsapp",
                "to": nomor,
                "type": "template",
                "template": {
                    "name": "template_notif_revice_review_url_draf",
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": nama_dokumen
                                },
                                {
                                    "type": "text",
                                    "text": nama_customer
                                },
                                {
                                    "type": "text",
                                    "text": standard
                                },
                                {
                                    "type": "text",
                                    "text": tahap_audit_label
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "url",
                            "index": 0,
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": url
                                }
                            ]
                        }
                    ]
                }
            }

        url = 'https://graph.facebook.com/v21.0/426469107220591/messages'
        access_token = 'EAAOT6dJD7ZBMBOzdC9eranvzlc4SbFM5RmZCIsKaKyWMKNFZBqmPHQNTZAMop4WcjPMOyuNl8tAlBsM9zi6S5LG7Jys58HXPvqXcMbndmP0mlcBHJz6o3lKKFGmI5CTbWo3o3ZBpN6cqEjbLYUmII2U0LZAshv48ZAiSNKKaXzlZAXY13oCkYBtEEk8JkHaZCbWPskgZDZD'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                _logger.info("WhatsApp message sent successfully.")
                
            else:
                _logger.error("Failed to send WhatsApp message: %s", response.text)
        except Exception as e:
            _logger.exception("An error occurred while sending WhatsApp message: %s", e)


    def set_to_revice(self):
        # Update record ini (utama)
        self.write({
            'state': 'approved',
            'state_sales': 'waiting_verify_operation',
        })

        # Kirim notifikasi WhatsApp
        self.send_whatsapp_status_review_revice()

        # Cari dan update semua review customer terkait
        review_records = self.env['tsi.iso.review'].search([
            ('customer', '=', self.customer.id)
        ])

        review_records.write({
            'state': 'revice',
            'state_sales': 'waiting_verify_operation',
        })

        return True


    def set_to_quotation(self):
        self.write({'state': 'quotation'})            
        return True

    def update_program_aktual(self):
        # Dictionary yang mencocokkan field salesinfo dengan nama ISO
        sales_info_iso_mapping = {
            'salesinfo_site': 'ISO 9001',
            'salesinfo_site_14001': 'ISO 14001',
            'salesinfo_site_27001': 'ISO 27001',
            'salesinfo_site_45001': 'ISO 45001',
            'salesinfo_site_22000': 'ISO 22000',
            'salesinfo_site_haccp': 'HACCP'
        }

        for salesinfo_field, iso_name in sales_info_iso_mapping.items():
            # Dapatkan informasi dari masing-masing field salesinfo
            info = getattr(self, salesinfo_field)
            
            if not info:
                continue

            # Cari semua record ops.program berdasarkan customer
            programs = self.env['ops.program'].search([('customer', '=', self.customer.id)])

            for program in programs:
                # Cari ISO standard yang cocok dengan iso_name di setiap ops.program yang ditemukan
                iso_standard = program.iso_standard_ids.filtered(lambda r: r.name == iso_name)
                
                if iso_standard:
                    # Jika ada stage 1, create program aktual untuk stage 1
                    if info.stage_1:
                        self._create_program_aktual(program, info.stage_1, 'Stage-01', iso_standard)

                    # Jika ada stage 2, create program aktual untuk stage 2
                    if info.stage_2:
                        self._create_program_aktual(program, info.stage_2, 'Stage-02', iso_standard)

                # Menambahkan pesan di chatter setelah update
                self.message_post(body=f'Updated ops.program.aktual records for customer {self.customer.name} and ISO {iso_name}')

    def _create_program_aktual(self, program, mandays_value, audit_type, iso_standard):
        # Membuat record di ops.program.aktual dengan menambahkan iso_standard_ids
        # self.env['ops.program.aktual'].create({
        #     'reference_id': program.id,
        #     'mandayss': mandays_value,
        #     'audit_type': audit_type,
        # })

        existing_record = self.env['ops.program.aktual'].search([
            ('reference_id', '=', program.id),
            ('audit_type', '=', audit_type)
        ], limit=1)

        if existing_record:
            # Update record yang sudah ada
            existing_record.write({
                'mandayss': mandays_value,
                'audit_type': audit_type
            })
        else:
            # Buat record baru jika tidak ada yang sesuai
            self.env['ops.program.aktual'].create({
                'reference_id': program.id,
                'mandayss': mandays_value,
                'audit_type': audit_type,
            })




class ISPOKebun(models.Model):
    _name           = 'tsi.ispo.kebun'
    _description    = 'ISPO Kebun'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference       = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    name            = fields.Char(string='Nama Kebun', tracking=True)
    lokasi          = fields.Text(string='Lokasi', tracking=True)
    karyawan        = fields.Char(string='Jumlah Karyawan', tracking=True)
    luas            = fields.Char(string='Luas HGU', tracking=True)
    tahun_tanam     = fields.Char(string='Tahun Tanam', tracking=True)
    keterangan      = fields.Text(string='Keterangan', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISPOKebun, self).create(vals)
        partner = record.reference
        partner.message_post(body=f"Created Nama Kebun: {record.name}, Lokasi: {record.lokasi}, Jumlah Karyawan: {record.karyawan}, Luas HGU: {record.luas}, Tahun Tanam: {record.tahun_tanam}, Keterangan: {record.keterangan}")
        return record

    def write(self, vals):
        res = super(ISPOKebun, self).write(vals)
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Updated Nama Kebun: {record.name}, Lokasi: {record.lokasi}, Jumlah Karyawan: {record.karyawan}, Luas HGU:{record.luas}, Tahun Tanam: {record.tahun_tanam}, Keterangan: {record.keterangan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Deleted Nama Kebun: {record.name}, Lokasi: {record.lokasi}, Jumlah Karyawan: {record.karyawan}, Luas HGU:{record.luas}, Tahun Tanam: {record.tahun_tanam}, Keterangan: {record.keterangan}")
        return super(ISPOKebun, self).unlink()

class ISPOPabrik(models.Model):
    _name           = 'tsi.ispo.pabrik'
    _description    = 'ISPO Pabrik'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference       = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    name            = fields.Char(string='Nama Pabrik', tracking=True)
    lokasi          = fields.Text(string='Lokasi', tracking=True)
    karyawan        = fields.Char(string='Jumlah Karyawan', tracking=True)
    luas            = fields.Char(string='Koordinat GPS', tracking=True)
    tahun_tanam     = fields.Char(string='Kapasitas', tracking=True)
    keterangan      = fields.Text(string='Volume Tahunan', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISPOPabrik, self).create(vals)
        partner = record.reference
        partner.message_post(body=f"Created Nama Pabrik: {record.name}, Lokasi: {record.lokasi}, Jumlah Karyawan: {record.karyawan}, Koordinat GPS:{record.luas}, Kapasitas: {record.tahun_tanam}, Volume Tahunan: {record.keterangan}")
        return record

    def write(self, vals):
        res = super(ISPOPabrik, self).write(vals)
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Updated Nama Pabrik: {record.name}, Lokasi: {record.lokasi}, Jumlah Karyawan: {record.karyawan}, Koordinat GPS:{record.luas}, Kapasitas: {record.tahun_tanam}, Volume Tahunan: {record.keterangan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Deleted Nama Pabrik: {record.name}, Lokasi: {record.lokasi}, Jumlah Karyawan: {record.karyawan}, Koordinat GPS:{record.luas}, Kapasitas: {record.tahun_tanam}, Volume Tahunan: {record.keterangan}")
        return super(ISPOPabrik, self).unlink()

# class ISPOSertifikat(models.Model):
#     _name           = 'tsi.ispo.sertifikat'
#     _description    = 'ISPO Sertifikat'
#     _inherit = ['mail.thread', 'mail.activity.mixin']

#     reference       = fields.Many2one('tsi.iso', string="Reference", tracking=True)
#     name            = fields.Char(string='Nama Sertifikat', tracking=True)
#     nomor           = fields.Char(string='Nomor Sertifikat', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISPOSertifikat, self).create(vals)
        partner = record.reference
        partner.message_post(body=f"Created Nama Sertifikat: {record.name}, Nomor Sertifikat: {record.nomor}")
        return record

    def write(self, vals):
        res = super(ISPOSertifikat, self).write(vals)
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Updated Nama Sertifikat: {record.name}, Nomor Sertifikat: {record.nomor}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Deleted Nama Sertifikat: {record.name}, Nomor Sertifikat: {record.nomor}")
        return super(ISPOSertifikat, self).unlink()

class ISOLineInitial(models.Model):
    _name = 'tsi.iso.initial'
    _description = 'ISO Line Initial'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    reference_id_ispo    = fields.Many2one('tsi.ispo', string="Reference")
    product_id = fields.Many2one(
        'product.product', string='Product',)
    audit_stage     = fields.Selection([
                            ('Initial Audit',         'Initial Audit'),
                            ('Recertification', 'Recertification'),],
                            string='Audit Stage', index=True, )
    price = fields.Float(string='Price')
    tahun = fields.Char("Tahun")
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    in_pajak = fields.Boolean("Include Pajak")
    ex_pajak = fields.Boolean("Exclude Pajak")

    @api.onchange('in_pajak', 'ex_pajak')
    def _onchange_pajak(self):
        for rec in self:
            # Cegah dua checkbox aktif bersamaan
            if rec.in_pajak and rec.ex_pajak:
                rec.ex_pajak = False  # Biar gak bentrok logika

            # Kalau in_pajak dicentang → hitung harga tanpa pajak
            if rec.in_pajak:
                rec.price = rec.price / 1.11 if rec.price else 0.0

            # Kalau ex_pajak dicentang → tidak ubah price (anggap sudah harga asli)
            elif rec.ex_pajak:
                pass  # Harga tetap

            # Kalau dua-duanya gak dicentang → anggap harga asli
            elif not rec.in_pajak and not rec.ex_pajak:
                pass  # Harga tetap

    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for line in self:
            if line.fee:
                line.percentage = line.fee /(line.price - line.fee) 
            else:
                line.percentage = 0

    # def _update_sale_order_lines(self):
    #     for record in self:
    #         # Ambil nama perusahaan dari `tsi.iso`
    #         company_name = record.reference_id.customer.name
            
    #         # Cari sale.order.line yang terkait
    #         sale_order_lines = self.env['sale.order.line'].search([
    #             ('order_id.partner_id.name', '=', company_name)
    #         ])
    #         sale_order_lines.write({
    #             'audit_tahapan': record.audit_stage,
    #             'price_unit': record.price
    #         })

    @api.model
    def create(self, vals):
        record = super(ISOLineInitial, self).create(vals)

        # Post message to reference_id (tsi.iso)
        if record.reference_id:
            record.reference_id.message_post(
                body=f"Created Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
            )

        # Post message to reference_id_ispo (tsi.ispo) if it exists
        if record.reference_id_ispo:
            record.reference_id_ispo.message_post(
                body=f"Created Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
            )

        return record

    def write(self, vals):
        res = super(ISOLineInitial, self).write(vals)
        for record in self:
            # Post message to reference_id (tsi.iso)
            if record.reference_id:
                record.reference_id.message_post(
                    body=f"Updated Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

            # Post message to reference_id_ispo (tsi.ispo) if it exists
            if record.reference_id_ispo:
                record.reference_id_ispo.message_post(
                    body=f"Updated Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

        return res

    def unlink(self):
        for record in self:
            # Post message to reference_id (tsi.iso)
            if record.reference_id:
                record.reference_id.message_post(
                    body=f"Deleted Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

            # Post message to reference_id_ispo (tsi.ispo) if it exists
            if record.reference_id_ispo:
                record.reference_id_ispo.message_post(
                    body=f"Deleted Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

        return super(ISOLineInitial, self).unlink()

class ISOLinesSurveillance(models.Model):
    _name           = 'tsi.iso.surveillance'
    _description    = 'ISO Line Surveillance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('tsi.iso', string="Reference")
    reference_id_ispo    = fields.Many2one('tsi.ispo', string="Reference")
    audit_stage     = fields.Selection([
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),],
                            string='Audit Stage', index=True, )
    audit_stage_ispo     = fields.Selection([
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),],
                            string='Audit Stage', index=True, )
    price = fields.Float(string='Price')
    tahun = fields.Char("Tahun")
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)
    hidden_in_review = fields.Boolean(string='Hidden in Review', default=True)

    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for line in self:
            if line.price > line.fee:
                line.percentage = line.fee / (line.price - line.fee)
            else:
                line.percentage = 0

    @api.model
    def create(self, vals):
        record = super(ISOLinesSurveillance, self).create(vals)

        # Post message to reference_id (tsi.iso)
        if record.reference_id:
            record.reference_id.message_post(
                body=f"Created Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
            )

        # Post message to reference_id_ispo (tsi.ispo) if it exists
        if record.reference_id_ispo:
            record.reference_id_ispo.message_post(
                body=f"Created Audit Stage: {record.audit_stage_ispo}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
            )

        return record

    def write(self, vals):
        res = super(ISOLinesSurveillance, self).write(vals)
        for record in self:
            # Post message to reference_id (tsi.iso)
            if record.reference_id:
                record.reference_id.message_post(
                    body=f"Updated Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

            # Post message to reference_id_ispo (tsi.ispo) if it exists
            if record.reference_id_ispo:
                record.reference_id_ispo.message_post(
                    body=f"Updated Audit Stage: {record.audit_stage_ispo}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

        return res

    def unlink(self):
        for record in self:
            # Post message to reference_id (tsi.iso)
            if record.reference_id:
                record.reference_id.message_post(
                    body=f"Deleted Audit Stage: {record.audit_stage}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

            # Post message to reference_id_ispo (tsi.ispo) if it exists
            if record.reference_id_ispo:
                record.reference_id_ispo.message_post(
                    body=f"Deleted Audit Stage: {record.audit_stage_ispo}, Price: {record.price}, Fee: {record.fee}, Percentage: {record.percentage}"
                )

        return super(ISOLinesSurveillance, self).unlink()

class ISOAccreditation(models.Model):
    _name           = 'tsi.iso.accreditation'
    _description    = 'Accreditation'

    name            = fields.Char(string='Name', tracking=True)
    description     = fields.Char(string='Description', tracking=True)
    active = fields.Boolean(string="Active", default=True)

    def action_archive(self):
        self.write({'active': False})

    def action_unarchive(self):
        self.write({'active': True})

class ISOSite(models.Model):
    _name           = 'tsi.iso.site'
    _description    = 'Site'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    nama_site       = fields.Char(string='Nama Site')
    type            = fields.Char(string='Type(HO, Factory etc)', tracking=True)
    address         = fields.Char(string='Address', tracking=True)
    product         = fields.Char(string='Product / Process / Activities', tracking=True)
    permanent       = fields.Char(string='Permanent & Contract', tracking=True)
    total_active    = fields.Char(string='Total No. of Active Temporary Project Sites (see attachment for detai)', tracking=True)
    total_emp       = fields.Integer(string='Total No. of Effective Employees', tracking=True)
    emp_total       = fields.Integer(string='Total No. of All Employees')
    # part_time       = fields.Char(string='Part-time (4 hours / day)')
    subcon          = fields.Char(string='Subcontractor', tracking=True)
    other           = fields.Char(string='Others', tracking=True)
    remarks         = fields.Char(string='Remark', tracking=True)
    # unskilled       = fields.Char(string='Unskilled Temporary')
    # seasonal        = fields.Char(string='Seasonal Workers')
    non_shift       = fields.Char(string='Non shift', tracking=True)
    shift1          = fields.Char(string='Shift 1', tracking=True)
    shift2          = fields.Char(string='Shift 2', tracking=True)
    shift3          = fields.Char(string='Shift 3', tracking=True)
    differs         = fields.Char(string='Process Differs Across All Shifts', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISOSite, self).create(vals)
        partner = record.reference_id
        partner.message_post(body=f"Created Type: {record.type}, Address: {record.address}, Product: {record.product}, Permanent & Contract: {record.permanent}, Total No: {record.total_active}, Total Employee: {record.total_emp}, Subcontractor: {record.subcon}, Others: {record.other}, Remark: {record.remarks}, Non shift: {record.non_shift}, Shift 1: {record.shift1}, Shift 2: {record.shift2}, Shift 3: {record.shift3}, Differs: {record.differs}")
        return record

    def write(self, vals):
        res = super(ISOSite, self).write(vals)
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Updated Type: {record.type}, Address: {record.address}, Product:{record.product}, Permanent & Contract: {record.permanent}, Total No: {record.total_active}, Total Employee: {record.total_emp}, Subcontractor: {record.subcon}, Others: {record.other}, Remark: {record.remarks}, Non shift: {record.non_shift}, Shift 1: {record.shift1}, Shift 2: {record.shift2}, Shift 3: {record.shift3}, Differs: {record.differs}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Deleted Type: {record.type}, Address: {record.address}, Product:{record.product}, Permanent & Contract: {record.permanent}, Total No: {record.total_active}, Total Employee: {record.total_emp}, Subcontractor: {record.subcon}, Others: {record.other}, Remark: {record.remarks}, Non shift: {record.non_shift}, Shift 1: {record.shift1}, Shift 2: {record.shift2}, Shift 3: {record.shift3}, Differs: {record.differs}")
        return super(ISOSite, self).unlink()

class ISOSalesinfo(models.Model):
    _name = 'tsi.iso.additional_salesinfo'
    _description = 'Salesinfo'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference_id = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id2 = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id3 = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id4 = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id5 = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id6 = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id7 = fields.Many2one('tsi.iso', string="Reference")
    reference_id8   = fields.Many2one('tsi.iso', string="Reference")
    reference_id9   = fields.Many2one('tsi.iso', string="Reference")
    reference_id10   = fields.Many2one('tsi.ispo', string="Reference")
    reference_id11   = fields.Many2one('tsi.iso', string="Reference")
    reference_id12   = fields.Many2one('tsi.iso', string="Reference")
    reference_id13   = fields.Many2one('tsi.iso', string="Reference")
    reference_id14   = fields.Many2one('tsi.iso', string="Reference")
    reference_id15   = fields.Many2one('tsi.iso', string="Reference")
    reference_id16   = fields.Many2one('tsi.iso', string="Reference")
    reference_id17   = fields.Many2one('tsi.iso', string="Reference")
    reference_id18   = fields.Many2one('tsi.iso', string="Reference")
    reference_id19   = fields.Many2one('tsi.iso', string="Reference")
    reference_id20   = fields.Many2one('tsi.iso', string="Reference")
    reference_id21   = fields.Many2one('tsi.iso', string="Reference")
    reference_id22   = fields.Many2one('tsi.iso', string="Reference")
    reference_id23   = fields.Many2one('tsi.iso', string="Reference")
    reference_id24   = fields.Many2one('tsi.iso', string="Reference")
    reference_id25   = fields.Many2one('tsi.iso', string="Reference")
    reference_id26   = fields.Many2one('tsi.iso', string="Reference")
    reference_id27   = fields.Many2one('tsi.iso', string="Reference")
    nama_site = fields.Char(string='Nama Site', tracking=True)
    stage_1 = fields.Char(string='Stage 1', tracking=True)
    stage_2 = fields.Char(string='Stage 2', tracking=True)
    surveilance_1 = fields.Char(string='Surveillance 1', tracking=True)
    surveilance_2 = fields.Char(string='Surveillance 2', tracking=True)
    surveilance_3   = fields.Char(string='Surveillance 3', tracking=True)
    surveilance_4   = fields.Char(string='Surveillance 4', tracking=True)
    surveilance_5   = fields.Char(string='Surveillance 5', tracking=True)
    recertification_1 = fields.Char(string='Recertification 1', tracking=True)
    recertification_2 = fields.Char(string='Recertification 2', tracking=True)
    recertification = fields.Char(string='Recertification', tracking=True)
    remarks = fields.Char(string='Remarks', tracking=True)

    def _post_message_to_references(self, record, action):
        references = [
            record.reference_id, record.reference_id2, record.reference_id3, 
            record.reference_id4, record.reference_id5, record.reference_id6,
            record.reference_id7, record.reference_id10 
        ]
        message_body = f"{action} Nama Site: {record.nama_site}, Stage 1: {record.stage_1}, Stage 2: {record.stage_2}, Surveillance 1: {record.surveilance_1}, Surveillance 2: {record.surveilance_2}, Surveillance 3: {record.surveilance_3}, Surveillance 4: {record.surveilance_4}, Surveillance 2: {record.surveilance_5}, Recertification: {record.recertification}, Recertification1: {record.recertification_1}, Recertification2: {record.recertification_2}, Remarks: {record.remarks}"

        for ref in references:
            if ref:
                ref.message_post(body=message_body)

    @api.model
    def create(self, vals):
        record = super(ISOSalesinfo, self).create(vals)
        self._post_message_to_references(record, "Created")
        return record

    def write(self, vals):
        res = super(ISOSalesinfo, self).write(vals)
        for record in self:
            self._post_message_to_references(record, "Updated")
        return res

    def unlink(self):
        for record in self:
            self._post_message_to_references(record, "Deleted")
        return super(ISOSalesinfo, self).unlink()

class ISO27001(models.Model):
    _name           = 'tsi.iso.additional_27001'
    _description    = '27001 Info'
    _inherit        = ['mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    reference_id1    = fields.Many2one('tsi.iso', string="Reference")
    reference_id2    = fields.Many2one('tsi.iso', string="Reference")
    reference_id3    = fields.Many2one('tsi.iso', string="Reference")
    nama_site       = fields.Char(string='Nama Site', tracking=True)
    employee        = fields.Char(string='Emp Included', tracking=True)
    it_aspect       = fields.Selection(string='Information Security', selection=[
                            ('identical',   'Mostly Identical'), 
                            ('extenct',     'Only to some extent identical'), 
                            ('differenct',  'Different'), 
                            ], tracking=True)
    it_explanation     = fields.Char(string='IT Explanation', tracking=True)
    isms_aspect     = fields.Selection(string='ISMS as sites', selection=[
                            ('identical',   'Identical, centrally managed'), 
                            ('differs',     'Differs in some respects'), 
                            ('separately',  'Managed separately'), 
                            ], tracking=True)
    isms_explanation     = fields.Char(string='ISMS Explanation', tracking=True)
    special         = fields.Char(string='Special Feature', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISO27001, self).create(vals)
        partner = record.reference_id
        partner.message_post(body=f"Created Nama Site: {record.nama_site}, Emp Included: {record.employee}, Information Security: {record.it_aspect}, IT Explanation:{record.it_explanation}, ISMS as sites: {record.isms_aspect}, ISMS Explanation: {record.isms_explanation}, Special Feature: {record.special}")
        return record

    def write(self, vals):
        res = super(ISO27001, self).write(vals)
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Updated Nama Site: {record.nama_site}, Emp Included: {record.employee}, Information Security: {record.it_aspect}, IT Explanation:{record.it_explanation}, ISMS as sites: {record.isms_aspect}, ISMS Explanation: {record.isms_explanation}, Special Feature: {record.special}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Deleted Nama Site: {record.nama_site}, Emp Included: {record.employee}, Information Security: {record.it_aspect}, IT Explanation:{record.it_explanation}, ISMS as sites: {record.isms_aspect}, ISMS Explanation: {record.isms_explanation}, Special Feature: {record.special}")
        return super(ISO27001, self).unlink()

class ISOHACCP22000(models.Model):
    _name           = 'tsi.iso.additional_haccp'
    _description    = 'HACCP 22000'
    _inherit        = ['mail.thread', 'mail.activity.mixin']

    reference_id        = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    hazard_number       = fields.Char(string='Number of hazard', tracking=True)
    hazard_describe     = fields.Char(string='Describe Hazard', tracking=True)
    process_number      = fields.Char(string='Number of process', tracking=True)
    process_describe    = fields.Char(string='Describe Process', tracking=True)
    tech_number         = fields.Char(string='Number of technology', tracking=True)
    tech_describe       = fields.Char(string='Describe Technology', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISOHACCP22000, self).create(vals)
        partner = record.reference_id
        partner.message_post(body=f"Created Number of hazard: {record.hazard_number}, Describe Hazard: {record.hazard_describe}, Number of process: {record.process_number}, Describe Process:{record.process_describe}, Number of technology: {record.tech_number}, Describe Technology: {record.tech_describe}")
        return record

    def write(self, vals):
        res = super(ISOHACCP22000, self).write(vals)
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Updated Number of hazard: {record.hazard_number}, Describe Hazard: {record.hazard_describe}, Number of process: {record.process_number}, Describe Process:{record.process_describe}, Number of technology: {record.tech_number}, Describe Technology: {record.tech_describe}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Deleted Number of hazard: {record.hazard_number}, Describe Hazard: {record.hazard_describe}, Number of process: {record.process_number}, Describe Process:{record.process_describe}, Number of technology: {record.tech_number}, Describe Technology: {record.tech_describe}")
        return super(ISOHACCP22000, self).unlink()

class ISPOPemasok(models.Model):
    _name           = 'tsi.ispo.pemasok'
    _description    = 'ISPO Pemasok'
    _inherit        = ['mail.thread', 'mail.activity.mixin']

    reference       = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    name            = fields.Char(string='Nama Pemasok', tracking=True)
    lokasi          = fields.Text(string='Lokasi', tracking=True)
    total_area      = fields.Char(string='Total Area', tracking=True)
    total_tertanam  = fields.Char(string='Area Tertanam', tracking=True)
    produksi        = fields.Char(string='Produksi TBS', tracking=True)
    koordinat       = fields.Char(string='Koordinat GPS', tracking=True)

    @api.model
    def create(self, vals):
        record = super(ISPOPemasok, self).create(vals)
        partner = record.reference
        partner.message_post(body=f"Created Nama Pemasok: {record.name}, Lokasi: {record.lokasi}, Total Area: {record.total_area}, Area Tertanam:{record.total_tertanam}, Produksi TBS: {record.produksi}, Koordinat GPS: {record.koordinat}")
        return record

    def write(self, vals):
        res = super(ISPOPemasok, self).write(vals)
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Updated Nama Pemasok: {record.name}, Lokasi: {record.lokasi}, Total Area: {record.total_area}, Area Tertanam:{record.total_tertanam}, Produksi TBS: {record.produksi}, Koordinat GPS: {record.koordinat}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference
            partner.message_post(body=f"Deleted Nama Pemasok: {record.name}, Lokasi: {record.lokasi}, Total Area: {record.total_area}, Area Tertanam:{record.total_tertanam}, Produksi TBS: {record.produksi}, Koordinat GPS: {record.koordinat}")
        return super(ISPOPemasok, self).unlink()

class ISOStandard(models.Model):
    _name           = 'tsi.iso.standard'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Standard'

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)
    standard        = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',  'ISPO'),
                        ], string='Standard', index=True, tracking=True)

    active = fields.Boolean(string="Active", default=True)

    def action_archive(self):
        self.write({'active': False})

    def action_unarchive(self):
        self.write({'active': True})

class ISOStandard(models.Model):
    _name           = 'tsi.iso.tahapan'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Tahapan Audit'

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)

class ISOStandard(models.Model):
    _name           = 'tsi.tahapan.audit'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Tahapan'

    nama            = fields.Char(string='Nama')
    deskripsi     = fields.Char(string='Description')

class EACode(models.Model):
    _name           = 'tsi.ea_code'
    _description    = 'EA Code'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)

    active = fields.Boolean(string="Active", default=True)

    def action_archive(self):
        self.write({'active': False})

    def action_unarchive(self):
        self.write({'active': True})

class Risk(models.Model):
    _name           = 'tsi.iso.risk'
    _description    = 'Risk'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', tracking=True)
    value           = fields.Integer(string='Value', tracking=True)


class SalesOrder(models.Model):
    _inherit        = 'sale.order'

    def get_end_of_month_choices(self):
        options = []
        today = date.today()
        year = today.year
        month = today.month

        # Tentukan apakah bulan ini masih aktif atau sudah lewat
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        end_of_this_month = next_month - timedelta(days=1)

        # Kalau sudah lewat, mulai dari bulan depan
        if today > end_of_this_month:
            month += 1
            if month > 12:
                month = 1
                year += 1

        # Tetapkan jumlah total bulan yang ingin ditampilkan (misalnya 32 bulan)
        total_months = 32

        for i in range(total_months):
            y = year + ((month + i - 1) // 12)
            m = ((month + i - 1) % 12) + 1

            if m == 12:
                next_month = date(y + 1, 1, 1)
            else:
                next_month = date(y, m + 1, 1)
            last_day = next_month - timedelta(days=1)

            options.append((last_day.isoformat(), last_day.strftime('%d %B %Y')))

        return options

    # ISO Reference
    iso_reference   = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    iso_notification   = fields.Many2one('audit.notification', string="Notification", tracking=True)
    application_review_ids   = fields.Many2many('tsi.iso.review', string="Review", tracking=True)
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    # ISPO Reference
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference")
    ispo_notification   = fields.Many2one('audit.notification.ispo', string="Notification")
    application_review_ispo_ids   = fields.Many2many('tsi.ispo.review', string="Review")
    reference_request_ispo_ids = fields.Many2many('tsi.audit.request.ispo', string='Audit Request', tracking=True)

    show_iso_fields = fields.Boolean(compute='_compute_show_fields', store=False)
    show_ispo_fields = fields.Boolean(compute='_compute_show_fields', store=False)
    show_iso_request_fields = fields.Boolean(compute='_compute_show_fields', store=False)
    template_quotation        = fields.Binary('Attachment')
    dokumen_sosialisasi        = fields.Binary('Organization Chart')
    upload_npwp        = fields.Binary('NPWP')
    file_namenpwp       = fields.Char('Filename NPWP', tracking=True)
    file_name       = fields.Char('Filename', tracking=True)
    file_name1       = fields.Char('Filename Dokumen', tracking=True)
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', related='iso_reference.doctype', readonly=True, index=True, tracking=True)

    segment_id          = fields.Many2many('res.partner.category', string='Segment', tracking=True)
    nomor_quotation     = fields.Char(string='Nomor Quotation', tracking=True)
    nomor_kontrak       = fields.Char(string='Nomor Kontrak', tracking=True)
    standard_names = fields.Char(string='Standard Names', compute='_compute_standard_names', store=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False, tracking=True)

    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Kategori', index=True, tracking=True)

    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', tracking=True)
    
    sale_order_options = fields.One2many('tsi.order.options', 'ordered_id', string='Optional Product', index=True)
    nomor_customer = fields.Char(string='Customer ID', default='New', readonly=True, copy=False, tracking=True)
    state = fields.Selection(selection_add=[
        ('draft', 'Quotation'),
        ('cliennt_approval', 'Client Approval'),
        ('waiting_verify_operation', 'Aplication Review'),
        ('create_kontrak', 'Create Kontrak'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Lost'),
        ('application_form', 'Application Form'),
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    
    audit_status = fields.Selection([
        ('program', 'Program'),
        ('Stage-1', 'Stage-1'),
        ('Stage-2', 'Stage-2'),
        ('Surveillance1', 'Surveillance1'),
        ('Surveillance2', 'Surveillance2'),
        ('Recertification', 'Recertification'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status', compute='_compute_status_audit', store=True, related="iso_notification.audit_state")
    audit_status_ispo = fields.Selection([
        ('program', 'Program'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status ISPO', related="ispo_notification.audit_state", store=True, tracking=True)
    # sales_person       = fields.Many2one('res.users', string="Sales Person", related="iso_reference.sales_person", tracking=True)
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract", required=False)
    hide_contract_type = fields.Boolean(compute='_compute_hide_contract_type', store=False)
    is_ispo_selected = fields.Boolean(string="ISPO Selected", compute="_compute_is_ispo_selected", store=True)
    sales_person = fields.Many2one(
        'res.users', string='Salesperson', readonly=False, index=True, tracking=2, store=True, compute='_compute_sales_person')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=False, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    # tgl_perkiraan_mulai = fields.Date(string="Estimated Audit Start Date")
    tgl_perkiraan_selesai = fields.Date(string="Plan of audit date",store=True)
    tgl_perkiraan_audit_selesai = fields.Selection(
        selection=lambda self: self.get_end_of_month_choices(),
        string="Plan of audit date"
    )
    terbit_invoice = fields.Selection([
        ('Direct', 'Direct'),
        ('Associate', 'Associate'),
    ], string="Terbit Invoice")
    associate_name = fields.Many2one('res.partner', compute='_compute_associate', readonly=False, string="Associate Name")


    @api.depends('iso_notification.audit_state')
    def _compute_status_audit(self):
        for record in self:
            record.audit_status = record.iso_notification.audit_state if record.iso_notification else False

    @api.depends('iso_standard_ids')
    def _compute_standard_names(self):
        for record in self:
            record.standard_names = ', '.join(record.iso_standard_ids.mapped('name'))

    @api.depends('iso_reference', 'ispo_reference', 'reference_request_ids', 'reference_request_ispo_ids')
    def _compute_associate(self):
        for record in self:
            if record.iso_reference:
                record.associate_name = record.iso_reference.associate_id
            elif record.ispo_reference:
                record.associate_name = record.ispo_reference.associate_id
            elif record.reference_request_ids:
                record.associate_name = record.reference_request_ids.pic_konsultan1
            elif record.reference_request_ispo_ids:
                record.associate_name = record.reference_request_ispo_ids.pic_konsultan1
            else:
                record.sales_person = False

    @api.depends('iso_reference', 'ispo_reference')
    def _compute_sales_person(self):
        for record in self:
            if record.iso_reference:
                record.sales_person = record.iso_reference.sales_person
            elif record.ispo_reference:
                # Anda bisa sesuaikan behavior di sini
                # Misalnya, jika ispo_reference ada, ambil sales_person dari ispo_reference
                record.sales_person = record.ispo_reference.sales_person
            else:
                record.sales_person = False

    @api.depends('iso_standard_ids')
    def _compute_is_ispo_selected(self):
        for record in self:
            record.is_ispo_selected = any(
                standard.name == 'ISPO' for standard in record.iso_standard_ids
            )

    def _compute_hide_contract_type(self):
        for order in self:
            order.hide_contract_type = any(line.audit_tahapan == 'Initial Audit' for line in order.order_line)

    @api.model
    def create(self, vals):
        self.write({
            'state' : 'sale',
        })
        if vals.get('nomor_customer', 'New') == 'New':
            seq_number = self.env['ir.sequence'].next_by_code('customer.id') or 'New'
            vals['nomor_customer'] = 'TSI-%s-%s' %(datetime.today().year, seq_number)
            result = super(SalesOrder, self).create(vals)
        return result

    @api.depends('iso_standard_ids')
    def _compute_show_fields(self):
        for rec in self:
            iso_standards = rec.iso_standard_ids.mapped('standard')

            rec.show_iso_fields = any(
                standard in iso_standards for standard in ['iso']
            )
            rec.show_ispo_fields = 'ispo' in iso_standards
            rec.show_iso_request_fields = any(
                standard in iso_standards for standard in ['iso']  # bisa diubah sesuai kebutuhan
            )

    def action_confirm(self):
        res = super(SalesOrder, self).action_confirm()
        
        for order in self:
            # Validasi: Field 'terbit_invoice' harus diisi sebelum konfirmasi
            if not order.terbit_invoice:
                raise UserError(_("Field 'Terbit Invoice' wajib diisi sebelum mengkonfirmasi!"))
            # Update nomor_customer jika belum ada
            if order.state == 'sale' and not order.partner_id.nomor_customer:
                order.partner_id.nomor_customer = order.nomor_customer

            # Update status_klien jika belum ada
            if order.state == 'sale' and not order.partner_id.status_klien:
                order.partner_id.status_klien = order.status_klien

            # Cek apakah ada order line dengan 'Initial Audit'
            initial_audit_required = any(
                line.audit_tahapan == 'Initial Audit' for line in order.order_line
            )
            if initial_audit_required and not order.template_quotation:
                raise UserError(_("Harus isi Template Quotation sebelum mengkonfirmasi!"))
            
            # Cek apakah ada order line dengan audit_stage 'surveillance'
            surveillance_required = any(
                line.audit_tahapan in ['Surveillance 1', 'Surveillance 2'] for line in order.order_line
            )

            # Cek apakah contract_type terisi dengan 'new' atau 'amendment'
            if surveillance_required and order.contract_type in ['new', 'amendment']:
                if not order.template_quotation:
                    raise UserError(_("Field Template Quotation wajib diisi untuk contract type 'New' atau 'Amendment'."))

            # Pastikan tipe_pembayaran diisi
            if not order.tipe_pembayaran:
                raise UserError('Mohon tentukan tipe pembayaran')

            # Jika iso_reference tidak diisi, buat audit.notification tanpa ISO reference
            if not order.iso_reference:
                if order.iso_standard_ids:
                    notification_without_iso = self.env['audit.notification'].create({
                        'customer': order.partner_id.id,
                        'sales_order_id': order.id,
                        'tipe_pembayaran': order.tipe_pembayaran,
                        'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)],
                    })
                    order.iso_notification = notification_without_iso.id

                    for standard in order.iso_standard_ids:
                        # Jika tipe pembayaran lunas di awal/akhir, buat program dan report
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_iso.id,
                                'customer': order.partner_id.id
                            })
                            report = self.env['ops.report'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_without_iso.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            # Buat program dan report tanpa lunasawal/lunasakhir
                            program = self.env['ops.program'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_iso.id,
                                'customer': order.partner_id.id
                            })
                else:
                    raise UserError('Tidak ada standar ISO yang terkait.')
            
            # Jika iso_reference diisi, buat audit.notification dengan ISO reference
            else:
                notification_with_iso = self.env['audit.notification'].create({
                    'iso_reference': order.iso_reference.id,
                    'customer': order.partner_id.id,
                    'sales_order_id': order.id,
                    'tipe_pembayaran': order.tipe_pembayaran,
                    'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)] if order.iso_standard_ids else False,
                })
                order.iso_notification = notification_with_iso.id

                # Jika ada ISO standards, buat program dan report
                if order.iso_standard_ids:
                    for standard in order.iso_standard_ids:
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program'].create({
                                'iso_reference': order.iso_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_iso.id,
                                'customer': order.partner_id.id
                            })
                            report = self.env['ops.report'].create({
                                'iso_reference': order.iso_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_with_iso.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            program = self.env['ops.program'].create({
                                'iso_reference': order.iso_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_iso.id,
                                'customer': order.partner_id.id
                            })

            # Jika iso_reference tidak diisi, buat audit.notification tanpa ISO reference
            if not order.ispo_reference:
                if order.iso_standard_ids:
                    notification_without_ispo = self.env['audit.notification.ispo'].create({
                        'customer': order.partner_id.id,
                        'sales_order_id': order.id,
                        'tipe_pembayaran': order.tipe_pembayaran,
                        'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)],
                    })
                    order.ispo_notification = notification_without_ispo.id

                    # Jika tipe pembayaran lunas di awal/akhir, buat program dan report
                    for standard in order.iso_standard_ids:
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program.ispo'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_ispo.id,
                                'customer': order.partner_id.id
                            })
                            report = self.env['ops.report.ispo'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_without_ispo.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            # Buat program dan report tanpa lunasawal/lunasakhir
                            program = self.env['ops.program.ispo'].create({
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_without_ispo.id,
                                'customer': order.partner_id.id
                            })
                else:
                    raise UserError('Tidak ada standar ISPO yang terkait.')
            else:
                # Jika ispo_reference diisi, buat notification dengan ISPO reference
                notification_with_ispo = self.env['audit.notification.ispo'].create({
                    'ispo_reference': order.ispo_reference.id,
                    'customer': order.partner_id.id,
                    'sales_order_id': order.id,
                    'tipe_pembayaran': order.tipe_pembayaran,
                    'iso_standard_ids': [(6, 0, order.iso_standard_ids.ids)] if order.iso_standard_ids else False,
                })
                order.ispo_notification = notification_with_ispo.id

                # Buat program dan report dengan ispo_reference
                if order.iso_standard_ids:
                    for standard in order.iso_standard_ids:
                        if order.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                            program = self.env['ops.program.ispo'].create({
                                'ispo_reference': order.ispo_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_ispo.id,
                                'customer': order.partner_id.id
                            })
                            report = self.env['ops.report.ispo'].create({
                                'ispo_reference': order.ispo_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': notification_with_ispo.id,
                                'customer': order.partner_id.id
                            })
                        else:
                            program = self.env['ops.program.ispo'].create({
                                'ispo_reference': order.ispo_reference.id,
                                'sales_order_id': order.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'type_client': order.tipe_pembayaran,
                                'notification_id': notification_with_ispo.id,
                                'customer': order.partner_id.id
                            })
                            
        return res

    def _create_ops_entries(self, order, standard, notification, is_partial):
        if is_partial:
            program = self.env['ops.program'].create({
                'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'contract_number': order.nomor_kontrak,
                'notification_id': notification.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'contract_date'     : self.date_order,
                'type_client': order.tipe_pembayaran,
                'file_name1': order.file_name1
            })
        else:
            program = self.env['ops.program'].create({
                'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'contract_number': order.nomor_kontrak,
                'notification_id': notification.id,
                'dokumen_sosialisasi': order.dokumen_sosialisasi,
                'contract_date'     : self.date_order,
                'type_client': order.tipe_pembayaran,
                'file_name1': order.file_name1
            })
            # plan = self.env['ops.plan'].create({
            #     'iso_reference': order.iso_reference.id,
            #     'sales_order_id': order.id,
            #     'iso_standard_ids': standard,
            #     'notification_id': notification.id,
            #     'contract_number': order.nomor_kontrak,
            #     'contract_date': order.date_order
            # })
            # review = self.env['ops.review'].create({
            #     'iso_reference': order.iso_reference.id,
            #     'sales_order_id': order.id,
            #     'iso_standard_ids': standard,
            #     'notification_id': notification.id
            # })
            report = self.env['ops.report'].create({
                'iso_reference': order.iso_reference.id,
                'sales_order_id': order.id,
                'iso_standard_ids': standard,
                'notification_id': notification.id
            })
            # sertifikat = self.env['ops.sertifikat'].create({
            #     'iso_reference': order.iso_reference.id,
            #     'sales_order_id': order.id,
            #     'iso_standard_ids': standard,
            #     'notification_id': notification.id
            # })

    def action_approve_quotation(self):
        # Logika untuk menyetujui penawaran
        self.write({'state': 'cliennt_approval'})
        return True
    
    def action_cancel_client(self):
        # Ubah state menjadi 'sent'
        self.write({'state': 'cancel'})
        return True
    
    def action_approval_client(self):
        # Validasi untuk memastikan bahwa tanggal perkiraan mulai dan selesai sudah diisi
        if  not self.tgl_perkiraan_audit_selesai:
            raise UserError("Harap isi Tanggal Perkiraan Mulai dan Tanggal Perkiraan Selesai sebelum melanjutkan.")
        self.create_reviews()
        # Ubah state menjadi 'waiting_verify_operation'
        self.write({'state': 'waiting_verify_operation'})
        return True

    def create_reviews(self):
        # Filter standar ISO dan ISPO berdasarkan tipe, misalnya menggunakan field `standard_type`
        iso_standards = self.iso_standard_ids.filtered(lambda s: s.standard == 'iso')
        ispo_standards = self.iso_standard_ids.filtered(lambda s: s.standard == 'ispo')

        # Jika ada standar ISO, buat review untuk ISO
        if iso_standards:
            for standard in iso_standards:
                self.create_iso_review(standard)
        
        # Jika ada standar ISPO, buat review untuk ISPO
        if ispo_standards:
            for standard in ispo_standards:
                self.create_ispo_review(standard)

    def create_iso_review(self, standard):
        # Buat record di model tsi.iso.review untuk setiap standar ISO
        self.env['tsi.iso.review'].create({
            'reference': self.iso_reference.id,  # Referensi ISO
            'iso_standard_ids': [(4, standard.id)],  # Tambahkan standar ISO ID
            # 'tgl_perkiraan_mulai': self.tgl_perkiraan_mulai,
            'tgl_perkiraan_selesai': datetime.strptime(self.tgl_perkiraan_audit_selesai, "%Y-%m-%d").date()
            if self.tgl_perkiraan_audit_selesai else False,
        })

    def create_ispo_review(self, standard):
        # Buat record di model tsi.ispo.review untuk setiap standar ISPO
        self.env['tsi.ispo.review'].create({
            'reference': self.ispo_reference.id,  # Referensi ISPO
            'iso_standard_ids': [(4, standard.id)],  # Tambahkan standar ISPO ID
            # 'tgl_perkiraan_mulai': self.tgl_perkiraan_mulai,
            'tgl_perkiraan_selesai': datetime.strptime(self.tgl_perkiraan_audit_selesai, "%Y-%m-%d").date()
            if self.tgl_perkiraan_audit_selesai else False,
        })
    
    def action_negotation(self):
        # Ubah state menjadi 'sent'
        self.write({'state': 'draft'})
        return True

    def create_iso(self):
        # Periksa apakah ada iso_standard_ids di sale.order
        if self.iso_standard_ids:
            # Iterasi setiap standar di iso_standard_ids
            for standard in self.iso_standard_ids:
                # Buat record di model tsi.iso.review untuk setiap standar
                self.env['tsi.iso.review'].create({
                    'reference': self.iso_reference.id,  # Referensi ISO
                    'iso_standard_ids': [(4, standard.id)],  # Tambahkan standard ID
                })

    def set_nomor_kontrak(self):
        if not self.nomor_kontrak :
            if self.iso_reference :
                current = datetime.now()
                year    = current.strftime('%Y')

                if self.iso_reference.doctype == 'ispo' :
                    mmyy        = current.strftime('%m/%y')
                    tahun       = current.strftime('%y')
                    bulan       = current.strftime('%m')
                    bulan_roman = roman.toRoman(int(bulan))

                    sequence    = self.env['ir.sequence'].next_by_code('tsi.ispo.kontrak')
                    nomor       = str(sequence) + '/TSI/SPK-ISPO/' + str(bulan_roman) + '/' + str(tahun)

                else :                
                    sequence    = self.env['ir.sequence'].next_by_code('tsi.iso.kontrak')
                    nomor       = 'TSI-' + str(sequence) + '.16.01/' + str(year)


                self.write({'nomor_kontrak': nomor})            

        return True

    def set_nomor_quotation(self):
        if not self.nomor_quotation :
            if self.iso_reference :
                current = datetime.now()
                year    = current.strftime('%Y')

                if self.iso_reference.doctype == 'ispo' :
                    mmyy        = current.strftime('%d.%m')
                    tahun       = current.strftime('%y')
                    bulan       = current.strftime('%m')
                    bulan_roman = roman.toRoman(int(bulan))

                    sequence    = self.env['ir.sequence'].next_by_code('tsi.ispo.kontrak')
                    nomor       = 'TSI-' + str(sequence) + '.'+ str(mmyy) +'/' + str(year)

                    self.write({'nomor_quotation': nomor})            

        return True

    def set_id_customer(self):
        # self.write({'state': 'quotation'})            
        return True

    def generate_crm(self):

        # is_ispo = any(standard.name == 'ISPO' for standard in self.iso_standard_ids) if self.iso_standard_ids else False
        
        # if is_ispo:
        #     if self.audit_status_ispo != 'certificate':
        #         partner_name = self.partner_id.name or 'Partner tidak dikenal'
        #         raise UserError(f'{partner_name} belum terbit sertifikat ISPO.')
        # else:
        #     if self.audit_status != 'certificate':
        #         partner_name = self.partner_id.name or 'Partner tidak dikenal'
        #         raise UserError(f'{partner_name} belum terbit sertifikat ISO.')

        if self.order_line:
            tahapan_audit_ids = []
            show_initial = False
            show_survilance1 = False
            show_survilance2 = False
            show_survilance3 = False
            show_survilance4 = False
            show_recertification = False

            if self.ispo_reference:
                reference = self.ispo_reference
            else:
                reference = self.iso_reference

            history_kontrak = self.env['tsi.history_kontrak'].search([
                ('partner_id', '=', self.partner_id.id)
            ], limit=1)

            if not history_kontrak:
                history_kontrak = self.env['tsi.history_kontrak'].create({
                    'partner_id': self.partner_id.id,
                    'segment': self.segment_id.id,
                    'iso_standard_ids': self.iso_standard_ids.ids,
                    'review_reference': self.application_review_ids.ids,
                    'review_reference_ispo': self.application_review_ispo_ids,
                    'iso_reference': self.iso_reference.id if self.iso_reference else False,
                    'ispo_reference': self.ispo_reference.id if self.ispo_reference else False,
                    'sales_reference': self.id,
                })
            else:
                existing_iso_standard_ids = history_kontrak.iso_standard_ids.ids
                new_iso_standard_ids = list(set(existing_iso_standard_ids + self.iso_standard_ids.ids))

                history_kontrak.write({
                    'segment': self.segment_id.id,
                    'iso_standard_ids': [(6, 0, new_iso_standard_ids)],
                    'review_reference': self.application_review_ids.ids,
                    'review_reference_ispo': self.application_review_ispo_ids,
                    'iso_reference': self.iso_reference.id if self.iso_reference else False,
                    'ispo_reference': self.ispo_reference.id if self.ispo_reference else False,
                })
            
            # Update status_klien to 'active' here
            self.partner_id.write({'status_klien': 'active'})  # Assuming the field name is 'status_klien'

            for line in self.order_line:
                audit_tahapan = line.audit_tahapan
                price_unit = line.price_unit

                # Ambil data dari model ops.sertifikat berdasarkan partner_id atau company_id
                sertifikat = self.env['ops.sertifikat'].search([
                    ('nama_customer', '=', self.partner_id.id)  
                ], limit=1)
                
                if sertifikat:
                    nomor_sertifikat = sertifikat.nomor_sertifikat
                    akre = sertifikat.akre_tes.id
                    initial_date = sertifikat.initial_date
                    issue_date = sertifikat.issue_date
                    validity_date = sertifikat.validity_date
                    expiry_date = sertifikat.expiry_date
                else:
                    nomor_sertifikat = False
                    akre = False
                    initial_date = False
                    issue_date = False
                    validity_date = False
                    expiry_date = False

                if audit_tahapan:
                    tahapan_audit = self.env['tsi.iso.tahapan'].search([('name', '=', audit_tahapan)], limit=1)
                    if tahapan_audit:
                        tahapan_audit_ids.append(tahapan_audit.id)

                        if audit_tahapan == 'Initial Audit':
                            show_initial = True
                            tahapan_field = 'tahapan_id'
                            mandays_field = 'mandays'
                            nomor_field = 'nomor_ia'
                            akre_field = 'accreditation'
                            initial_field = 'tanggal_sertifikat1'
                            issue_field = 'tanggal_sertifikat2'
                            validity_field = 'tanggal_sertifikat3'
                            expiry_field = 'tanggal_sertifikat'
                            nokontrak_field = 'nomor_kontrak_ia'
                            tanggal_field = 'tanggal_kontrak_ia'

                        if self.iso_reference:
                            for iso_standard in self.iso_standard_ids:
                                mandays_app = self.env['tsi.iso.mandays_app'].search([
                                    (tahapan_field, '=', tahapan_audit.id),
                                    ('standard', '=', iso_standard.id),
                                ], limit=1)
                                if mandays_app:
                                    mandays_app.write({
                                        mandays_field: price_unit,
                                        nomor_field: nomor_sertifikat,
                                        akre_field: akre,
                                        initial_field: initial_date,
                                        issue_field: issue_date,
                                        validity_field: validity_date,
                                        expiry_field: expiry_date,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })
                                else:
                                    self.env['tsi.iso.mandays_app'].create({
                                        tahapan_field: history_kontrak.id,
                                        'standard': iso_standard.id,
                                        mandays_field: price_unit,
                                        nomor_field: nomor_sertifikat,
                                        akre_field: akre,
                                        initial_field: initial_date,
                                        issue_field: issue_date,
                                        validity_field: validity_date,
                                        expiry_field: expiry_date,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })

                        if self.ispo_reference:
                            for iso_standard in self.iso_standard_ids:
                                mandays_app = self.env['tsi.iso.mandays_app'].search([
                                    (tahapan_field, '=', tahapan_audit.id),
                                    ('standard', '=', iso_standard.id),
                                ], limit=1)
                                if mandays_app:
                                    mandays_app.write({
                                        mandays_field: price_unit,
                                        nomor_field: nomor_sertifikat,
                                        akre_field: akre,
                                        initial_field: initial_date,
                                        issue_field: issue_date,
                                        validity_field: validity_date,
                                        expiry_field: expiry_date,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })
                                else:
                                    self.env['tsi.iso.mandays_app'].create({
                                        tahapan_field: history_kontrak.id,
                                        'standard': iso_standard.id,
                                        mandays_field: price_unit,
                                        nomor_field: nomor_sertifikat,
                                        akre_field: akre,
                                        initial_field: initial_date,
                                        issue_field: issue_date,
                                        validity_field: validity_date,
                                        expiry_field: expiry_date,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })

            option_records = self.env['tsi.order.options'].search([('ordered_id', '=', self.id)])
            for option in option_records:
                audit_tahapan = option.audit_tahapans
                price_unit = option.price_units

                sertifikat = self.env['ops.sertifikat'].search([
                    ('nama_customer', '=', self.partner_id.id)
                ], limit=1)
                
                if sertifikat:
                    nomor_sertifikat = sertifikat.nomor_sertifikat
                    akre = sertifikat.akre_tes
                    initial_date = sertifikat.initial_date
                else:
                    nomor_sertifikat = False
                    akre = False
                    initial_date = False

                if audit_tahapan:
                    tahapan_audit = self.env['tsi.iso.tahapan'].search([('name', '=', audit_tahapan)], limit=1)
                    if tahapan_audit:
                        tahapan_audit_ids.append(tahapan_audit.id)

                        # Logic remains similar to the one above
                        if audit_tahapan == 'Surveillance 1':
                            show_survilance1 = True
                            tahapan_field = 'tahapan_id1'
                            mandays_field = 'mandays_s1'
                            nomor_field = 'nomor_s1'
                            akre_field = 'accreditation'
                            initial_field = 'initial_sertifikat_s_2'
                            nokontrak_field = 'nomor_kontrak_s1'
                            tanggal_field = 'tanggal_kontrak_s1'
                        elif audit_tahapan == 'Surveillance 2':
                            show_survilance2 = True
                            tahapan_field = 'tahapan_id2'
                            mandays_field = 'mandays_s2'
                            nomor_field = 'nomor_s2'
                            akre_field = 'accreditation'
                            initial_field = 'tanggal_sertifikat_initial_s2'
                            nokontrak_field = 'nomor_kontrak_s2'
                            tanggal_field = 'tanggal_kontrak_s2'
                        elif audit_tahapan == 'Surveillance 3':
                            show_survilance3 = True
                            tahapan_field = 'tahapan_id3'
                            mandays_field = 'mandays_s3'
                            nomor_field = 'nomor_s3'
                            akre_field = 'accreditation'
                            initial_field = 'initial_tanggal_sertifikat_s3'
                            nokontrak_field = 'nomor_kontrak_s3'
                            tanggal_field = 'tanggal_kontrak_s3'
                        elif audit_tahapan == 'Surveillance 4':
                            show_survilance4 = True
                            tahapan_field = 'tahapan_id4'
                            mandays_field = 'mandays_s4'
                            nomor_field = 'nomor_s4'
                            akre_field = 'accreditation'
                            initial_field = 'initiall_s4'
                            nokontrak_field = 'nomor_kontrak_s4'
                            tanggal_field = 'tanggal_kontrak_s4'
                        elif audit_tahapan == 'Recertification':
                            show_recertification = True
                            tahapan_field = 'tahapan_id_re'
                            mandays_field = 'mandays_rs'
                            nomor_field = 'nomor_re'
                            akre_field = 'accreditation'
                            initial_field = 'tanggal_sertifikat_initial_rs'
                            nokontrak_field = 'nomor_kontrak_re'
                            tanggal_field = 'tanggal_kontrak_re'

                        if self.iso_reference:
                            for iso_standard in self.iso_standard_ids:
                                mandays_app = self.env['tsi.iso.mandays_app'].search([
                                    (tahapan_field, '=', tahapan_audit.id),
                                    ('standard', '=', iso_standard.id),
                                ], limit=1)
                                if mandays_app:
                                    mandays_app.write({
                                        mandays_field: price_unit,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })
                                else:
                                    self.env['tsi.iso.mandays_app'].create({
                                        tahapan_field: history_kontrak.id,
                                        'standard': iso_standard.id,
                                        mandays_field: price_unit,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })

                        if self.ispo_reference:
                            for iso_standard in self.iso_standard_ids:
                                mandays_app = self.env['tsi.iso.mandays_app'].search([
                                    (tahapan_field, '=', tahapan_audit.id),
                                    ('standard', '=', iso_standard.id),
                                ], limit=1)
                                if mandays_app:
                                    mandays_app.write({
                                        mandays_field: price_unit,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })
                                else:
                                    self.env['tsi.iso.mandays_app'].create({
                                        tahapan_field: history_kontrak.id,
                                        'standard': iso_standard.id,
                                        mandays_field: price_unit,
                                        nokontrak_field: self.nomor_kontrak,
                                        tanggal_field: self.date_order.date(),
                                    })

            history_kontrak.write({
                'tahapan_audit_ids': [(6, 0, tahapan_audit_ids)],
                'show_initial': show_initial,
                'show_survilance1': show_survilance1,
                'show_survilance2': show_survilance2,
                'show_survilance3': show_survilance3,
                'show_survilance4': show_survilance4,
                'show_recertification': show_recertification,
            })

        else:
            raise UserError('Mohon melengkapi data penjualan')

        self.message_post(body="Generate CRM Oleh %s" % self.env.user.name)

    # def generate_ops(self):
    #     if self.tipe_pembayaran :
    #         if self.iso_reference.iso_standard_ids :
    #             notification = self.env['audit.notification'].create({
    #                 'iso_reference'     : self.iso_reference.id,
    #                 'sales_order_id'    : self.id,
    #                 'tipe_pembayaran'    : self.tipe_pembayaran,
    #                 'iso_standard_ids'  : self.iso_reference.iso_standard_ids,
    #             })
    #             self.iso_notification = notification.id
    #             for standard in self.iso_reference.iso_standard_ids :
    #                 if self.tipe_pembayaran in ['lunasawal','lunasakhir'] :

    #                     program = self.env['ops.program'].create({
    #                         'iso_reference'     : self.iso_reference.id,
    #                         'sales_order_id'    : self.id,
    #                         'iso_standard_ids'  : standard,
    #                         'contract_number'   : self.nomor_kontrak,
    #                         'notification_id'   : notification.id     
    #                     })
    #                     # plan = self.env['ops.plan'].create({
    #                     #     'iso_reference'     : self.iso_reference.id,
    #                     #     'sales_order_id'    : self.id,
    #                     #     'iso_standard_ids'  : standard,
    #                     #     'notification_id'   : notification.id     
    #                     # })
    #                     # review = self.env['ops.review'].create({
    #                     #     'iso_reference'     : self.iso_reference.id,
    #                     #     'sales_order_id'    : self.id,
    #                     #     'iso_standard_ids'  : standard,
    #                     #     'notification_id'   : notification.id     
    #                     # })
    #                     report = self.env['ops.report'].create({
    #                         'iso_reference'     : self.iso_reference.id,
    #                         'sales_order_id'    : self.id,
    #                         'iso_standard_ids'  : standard,
    #                         'notification_id'   : notification.id     
    #                     })
    #                     sertifikat = self.env['ops.sertifikat'].create({
    #                         'iso_reference'     : self.iso_reference.id,
    #                         'sales_order_id'    : self.id,
    #                         'iso_standard_ids'  : standard,
    #                         'notification_id'   : notification.id     
    #                     })
    #                 else :
    #                     program = self.env['ops.program'].create({
    #                         'iso_reference'     : self.iso_reference.id,
    #                         'sales_order_id'    : self.id,
    #                         'iso_standard_ids'  : standard,
    #                         'contract_number'   : self.nomor_kontrak,
    #                         'notification_id'   : notification.id,
    #                         'contract_date'        : self.date_order,     
    #                     })
    #                     # plan = self.env['ops.plan'].create({
    #                     #     'iso_reference'     : self.iso_reference.id,
    #                     #     'sales_order_id'    : self.id,
    #                     #     'iso_standard_ids'  : standard,
    #                     #     'notification_id'   : notification.id     
    #                     # })                        
    #     else :
    #         raise UserError('Mohon tentukan tipe pembayaran')   

    #             # notification.write({'plan_lines': [(4, plan.id)]})
    #             # notification.write({'program_lines': [(4, program.id)]})
    #             # notification.write({'review_lines': [(4, review.id)]})
    #             # notification.write({'report_lines': [(4, report.id)]})

    #     return True

class AccountMove(models.Model):
    _inherit            = 'account.move'

    iso_reference       = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    ispo_reference       = fields.Many2one('tsi.ispo', string="Reference", tracking=True)
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    reference_request_ispo_ids = fields.Many2many('tsi.audit.request.ispo', string='Audit Request', tracking=True)
    sale_reference      = fields.Many2one('sale.order', string="Sale Reference", tracking=True)
    iso_notification    = fields.Many2one('audit.notification', related='sale_reference.iso_notification', string="Notification", tracking=True)
    ispo_notification    = fields.Many2one('audit.notification.ispo', related='sale_reference.ispo_notification', string="Notification", tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, tracking=True)
    contract_number = fields.Char(string='Nomor Kontrak', compute='_compute_contract_number', store=True, tracking=True)
    noted = fields.Char('Intervention', tracking=True)
    doctype         = fields.Selection([
                            ('ISO',  'ISO'),
                            ('ISPO',   'ISPO'),
                        ], string='Doc Type', index=True, tracking=True)
    formatted_amount_total = fields.Char(string='Formatted Total', compute='get_formatted_amount_total')
    formatted_amount_untaxed = fields.Char(string='Formatted Total Untaxed', compute='get_formatted_amount_untaxed')
    formatted_amount_tax = fields.Char(string='Formatted Total TAX', compute='get_formatted_amount_tax')
    currency_id = fields.Many2one('res.currency', string='Currency', tracking=True)
    amount_total_text = fields.Char(string='Amount Total in Words', compute='_compute_amount_total_text', tracking=True)
    thn = fields.Char(string='Invoice Year', compute='_compute_invoice_date_parts', tracking=True)
    mon = fields.Char(string='Invoice Month', compute='_compute_invoice_date_parts', tracking=True)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', tracking=True, related="iso_notification.tipe_pembayaran", readonly=False)
    terbit_invoice = fields.Selection([
        ('Direct', 'Direct'),
        ('Associate', 'Associate'),
    ], string="Terbit Invoice")

    associate_name = fields.Many2one('res.partner', string="Associate Name")
    total_price_unit = fields.Float(string='Total Harga Satuan', compute='_compute_total_price_unit', store=True)
    formatted_total_price_unit = fields.Char(string="Total Harga Satuan (Format)", compute='_compute_formatted_price_unit')
    vat_string = fields.Char(
        string='VAT Summary', compute='_compute_vat_string', store=True
    )

    @api.depends('invoice_line_ids.tax_ids')
    def _compute_vat_string(self):
        for move in self:
            taxes = move.invoice_line_ids.mapped('tax_ids')
            if taxes:
                # Hilangkan duplikat dan jaga urutan
                unique_names = list(dict.fromkeys(t.name for t in taxes if t.name))
                move.vat_string = ', '.join(unique_names)
            else:
                move.vat_string = ''

    # Format Total Harga Satuan (Seperti format_amount_untaxed)
    def format_total_price_unit(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('total_price_unit')
    def _compute_formatted_price_unit(self):
        for rec in self:
            rec.formatted_total_price_unit = self.format_total_price_unit(rec.total_price_unit)

    @api.depends('invoice_line_ids.price_unit')
    def _compute_total_price_unit(self):
        for move in self:
            move.total_price_unit = sum(line.price_unit for line in move.invoice_line_ids)

    @api.onchange('terbit_invoice')
    def _onchange_terbit_invoice(self):
        """Menampilkan partner_id & associate_name sesuai pilihan terbit_invoice"""
        if self.terbit_invoice == 'Associate':
            # Jika "Associate", tetap tampilkan partner_id dan wajibkan associate_name
            self.partner_id = self.partner_id  # Partner tetap ada
        else:
            # Jika "Direct", kosongkan associate_name
            self.associate_name = False
    
    def action_post(self):
        for rec in self:
            try:
                _logger.info('Processing move ID: %s', rec.id)
                if rec.payment_id:
                    if rec.payment_id.state not in ['posted', 'cancel']:
                        _logger.info('Calling action_post for payment_id %s', rec.payment_id.id)
                        rec.payment_id.action_post()
                else:
                    _logger.info('Calling _post for move ID %s', rec.id)
                    rec._post(soft=False)
                
                # Menambahkan fitur untuk mengirim notifikasi
                _logger.info('Sending notification for move ID %s', rec.id)
                rec.send_post_notification()

                _logger.info('Move %s posted successfully.', rec.id)
            except UserError as e:
                _logger.error('UserError while posting move %s: %s', rec.id, str(e))
                raise
            except Exception as e:
                _logger.error('Error posting move %s: %s', rec.id, str(e))
                raise UserError(f'Error posting move {rec.id}: {str(e)}')
        return False
    
    def send_post_notification(self):
        for rec in self:
            # Logika untuk mengirim notifikasi, misalnya email
            _logger.info('Notifikasi: Move %s berhasil diposting.', rec.id)
            # Contoh email, Anda dapat menambahkan logika email di sini
            # self.env['mail.mail'].create({
            #     'subject': 'Move Posted',
            #     'body_html': f'<p>Move {rec.id} has been posted successfully.</p>',
            #     'email_to': 'example@example.com',
            # }).send()

    #Compute Bulan dan Tahun
    @api.depends('invoice_date')
    def _compute_invoice_date_parts(self):
        for move in self:
            if move.invoice_date:
                date = fields.Date.from_string(move.invoice_date)
                move.thn = date.strftime('%Y')
                move.mon = date.strftime('%m')
            else:
                move.thn = ''
                move.mon = ''

    #Compute Angka Menjadi huruf
    @api.depends('amount_total')
    def _compute_amount_total_text(self):
        for move in self:
            move.amount_total_text = self._amount_to_text(move.amount_total)

    #Compute Angka Menjadi huruf
    def _amount_to_text(self, amount):
        # Convert amount to words in Indonesian
        words = num2words(amount, lang='id').replace('-', ' ')
        # Remove decimal part and add 'rupiah'
        words = words.split(' koma ')[0] + ' rupiah'
        return words

    #Format Amoun Total
    def format_amount(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    #Format Amoun Total
    def get_formatted_amount_total(self):
        for record in self:
            record.formatted_amount_total = self.format_amount(record.amount_total)

    #Format Amoun Untaxed
    def format_amount_untaxed(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    #Format Amoun Untaxed
    def get_formatted_amount_untaxed(self):
        for record in self:
            record.formatted_amount_untaxed = self.format_amount_untaxed(record.amount_untaxed)

    #Format Amoun Tax    
    def format_amount_tax(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    #Format Amoun Tax
    def get_formatted_amount_tax(self):
        for record in self:
            record.formatted_amount_tax = self.format_amount_tax(record.amount_tax)

    @api.depends('invoice_origin')
    def _compute_contract_number(self):
        for invoice in self:
            if invoice.invoice_origin:
                sales_order = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)], limit=1)
                if sales_order:
                    invoice.contract_number = sales_order.nomor_kontrak

    def set_lunas_dp(self):
        if self.sale_reference:
            # Cek tipe pembayaran
            if self.tipe_pembayaran == 'termin':
                # Jika tipe pembayaran 'termin', buat dua records
                for standard in self.iso_reference.iso_standard_ids:
                    # Mencari reference request yang cocok berdasarkan iso_standard_ids
                    matching_reference = self.reference_request_ids.filtered(
                        lambda r: standard.id in r.iso_standard_ids.ids  # Gunakan .ids untuk mengambil ID dari Many2many
                    )
                    reference_ids = matching_reference.ids if matching_reference else []

                    # Buat ops.report
                    self.env['ops.report'].create({
                        'iso_reference': self.iso_reference.id,
                        'reference_request_ids': [(6, 0, reference_ids)],  # Gunakan reference_ids yang benar
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.iso_notification.id
                    })
                    # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                    if self.iso_notification.plan_lines:
                        self.iso_notification.plan_lines.write({'state': 'done'})
                
                # Buat satu lagi record untuk 'termin' jika perlu
                for standard in self.iso_reference.iso_standard_ids:
                    matching_reference = self.reference_request_ids.filtered(
                        lambda r: standard.id in r.iso_standard_ids.ids
                    )
                    reference_ids = matching_reference.ids if matching_reference else []

                    # Buat ops.report
                    self.env['ops.report'].create({
                        'iso_reference': self.iso_reference.id,
                        'reference_request_ids': [(6, 0, reference_ids)],  # Gunakan reference_ids yang benar
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.iso_notification.id
                    })
                    # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                    if self.iso_notification.plan_lines:
                        self.iso_notification.plan_lines.write({'state': 'done'})

            elif self.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                # Jika tipe pembayaran 'lunasawal' atau 'lunasakhir', buat satu record
                for standard in self.iso_reference.iso_standard_ids:
                    self.env['ops.report'].create({
                        'iso_reference': self.iso_reference.id,
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.iso_notification.id
                    })

            # Proses untuk ISPO reference
            if self.ispo_reference:
                for standard in self.ispo_reference.iso_standard_ids:
                    self.env['ops.report.ispo'].create({
                        'ispo_reference': self.ispo_reference.id,
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.ispo_notification.id
                    })

            # Proses berdasarkan reference_request_ids jika ada
            if self.reference_request_ids:
                for reference_request in self.reference_request_ids:
                    for standard in reference_request.iso_standard_ids:
                        self.env['ops.report'].create({
                            'iso_reference': self.iso_reference.id,
                            'reference_request_ids': [(6, 0, [reference_request.id])],  # Gunakan reference_request.id
                            'sales_order_id': self.sale_reference.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'notification_id': self.iso_notification.id
                        })
                        # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                        if self.iso_notification.plan_lines:
                            self.iso_notification.plan_lines.write({'state': 'done'})

            # Proses untuk reference_request_ispo_ids jika ada
            if self.reference_request_ispo_ids:
                for standard in self.reference_request_ispo_ids.iso_standard_ids:
                    self.env['ops.report.ispo'].create({
                        'sales_order_id': self.sale_reference.id,
                        'iso_standard_ids': [(6, 0, [standard.id])],
                        'notification_id': self.ispo_notification.id
                    })

        self.message_post(body="Set Lunas DP Oleh %s" % self.env.user.name)

        return True

    def set_lunas_payment(self):

        # lines_initial = self.iso_reference.lines_initial if self.iso_reference else self.env['tsi.iso.initial']

        for record in self:
            if record.iso_notification and record.iso_notification.audit_state != 'recommendation':
                raise UserError("Audit belum pada tahap Recommendation. Tidak bisa melanjutkan proses untuk Terbit Sertifikat.")

            if record.sale_reference:
                if record.iso_reference:
                    for standard in record.iso_reference.iso_standard_ids:
                        self.env['ops.sertifikat'].create({
                            'iso_reference': record.iso_reference.id,
                            'sales_order_id': record.sale_reference.id,
                            'iso_standard_ids': standard,
                            'notification_id': record.iso_notification.id
                        })
                    # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                    if self.iso_notification.review_lines:
                        self.iso_notification.review_lines.write({'state': 'done'})
                elif record.ispo_reference:
                    for standard in record.ispo_reference.iso_standard_ids:
                        self.env['ops.sertifikat.ispo'].create({
                            'ispo_reference': record.ispo_reference.id,
                            'sales_order_id': record.sale_reference.id,
                            'iso_standard_ids': standard,
                            'notification_id': record.ispo_notification.id
                        })

                else:
                    for standard in record.iso_standard_ids:
                        if standard.name == 'ISPO':
                            self.env['ops.sertifikat.ispo'].create({
                                'sales_order_id': record.sale_reference.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': record.ispo_notification.id,
                                'nama_customer' : record.sale_reference.partner_id.name
                            })
                        else:
                            self.env['ops.sertifikat'].create({
                                'sales_order_id': record.sale_reference.id,
                                'iso_standard_ids': [(6, 0, [standard.id])],
                                'notification_id': record.iso_notification.id,
                                'nama_customer' : record.sale_reference.partner_id.name
                            })
                            # Ubah status state menjadi 'done' pada ops.plan terkait dengan iso_notification
                            if self.iso_notification.review_lines:
                                self.iso_notification.review_lines.write({'state': 'done'})

        # --- Blok Pengajuan Marketing ---
        # if self.iso_reference and lines_initial:
        #     AUDIT_STAGE_MAP = {
        #         'Initial Audit': 'initial_audit',
        #         'Recertification': 'recertification',
        #     }

        #     stages_dict = {}
        #     for line in lines_initial:
        #         mapped_stage = AUDIT_STAGE_MAP.get(line.audit_stage)
        #         if not mapped_stage:
        #             continue
        #         stages_dict.setdefault(mapped_stage, []).append(line)

        #     cust_id = self.sale_reference.partner_id.id
        #     sp_id = self.sale_reference.sales_person.id
        #     std_ids = self.sale_reference.iso_standard_ids.ids
        #     today = fields.Date.today()

        #     note_text = (
        #         "📌 Komisi ISO & ISPO Berdasarkan Harga per Standard:\n\n"

        #         "✅ ISO: 9001, 14001, 45001, 22001, HACCP, Others ISO\n\n"
        #         "💰 Harga > 15jt / standard:\n"
        #         "   - Direct     : 7%\n"
        #         "   - Associate  : 5%\n\n"
        #         "💰 Harga 10 - 15jt / standard:\n"
        #         "   - Direct     : 5%\n"
        #         "   - Associate  : 3%\n\n"
        #         "💰 Harga < 10jt / standard:\n"
        #         "   - Direct     : 0%\n"
        #         "   - Associate  : 0%\n\n"

        #         "✅ ISO: 27001, 37001, 20001 TSI\n\n"
        #         "💰 Harga > 30jt / standard:\n"
        #         "   - Direct     : 7%\n"
        #         "   - Associate  : 5%\n\n"
        #         "💰 Harga 20 - 30jt / standard:\n"
        #         "   - Direct     : 5%\n"
        #         "   - Associate  : 3%\n\n"
        #         "💰 Harga < 20jt / standard:\n"
        #         "   - Direct     : 0%\n"
        #         "   - Associate  : 0%\n\n"

        #         "✅ ISPO\n\n"
        #         "💰 Harga > 60jt / standard:\n"
        #         "   - Direct     : 7%\n"
        #         "   - Associate  : 5%\n\n"
        #         "💰 Harga 40 - 60jt / standard:\n"
        #         "   - Direct     : 5%\n"
        #         "   - Associate  : 3%\n\n"
        #         "💰 Harga < 40jt / standard:\n"
        #         "   - Direct     : 0%\n"
        #         "   - Associate  : 0%\n\n"
        #     )

        #     marketing_obj = self.env['tsi.pengajuan.marketing']
        #     for tahap_audit, lines in stages_dict.items():
        #         nilai_bersih = sum(l.price - l.fee for l in lines)

        #         domain = [
        #             ('customer', '=', cust_id),
        #             ('tahap_audit', '=', tahap_audit),
        #         ]
        #         candidates = marketing_obj.search(domain)
        #         existing = candidates.filtered(
        #             lambda r: set(r.iso_standard_ids.ids) == set(std_ids)
        #         )

        #         if existing:
        #             existing.write({'tanggal_pelunasan': today})
        #         else:
        #             marketing_obj.create({
        #                 'customer': cust_id,
        #                 'sales_person': sp_id,
        #                 'iso_standard_ids': [(6, 0, std_ids)],
        #                 'tanggal_pelunasan': today,
        #                 'tahap_audit': tahap_audit,
        #                 'nilai_bersih': nilai_bersih,
        #                 'note': note_text,
        #             })

        self.message_post(body="Set Lunas Payment Oleh %s" % self.env.user.name)
        return True

    @api.model
    def create(self, vals):
        if 'invoice_origin' in vals:
            sale_order = self.env['sale.order'].search([('name', '=', vals['invoice_origin'])], limit=1)
            if sale_order:
                if sale_order.iso_reference:
                    vals['iso_reference'] = sale_order.iso_reference
                    vals['iso_notification'] = sale_order.iso_notification
                
                if sale_order.ispo_reference:
                    vals['ispo_reference'] = sale_order.ispo_reference
                    vals['ispo_notification'] = sale_order.ispo_notification

                if sale_order.reference_request_ids:
                    vals['reference_request_ids'] = [(6, 0, sale_order.reference_request_ids.ids)]
                    vals['iso_notification'] = sale_order.iso_notification

                if sale_order.reference_request_ispo_ids:
                    vals['reference_request_ispo_ids'] = [(6, 0, sale_order.reference_request_ispo_ids.ids)]
                    vals['ispo_notification'] = sale_order.ispo_notification

                if sale_order.iso_standard_ids:
                    vals['iso_standard_ids'] = [(6, 0, sale_order.iso_standard_ids.ids)]

                vals['sale_reference'] = sale_order.id

        return super(AccountMove, self).create(vals)
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    audit_tahapan = fields.Selection([
                            ('Initial Audit', 'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Recertefication', 'Recertefication'),],
                            string='Audit Stage', index=True, tracking=True)
    tahun = fields.Integer(string="Tahun", tracking=True)
    formatted_price_unit = fields.Char(string='Formatted Unit Price', compute='_compute_formatted_price_unit')
    in_pajak = fields.Boolean("Include Pajak")
    ex_pajak = fields.Boolean("Exclude Pajak")

    def _compute_formatted_price_unit(self):
        for line in self:
            # Format harga dalam Rupiah, tambahkan tanda minus jika harga negatif
            if line.price_unit < 0:
                line.formatted_price_unit = "({:,.0f})".format(abs(line.price_unit)).replace(',', '.')
            else:
                line.formatted_price_unit = "{:,.0f}".format(line.price_unit).replace(',', '.')

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    code = fields.Char(string='Bank Code', index=True, tracking=True)
    branch = fields.Char(string="Bank Branch", tracking=True)

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sertifikat_id = fields.Many2one('ops.sertifikat', string="Sertifikat")
    cek_crm = fields.Boolean(string='To CRM', tracking=True)
    audit_tahapan = fields.Selection([
                            ('Initial Audit',         'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),
                            ('Surveillance 5', 'Surveillance 5'),
                            ('Surveillance 6', 'Surveillance 6'),
                            ('Recertification', 'Recertification 1'),
                            ('Recertification 2', 'Recertification 2'),
                            ('Recertification 3', 'Recertification 3'),
                            ],string='Audit Stage', index=True, tracking=True)
    tahun           = fields.Char("Tahun", tracking=True)
    in_pajak = fields.Boolean("Include Pajak")
    ex_pajak = fields.Boolean("Exclude Pajak")

    @api.onchange('in_pajak', 'ex_pajak')
    def _onchange_in_ex_pajak(self):
        for rec in self:
            # Pastikan hanya satu checkbox yang aktif
            if rec.in_pajak and rec.ex_pajak:
                rec.ex_pajak = False

            # Kalau in_pajak dicentang → hitung harga tanpa pajak
            if rec.in_pajak:
                rec.price_unit = rec.price_unit / 1.11 if rec.price_unit else 0.0

            # Kalau ex_pajak dicentang → biarkan price_unit apa adanya
            elif rec.ex_pajak:
                pass  # Tidak diubah

            # Kalau tidak dicentang keduanya → biarkan juga
            elif not rec.in_pajak and not rec.ex_pajak:
                pass

    @api.model
    def create(self, vals):
        record = super(SaleOrderLine, self).create(vals)
        partner = record.order_id
        partner.message_post(body=f"Created Product: {record.product_id.name}, Audit Stage: {record.audit_tahapan}, Tahun: {record.tahun}, Quantity:{record.product_uom_qty}, Unit Price: {record.price_unit}, Tax: {record.tax_id.name}")
        return record

    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        for record in self:
            partner = record.order_id
            partner.message_post(body=f"Updated Product: {record.product_id.name}, Audit Stage: {record.audit_tahapan}, Tahun: {record.tahun}, Quantity:{record.product_uom_qty}, Unit Price: {record.price_unit}, Tax: {record.tax_id.name}")
        return res

    def unlink(self):
        for record in self:
            partner = record.order_id
            partner.message_post(body=f"Deleted Product: {record.product_id.name}, Audit Stage: {record.audit_tahapan}, Tahun: {record.tahun}, Quantity:{record.product_uom_qty}, Unit Price: {record.price_unit}, Tax: {record.tax_id.name}")
        return super(SaleOrderLine, self).unlink()

    # def _prepare_invoice_line(self, **optional_values):
    #     """
    #     Prepare the dict of values to create the new invoice line for a sales order line.

    #     :param qty: float quantity to invoice
    #     :param optional_values: any parameter that should be added to the returned invoice line
    #     """
    #     self.ensure_one()
    #     res = {
    #         'display_type': self.display_type,
    #         'sequence': self.sequence,
    #         'name': self.name,
    #         'audit_tahapan': self.audit_tahapan,
    #         'product_id': self.product_id.id,
    #         'product_uom_id': self.product_uom.id,
    #         'quantity': self.qty_to_invoice,
    #         'discount': self.discount,
    #         'price_unit': self.price_unit,
    #         'tax_ids': [(6, 0, self.tax_id.ids)],
    #         'sale_line_ids': [(4, self.id)],
    #     }
    #     if self.order_id.analytic_account_id and not self.display_type:
    #         res['analytic_account_id'] = self.order_id.analytic_account_id.id
    #     # if self.analytic_tag_ids and not self.display_type:
    #     #     res['analytic_tag_ids'] = [(6, 0, self.analytic_tag_ids.ids)]
    #     if optional_values:
    #         res.update(optional_values)
    #     if self.display_type:
    #         res['account_id'] = False
    #     return res


class SaleOrderOptions(models.Model):
    _name = 'tsi.order.options'
    _order = 'ordered_id'

    ordered_id = fields.Many2one('sale.order', string="Optional Product", tracking=True)
    sertifikat_id = fields.Many2one('ops.sertifikat', string="Sertifikat")
    surveillance_id = fields.Many2one('tsi.iso.surveillance', string="Surveillance Line")
    tahun_audit = fields.Char("Tahun", tracking=True)
    audit_tahapans = fields.Selection([
                        ('Surveillance 1', 'Surveillance 1'),
                        ('Surveillance 2', 'Surveillance 2'),
                        ('Surveillance 3', 'Surveillance 3'),
                        ('Surveillance 4', 'Surveillance 4'),
                        ('Recertefication', 'Recertefication')],
                        string='Audit Stage', index=True, tracking=True)
    price_units = fields.Float(string="Price Unit", required=True, tracking=True)
    quanty      = fields.Float(string="Quantity", required=True, default=1.0, tracking=True)

    @api.model
    def create(self, vals):
        record = super(SaleOrderOptions, self).create(vals)
        partner = record.ordered_id
        partner.message_post(body=f"Created Audit Stage: {record.audit_tahapans}, Tahun: {record.tahun_audit}, Quantity:{record.quanty}, Unit Price: {record.price_units}")
        return record

    def write(self, vals):
        res = super(SaleOrderOptions, self).write(vals)
        for record in self:
            partner = record.ordered_id
            partner.message_post(body=f"Updated Audit Stage: {record.audit_tahapans}, Tahun: {record.tahun_audit}, Quantity:{record.quanty}, Unit Price: {record.price_units}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ordered_id
            partner.message_post(body=f"Deleted Audit Stage: {record.audit_tahapans}, Tahun: {record.tahun_audit}, Quantity:{record.quanty}, Unit Price: {record.price_units}")
        return super(SaleOrderOptions, self).unlink()

class MandaysAuditor(models.Model):
        _name           = 'mandays.auditor'
        _description    = 'Mandays Auditor'
        _rec_name       = 'name_auditor'

        name_auditor    = fields.Many2one('hr.employee', 
                                string="Nama Audior",
                                domain="[('department_id.name', 'in', ['OPERATION ICT', 'OPERATION XMS', 'OPERATION SUSTAINABILITY', 'Auditor Subcont'])]")
        auditor_ir      = fields.Boolean("Auditor Internal")
        auditor_er      = fields.Boolean("Auditor External")
        harga_mandays   = fields.Float("Harga Mandays")