from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import requests
import json

import logging
_logger = logging.getLogger(__name__)

class AuditRequest(models.Model):
    _name           = 'tsi.audit.request'
    _description    = 'Audit Request'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _order          = 'id DESC'

    name            = fields.Char(string="Document No",  readonly=True, tracking=True)
    audit_stage     = fields.Selection([
                            ('surveilance1',     'Surveillance 1'),
                            ('surveilance2',     'Surveillance 2'),
                            ('recertification', 'Recertification 1'),
                        ], string='Audit Stage', tracking=True, store=True)

    cycle               = fields.Selection([
                            ('cycle1',     'Cycle 1'),
                            ('cycle2',     'Cycle 2'),
                            ('cycle3',     'Cycle 3'),
                        ], string='Cycle', tracking=True)

    audit_stage2        = fields.Selection([
                            ('surveilance3',     'Surveillance 3'),
                            ('surveilance4',     'Surveillance 4'),
                            ('recertification2', 'Recertification 2'),
                        ], string='Audit Stage', tracking=True)

    audit_stage3        = fields.Selection([
                            ('surveilance5',     'Surveillance 5'),
                            ('surveilance6',     'Surveillance 6'),
                            ('recertification3', 'Recertification 3'),
                        ], string='Audit Stage', tracking=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False)
    reference           = fields.Many2one('tsi.history_kontrak', string="Reference")
    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True, tracking=True)
    office_address      = fields.Char(string='Office Address', related="reference.office_address", readonly=False, tracking=True)
    site_address        = fields.Char(string='Site Project Address', tracking=True)
    invoicing_address   = fields.Char(string="Invoicing Address", related="reference.invoicing_address", readonly=False, tracking=True)
    sales               = fields.Many2one('res.users', string='Sales Person',store=True, related="reference.sales", readonly=False, tracking=True)
    user_id             = fields.Many2one('res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user)
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    telp                = fields.Char(string='Telp', related="reference.telp", readonly=False, tracking=True)
    email               = fields.Char(string='Email', related="reference.email", readonly=False, tracking=True)
    website             = fields.Char(string='Website', related="reference.website", readonly=False, tracking=True)
    cellular            = fields.Char(string='Cellular', tracking=True)
    scope               = fields.Char(string='Scope', related="reference.scope", readonly=False, tracking=True)
    boundaries          = fields.Char(string='Boundaries', related="reference.boundaries", readonly=False, tracking=True)
    number_site         = fields.Char(string='Number of Site', related="reference.number_site", readonly=False, tracking=True)
    total_emp           = fields.Char(string='Total Employee', tracking=True)
    total_emp_site      = fields.Char(string='Total Employee Site Project', tracking=True)
    mandays             = fields.Char(string='Mandays', tracking=True)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran', tracking=True)
    is_amendment = fields.Boolean(string="Is Amendment Contract?")
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract",)
    category            = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',   'Silver'),
                            ('gold', 'Gold')
                        ], string='Category', related="reference.category", readonly=False, store=True)
    upload_npwp        = fields.Binary('Upload NPWP')
    file_name1       = fields.Char('Filename NPWP', tracking=True, store=True)
    issue_date = fields.Date(string="Issue Date", default=fields.Date.today, store=True)
    approve_date = fields.Datetime(string="Approve Date", store=True, tracking=True)

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    state_sales = fields.Selection([
        ('draft', 'Quotation'),
        ('cliennt_approval', 'Client Approval'),
        ('waiting_verify_operation', 'Waiting Verify Operation'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Lost'),
    ], string='Status Sales', store=True, tracking=True, related="sale_order_id.state")

    lines_audit_request   = fields.One2many('audit_request.line', 'reference_id', string="Lines Audit Request", index=True, tracking=True)

    # Site Line
    site_ids          = fields.One2many('crm.site.line', 'crm_site_id', string="Sites Audit Request", index=True, related='reference.site_ids', readonly=False, tracking=True)
    site_ids_14001    = fields.One2many('crm.site.line', 'crm_site_id_14001', string="Mandays Audit Request", index=True, related='reference.site_ids_14001', readonly=False, tracking=True)
    site_ids_45001    = fields.One2many('crm.site.line', 'crm_site_id_45001', string="Mandays Audit Request", index=True, related='reference.site_ids_45001', readonly=False, tracking=True)
    site_ids_27001    = fields.One2many('crm.site.line', 'crm_site_id_27001', string="Mandays Audit Request", index=True, related='reference.site_ids_27001', readonly=False, tracking=True)
    site_ids_27701    = fields.One2many('crm.site.line', 'crm_site_id_27701', string="Mandays Audit Request", index=True, related='reference.site_ids_27701', readonly=False, tracking=True)
    site_ids_27017    = fields.One2many('crm.site.line', 'crm_site_id_27017', string="Mandays Audit Request", index=True, related='reference.site_ids_27017', readonly=False, tracking=True)
    site_ids_27018    = fields.One2many('crm.site.line', 'crm_site_id_27018', string="Mandays Audit Request", index=True, related='reference.site_ids_27018', readonly=False, tracking=True)
    site_ids_27001_2022 = fields.One2many('crm.site.line', 'crm_site_id_27001_2022', string="Mandays Audit Request", index=True, related='reference.site_ids_27001_2022', readonly=False, tracking=True)
    site_ids_haccp    = fields.One2many('crm.site.line', 'crm_site_id_haccp', string="Mandays Audit Request", index=True, related='reference.site_ids_haccp', readonly=False, tracking=True)
    site_ids_gmp      = fields.One2many('crm.site.line', 'crm_site_id_gmp', string="Mandays Audit Request", index=True, related='reference.site_ids_gmp', readonly=False, tracking=True)
    site_ids_22000    = fields.One2many('crm.site.line', 'crm_site_id_22000', string="Mandays Audit Request", index=True, related='reference.site_ids_22000', readonly=False, tracking=True)
    site_ids_22301    = fields.One2many('crm.site.line', 'crm_site_id_22301', string="Mandays Audit Request", index=True, related='reference.site_ids_22301', readonly=False, tracking=True)
    site_ids_31000    = fields.One2many('crm.site.line', 'crm_site_id_31000', string="Mandays Audit Request", index=True, related='reference.site_ids_31000', readonly=False, tracking=True)
    site_ids_9994     = fields.One2many('crm.site.line', 'crm_site_id_9994', string="Mandays Audit Request", index=True, related='reference.site_ids_9994', readonly=False, tracking=True)
    site_ids_37001    = fields.One2many('crm.site.line', 'crm_site_id_37001', string="Mandays Audit Request", index=True, related='reference.site_ids_37001', readonly=False, tracking=True)
    site_ids_13485    = fields.One2many('crm.site.line', 'crm_site_id_13485', string="Mandays Audit Request", index=True, related='reference.site_ids_13485', readonly=False, tracking=True)
    site_ids_smk      = fields.One2many('crm.site.line', 'crm_site_id_smk', string="Mandays Audit Request", index=True, related='reference.site_ids_smk', readonly=False, tracking=True)
    site_ids_21000    = fields.One2many('crm.site.line', 'crm_site_id_21000', string="Mandays Audit Request", index=True, related='reference.site_ids_21000', readonly=False, tracking=True)
    site_ids_37301    = fields.One2many('crm.site.line', 'crm_site_id_37301', string="Mandays Audit Request", index=True, related='reference.site_ids_37301', readonly=False, tracking=True)
    site_ids_21001    = fields.One2many('crm.site.line', 'crm_site_id_21001', string="Mandays Audit Request", index=True, related='reference.site_ids_21001', readonly=False, tracking=True)
    site_ids_31001    = fields.One2many('crm.site.line', 'crm_site_id_31001', string="Mandays Audit Request", index=True, related='reference.site_ids_31001', readonly=False, tracking=True)
    
    # Mandays Line
    mandays_ids = fields.One2many('crm.mandays.line', 'crm_mandays_id', string="Mandays Audit Request", index=True, related='reference.mandays_ids', readonly=False, tracking=True)
    mandays_ids_14001 = fields.One2many('crm.mandays.line', 'crm_mandays_id_14001', string="Mandays Audit Request", index=True, related='reference.mandays_ids_14001', readonly=False, tracking=True)
    mandays_ids_45001 = fields.One2many('crm.mandays.line', 'crm_mandays_id_45001', string="Mandays Audit Request", index=True, related='reference.mandays_ids_45001', readonly=False, tracking=True)
    mandays_ids_27001 = fields.One2many('crm.mandays.line', 'crm_mandays_id_27001', string="Mandays Audit Request", index=True, related='reference.mandays_ids_27001', readonly=False, tracking=True)
    mandays_ids_27701 = fields.One2many('crm.mandays.line', 'crm_mandays_id_27701', string="Mandays Audit Request", index=True, related='reference.mandays_ids_27701', readonly=False, tracking=True)
    mandays_ids_27017 = fields.One2many('crm.mandays.line', 'crm_mandays_id_27017', string="Mandays Audit Request", index=True, related='reference.mandays_ids_27017', readonly=False, tracking=True)
    mandays_ids_27018 = fields.One2many('crm.mandays.line', 'crm_mandays_id_27018', string="Mandays Audit Request", index=True, related='reference.mandays_ids_27018', readonly=False, tracking=True)
    mandays_ids_27001_2022 = fields.One2many('crm.mandays.line', 'crm_mandays_id_27001_2022', string="Mandays Audit Request", index=True, related='reference.mandays_ids_27001_2022', readonly=False, tracking=True)
    mandays_ids_haccp = fields.One2many('crm.mandays.line', 'crm_mandays_id_haccp', string="Mandays Audit Request", index=True, related='reference.mandays_ids_haccp', readonly=False, tracking=True)
    mandays_ids_gmp = fields.One2many('crm.mandays.line', 'crm_mandays_id_gmp', string="Mandays Audit Request", index=True, related='reference.mandays_ids_gmp', readonly=False, tracking=True)
    mandays_ids_22000 = fields.One2many('crm.mandays.line', 'crm_mandays_id_22000', string="Mandays Audit Request", index=True, related='reference.mandays_ids_22000', readonly=False, tracking=True)
    mandays_ids_22301 = fields.One2many('crm.mandays.line', 'crm_mandays_id_22301', string="Mandays Audit Request", index=True, related='reference.mandays_ids_22301', readonly=False, tracking=True)
    mandays_ids_31000 = fields.One2many('crm.mandays.line', 'crm_mandays_id_31000', string="Mandays Audit Request", index=True, related='reference.mandays_ids_31000', readonly=False, tracking=True)
    mandays_ids_9994 = fields.One2many('crm.mandays.line', 'crm_mandays_id_9994', string="Mandays Audit Request", index=True, related='reference.mandays_ids_9994', readonly=False, tracking=True)
    mandays_ids_37001 = fields.One2many('crm.mandays.line', 'crm_mandays_id_37001', string="Mandays Audit Request", index=True, related='reference.mandays_ids_37001', readonly=False, tracking=True)
    mandays_ids_13485 = fields.One2many('crm.mandays.line', 'crm_mandays_id_13485', string="Mandays Audit Request", index=True, related='reference.mandays_ids_13485', readonly=False, tracking=True)
    mandays_ids_smk = fields.One2many('crm.mandays.line', 'crm_mandays_id_smk', string="Mandays Audit Request", index=True, related='reference.mandays_ids_smk', readonly=False, tracking=True)
    mandays_ids_21000 = fields.One2many('crm.mandays.line', 'crm_mandays_id_21000', string="Mandays Audit Request", index=True, related='reference.mandays_ids_21000', readonly=False, tracking=True)
    mandays_ids_37301 = fields.One2many('crm.mandays.line', 'crm_mandays_id_37301', string="Mandays Audit Request", index=True, related='reference.mandays_ids_37301', readonly=False, tracking=True)
    mandays_ids_21001 = fields.One2many('crm.mandays.line', 'crm_mandays_id_21001', string="Mandays Audit Request", index=True, related='reference.mandays_ids_21001', readonly=False, tracking=True)
    mandays_ids_31001 = fields.One2many('crm.mandays.line', 'crm_mandays_id_31001', string="Mandays Audit Request", index=True, related='reference.mandays_ids_31001', readonly=False, tracking=True)

    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True)
    iso_notification    = fields.Many2one('audit.notification', string="Notification Reference", readonly=True, tracking=True)
    # crm_reference       = fields.Many2one('tsi.history_kontrak', string="CRM Reference", readonly=True)

    state           =fields.Selection([
                            ('request',         'Request'),
                            ('reject',          'Reject'),
                            ('approve',         'Approve'),
                            ('revice',          'Revised'),
                            # ('approve_so',      'Approve SO'),
                            # ('approve_quot',    'Approve Quotation'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='request')

    state_crm =fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('lanjut', 'Lanjut'),
            ('lost','Loss'),
            ('suspend', 'Suspend'),
            ], string='Status', related="reference.state", store=True)

    referal = fields.Char(string='Referal', related="reference.referal", store=True)

    upload_contract = fields.Binary('Upload Kontrak')
    file_name       = fields.Char('Filename', tracking=True, store=True)
    closing_by = fields.Selection([
                ('konsultan',  'Konsultan'),
                ('direct',   'Direct'),
                ], string='Closing By', related="reference.closing_by", readonly=False, tracking=True, store=True)
    transport_by        = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Transport By', related="reference.transport_by", readonly=False, store=True)
    hotel_by            = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Akomodasi Hotel By', related="reference.hotel_by", readonly=False, store=True)
    tipe_klien_transport = fields.Selection([
                            ('reimbursement',  'Reimbursement'),
                            ('order_klien',   'Order By Klien'),
                        ], string='Tipe', related="reference.tipe_klien_transport", readonly=False, store=True)
    tipe_klien_hotel    = fields.Selection([
                            ('reimbursement',  'Reimbursement'),
                            ('order_klien',   'Order By Klien'),
                        ], string='Tipe', related="reference.tipe_klien_hotel", readonly=False, store=True)
    pic_crm             = fields.Selection([
                            ('dhea',  'Dhea'),
                            ('fauziah',   'Fauziah'),
                            ('mercy',   'Mercy'),
                            ('diara',   'Diara'),
                        ], string='PIC CRM', related="reference.pic_crm", readonly=False, store=True)

    pic_direct          = fields.Char(string='PIC Direct', related="reference.pic_direct", readonly=False, tracking=True)
    email_direct        = fields.Char(string='Email Direct', related="reference.email_direct", readonly=False, tracking=True)
    phone_direct        = fields.Char(string='No Telp Direct', related="reference.phone_direct", readonly=False, tracking=True)

    pic_konsultan1       = fields.Many2one('res.partner', string='PIC Konsultan', related="reference.pic_konsultan1", readonly=False, tracking=True, store=True)
    pic_konsultan       = fields.Char(string='PIC Konsultan', related="reference.pic_konsultan", readonly=False, tracking=True)
    email_konsultan     = fields.Char(string='Email Konsultan', related="reference.email_konsultan", readonly=False, tracking=True)
    phone_konsultan     = fields.Char(string='No Telp Konsultan', related="reference.phone_konsultan", readonly=False, tracking=True)

    note                = fields.Text(string='Note', tracking=True)

    # ISO 9001
    show_9001          = fields.Boolean(string='Additional Info', default=False)
    ea_code_9001       = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_9001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]", related="reference.ea_code_9001", readonly=False, tracking=True)
    accreditation_9001 = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_9001", readonly=False, tracking=True)

    # ISO 14001
    show_14001           = fields.Boolean(string='Additional Info', default=False)
    ea_code_14001        = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_14001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]", related="reference.ea_code_14001", readonly=False, tracking=True)
    accreditation_14001  = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_14001", readonly=False, tracking=True)

    # ISO 45001
    show_45001              = fields.Boolean(string='Additional Info', default=False)
    ea_code_45001           = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_45001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]", related="reference.ea_code_45001", readonly=False, tracking=True)
    accreditation_45001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_45001", readonly=False, tracking=True)

    # ISO 37001
    show_37001              = fields.Boolean(string='Additional Info', default=False)
    accreditation_37001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_37001", readonly=False, tracking=True)
    ea_code_37001           = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_37001', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_37001", readonly=False, tracking=True)

    # ISO 13485
    show_13485          = fields.Boolean(string='Additional Info', default=False)
    accreditation_13485 = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_13485", readonly=False, tracking=True)
    ea_code_13485       = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_13485', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_13485", readonly=False, tracking=True)

    # ISO 22000
    show_22000            = fields.Boolean(string='Additional Info', default=False)
    accreditation_22000   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_22000", readonly=False, tracking=True)
    ea_code_22000         = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_22000', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'ISO 22000:2018')]", related="reference.ea_code_22000", readonly=False, tracking=True)

    # ISO 21000
    show_21000            = fields.Boolean(string='Additional Info', default=False)
    accreditation_21000   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_21000", readonly=False, tracking=True)
    ea_code_21000         = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_21000', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_21000", readonly=False, tracking=True)

    # HACCP
    show_haccp            = fields.Boolean(string='Additional Info', default=False)
    accreditation_haccp   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_haccp", readonly=False, tracking=True)
    ea_code_haccp         = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_haccp', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'HACCP')]", related="reference.ea_code_haccp", readonly=False, tracking=True)

    # GMP
    show_gmp            = fields.Boolean(string='Additional Info', default=False)
    accreditation_gmp   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_gmp", readonly=False, tracking=True)
    ea_code_gmp         = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_gmp', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_gmp", readonly=False, tracking=True)

    # SMK3
    show_smk            = fields.Boolean(string='Additional Info', default=False)
    accreditation_smk   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_smk", readonly=False, tracking=True)
    ea_code_smk         = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_smk', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_smk", readonly=False, tracking=True)

    # ISO 27001
    show_27001             = fields.Boolean(string='Additional Info', default=False)
    ea_code_27001          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_27001', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_27001", readonly=False, tracking=True)
    accreditation_27001    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_27001", readonly=False, tracking=True)

    # ISO 27001 : 2022
    show_27001_2022             = fields.Boolean(string='Additional Info', default=False)
    ea_code_27001_2022          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_27001_2022', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_27001_2022", readonly=False, tracking=True)
    accreditation_27001_2022    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_27001_2022", readonly=False, tracking=True)

    # ISO 27701
    show_27701             = fields.Boolean(string='Additional Info', default=False)
    ea_code_27701          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_27701', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_27701", readonly=False, tracking=True)
    accreditation_27701    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_27701", readonly=False, tracking=True)

    # ISO 27017
    show_27017             = fields.Boolean(string='Show 27017', default=False)
    ea_code_27017          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_27017', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_27017", readonly=False, tracking=True)
    accreditation_27017    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_27017", readonly=False, tracking=True)

    # ISO 27018
    show_27018             = fields.Boolean(string='Show 27018', default=False)
    ea_code_27018          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_27018', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_27018", readonly=False, tracking=True)
    accreditation_27018    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_27018", readonly=False, tracking=True)

    # ISO 31000
    show_31000             = fields.Boolean(string='Show 31000', default=False)
    ea_code_31000          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_31000', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_31000", readonly=False, tracking=True)
    accreditation_31000    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_31000", readonly=False, tracking=True)

    # ISO 22301
    show_22301             = fields.Boolean(string='Show 22301', default=False)
    ea_code_22301          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_22301', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_22301", readonly=False, tracking=True)
    accreditation_22301    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_22301", readonly=False, tracking=True)

    # ISO 9994
    show_9994             = fields.Boolean(string='Show 9994', default=False)
    ea_code_9994          = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_9994', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_9994", readonly=False, tracking=True)
    accreditation_9994    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_9994", readonly=False, tracking=True)

    # ISO 37301
    show_37301              = fields.Boolean(string='Show 13485', default=False)
    accreditation_37301     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_37301", readonly=False, tracking=True)
    ea_code_37301           = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_37301', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_37301", readonly=False, tracking=True)

    # ISO 31001
    show_31001              = fields.Boolean(string='Show 13485', default=False)
    accreditation_31001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_31001", readonly=False, tracking=True)
    ea_code_31001           = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_31001', string="IAF Code", domain=[('name', '=', 'Not Applicable')], related="reference.ea_code_31001", readonly=False, tracking=True)

    # ISO 21001
    show_21001              = fields.Boolean(string='Show 13485', default=False)
    accreditation_21001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_21001", readonly=False, tracking=True)
    ea_code_21001           = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_21001', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'ISO 21001:2018')]", related="reference.ea_code_21001", readonly=False, tracking=True)

    # tgl_perkiraan_selesai = fields.Date(string="Plan of audit date", related="reference.tgl_perkiraan_selesai", readonly=False, store=True)
    tgl_perkiraan_audit_selesai = fields.Selection(string="Plan of audit date", related="reference.tgl_perkiraan_audit_selesai", readonly=False, store=True)

    def send_whatsapp_status_new_request(self):
        dokumen_id = self.id
        nama_dokumen = self.name
        nama_customer = self.reference.partner_id.name
        standard = self.iso_standard_ids.name
        audit_stage_map = {
            'surveilance1': 'Surveillance 1',
            'surveilance2': 'Surveillance 2',
            'recertification': 'Recertification'
        }

        tahap_audit = self.audit_stage
        tahap_audit_label = audit_stage_map.get(tahap_audit, 'Unknown')
        
        user = self.env['res.users'].sudo().search([("id", "=", 18)])
        nomor = user.employee_ids.phone_wa 
        
        url = "web#id=%s&menu_id=751&action=1008&model=tsi.audit.request&view_type=form" % (dokumen_id)
        
        payload = {
                "messaging_product": "whatsapp",
                "to": nomor,
                "type": "template",
                "template": {
                    "name": "template_notif_new_audit_request_url_draf",
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
    
    def send_whatsapp_status_approve_request(self):
        dokumen_id = self.id
        nama_dokumen = self.name
        nama_customer = self.reference.partner_id.name
        standard = self.iso_standard_ids.name
        audit_stage_map = {
            'surveilance1': 'Surveillance 1',
            'surveilance2': 'Surveillance 2',
            'recertification': 'Recertification'
        }

        tahap_audit = self.audit_stage
        tahap_audit_label = audit_stage_map.get(tahap_audit, 'Unknown')
        
        user = self.env['res.users'].sudo().search([("id", "in", [10,38])])
        nomors = [u.employee_ids.phone_wa for u in user]
        
        url = "web#id=%s&menu_id=751&action=1008&model=tsi.audit.request&view_type=form" % (dokumen_id)
        
        for nomor in nomors:
            payload = {
                    "messaging_product": "whatsapp",
                    "to": nomor,
                    "type": "template",
                    "template": {
                        "name": "template_notif_status_audit_request_approve_url_draf",
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
                                            
    def send_whatsapp_status_reject_request(self):
        dokumen_id = self.id
        nama_dokumen = self.name
        nama_customer = self.reference.partner_id.name
        standard = self.iso_standard_ids.name
        audit_stage_map = {
            'surveilance1': 'Surveillance 1',
            'surveilance2': 'Surveillance 2',
            'recertification': 'Recertification'
        }

        tahap_audit = self.audit_stage
        tahap_audit_label = audit_stage_map.get(tahap_audit, 'Unknown')
        
        creator = self.create_uid
        nomor = creator.employee_ids.phone_wa
        
        url = "web#id=%s&menu_id=751&action=1008&model=tsi.audit.request&view_type=form" % (dokumen_id)
        
        payload = {
                "messaging_product": "whatsapp",
                "to": nomor,
                "type": "template",
                "template": {
                    "name": "template_notif_status_audit_request_reject_url_draf",
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

    def send_whatsapp_status_reject_revice(self):
        dokumen_id = self.id
        nama_dokumen = self.name
        nama_customer = self.reference.partner_id.name
        standard = self.iso_standard_ids.name
        audit_stage_map = {
            'surveilance1': 'Surveillance 1',
            'surveilance2': 'Surveillance 2',
            'recertification': 'Recertification'
        }

        tahap_audit = self.audit_stage
        tahap_audit_label = audit_stage_map.get(tahap_audit, 'Unknown')
        
        user = self.env['res.users'].sudo().search([("id", "=", 18)])
        nomor = user.employee_ids.phone_wa 
        
        url = "web#id=%s&menu_id=751&action=1008&model=tsi.audit.request&view_type=form" % (dokumen_id)
        
        payload = {
                "messaging_product": "whatsapp",
                "to": nomor,
                "type": "template",
                "template": {
                    "name": "template_notif_revice_audit_request_url_draf",
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

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.audit.request')
        vals['name'] = sequence or _('New')
        result = super(AuditRequest, self).create(vals)
        result.send_whatsapp_status_new_request()
        return result
    
    
    def set_reject(self):
        self.send_whatsapp_status_reject_request()
        self.write({'state': 'reject'})

        self.reference.state = 'reject'
        # self.send_reject_message()
        # self.send_reject_email()          
        return True

    # @api.model
    # def action_set_default_cycle(self, *args, **kwargs):
    #     records = self.search([('cycle', '=', False)])
    #     records.write({'cycle': 'cycle1'})
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': 'Success',
    #             'message': f'{len(records)} record(s) updated to cycle1.',
    #             'type': 'success',
    #             'sticky': False,
    #         }
    #     }

    # def send_reject_message(self):
    #     self.ensure_one()

    #     if not self.user_id or not self.user_id.partner_id:
    #         _logger.error("❌ ERROR: No valid partner for user_id: %s", self.user_id.id)
    #         return False

    #     partner_id = self.user_id.partner_id.id

    #     channel = self.env['mail.channel'].sudo().search([
    #         ('channel_partner_ids', 'in', [partner_id]),
    #         ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
    #         ('channel_type', '=', 'chat')
    #     ], limit=1)

    #     if not channel:
    #         channel = self.env['mail.channel'].sudo().create({
    #             'name': f"Chat with {self.user_id.name}",
    #             'channel_type': 'chat',
    #             'public': 'private',
    #             'channel_partner_ids': [(6, 0, [partner_id, self.env.user.partner_id.id])]
    #         })

    #     standard_list = ", ".join(self.iso_standard_ids.mapped("name")) if self.iso_standard_ids else "No Standards"

    #     message_body = f"""
    #         <p><strong>Audit Request Rejected</strong></p>
    #         <p>Your audit request has been <strong>rejected</strong>.</p>
    #         <p><strong>Request ID:</strong> {self.name}</p>
    #         <p><strong>Company Name:</strong> {self.partner_id.name}</p>
    #         <p><strong>Standard:</strong> {standard_list}</p>
    #         <p><strong>Status:</strong> {self.state}</p>
    #         <p>Thank you.</p>
    #     """

    #     channel.message_post(
    #         body=message_body,
    #         subject="Audit Request Rejected",
    #         message_type="comment",
    #         subtype_xmlid="mail.mt_comment",
    #         author_id=self.env.user.partner_id.id,
    #     )

    #     _logger.info("✅ Direct message sent to partner ID: %s via chat", partner_id)
    #     return True

    # def send_reject_email(self):
    #     self.ensure_one()
    #     template = self.env.ref('v15_tsi.email_template_reject_audit_request')

    #     recipient_email = self.user_id.partner_id.email

    #     if not recipient_email:
    #         _logger.error("❌ ERROR: No valid email found for user_id: %s", self.user_id.id)
    #         return False

    #     _logger.info("✅ Sending rejection email to: %s", recipient_email)

    #     if template:
    #         template.sudo().send_mail(self.id, force_send=True, email_values={'email_to': recipient_email})

    def set_revice(self):
        self.write({'state': 'revice'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_audit_request_action')
        action.update({
            'context': {'default_customer': self.partner_id.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_audit_request_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_audit_request_view_tree').id, 'tree')],
        })
        # Kirim WhatsApp dulu dari record ini, bukan dari action dict
        self.send_whatsapp_status_reject_revice()
        return action

    def set_request(self):
        self.write({'state': 'request'})            
        return True

    def set_approve(self):
        self.send_whatsapp_status_approve_request()
        self.write({
            'state': 'approve',
            'approve_date': fields.Datetime.now(),
        })            
        return True

    def create_quotation(self):
        return {
            'name': "Create Kontrak",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit_request',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_request_view').id,
            'target': 'new'
        }

    def generate_ops(self):
        
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'iso_reference': self.iso_reference.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tipe_pembayaran': self.tipe_pembayaran,
            'nomor_kontrak': self.no_kontrak,  # Mengisi nomor_kontrak
            'nomor_quotation': self.no_kontrak,  # Mengisi nomor_quotation
            'contract_type': self.contract_type,
            # 'template_quotation': self.template_quotation,
            # 'dokumen_sosialisasi': self.dokumen_sosialisasi,
            # 'file_name': self.file_name,
            # 'file_name1': self.file_name1,
        })

        for line in self.lines_audit_request:
            product = line.product_id  
            
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,  
                'product_id': product.id if product else False, 
                'audit_tahapan': line.audit_tahapan,
                'tahun': line.tahun,
                'price_unit': line.price,
            })

        # for line in self.lines_audit_request:
        #     self.env['tsi.order.options'].create({
        #         'ordered_id': sale_order.id,
        #         # 'product_id': line.product_id.id,
        #         'audit_tahapans': line.audit_tahapan,
        #         'tahun_audit': line.tahun,
        #         'price_units': line.price,
        #         # 'product_uom_qty': 1.0,  
        #         # 'tax_id': [(6, 0, line.product_id.taxes_id.ids)] 
        #     })

        # sale_order.action_confirm()

        sale_order.write({'state': 'sent'}) 

        return True

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
                obj.show_gmp = False
                obj.show_22000 = False
                obj.show_22301 = False
                obj.show_31000 = False
                obj.show_37001 = False
                obj.show_13485 = False
                obj.show_smk = False
                obj.show_21000 = False  
                obj.show_37301 = False
                obj.show_9994 = False
                obj.show_31001 = False
                obj.show_21001 = False
                # obj.show_ispo = False               
                obj.show_9001 = False
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISO 14001:2015' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_14001 = True
                    if standard.name == 'ISO 45001:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_45001 = True
                    if standard.name == 'ISO/IEC 27001:2013' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_27001 = True
                    if standard.name == 'ISO/IEC 27001:2022' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_27001_2022 = True
                    if standard.name == 'ISO/IEC 27701:2019' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_27701 = True
                    if standard.name == 'ISO/IEC 27017:2015' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_27017 = True
                    if standard.name == 'ISO/IEC 27018:2019' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_27018 = True
                    if standard.name == 'ISO 22000:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_22000 = True
                    if standard.name == 'ISO 22301:2019' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_22301 = True
                    if standard.name == 'HACCP' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_haccp = True
                    if standard.name == 'ISO 31000:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_31000 = True
                    if standard.name == 'ISO 13485:2016' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_13485 = True
                    if standard.name == 'ISO 37301:2021' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_37301 = True
                    if standard.name == 'ISO 9994:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_9994 = True
                    if standard.name == 'ISO 37001:2016' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_37001 = True
                    if standard.name == 'SMK3' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_smk = True
                    if standard.name == 'GMP' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_gmp = True
                    if standard.name == 'ISO 21000:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_21000 = True
                    if standard.name == 'ISO 21001:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_21001 = True
                    if standard.name == 'ISO 31001:2018' :
                        if obj.show_9001 != True :
                            obj.show_9001 = False
                        obj.show_31001 = True
                    # if standard.name == 'ISPO' :
                    #     if obj.show_ispo != True :
                    #         obj.show_ispo = False
                    #     obj.show_ispo = True
                    elif standard.name == 'ISO 9001:2015' :
                        obj.show_9001 = True

    # def generate_ops(self):
    #     if self.tipe_pembayaran:
    #         if self.iso_standard_ids:
    #             notification = self.env['audit.notification'].create({
    #                 'iso_reference': self.iso_reference.id,
    #                 'audit_request_id': self.id,
    #                 'tipe_pembayaran': self.tipe_pembayaran,
    #                 'iso_standard_ids': self.iso_standard_ids,
    #                 'customer': self.partner_id.id
    #             })
    #             self.iso_notification = notification.id

    #             for standard in self.iso_standard_ids:
    #                 if self.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                        
    #                     program = self.env['ops.program'].create({
    #                         'iso_reference': self.iso_reference.id,
    #                         'audit_request_id': self.id,
    #                         'iso_standard_ids': [(6, 0, [standard.id])],
    #                         'type_client': self.tipe_pembayaran,
    #                         'notification_id': notification.id,
    #                         'customer': self.partner_id.id
    #                     })

    #                     report = self.env['ops.report'].create({
    #                         'iso_reference': self.iso_reference.id,
    #                         'audit_request_id': self.id,
    #                         'iso_standard_ids': [(6, 0, [standard.id])],
    #                         'notification_id': notification.id,
    #                         'customer': self.partner_id.id
    #                     })

    #                 else:
    #                     program = self.env['ops.program'].create({
    #                         'iso_reference': self.iso_reference.id,
    #                         'audit_request_id': self.id,
    #                         'iso_standard_ids': [(6, 0, [standard.id])],
    #                         'type_client': self.tipe_pembayaran,
    #                         'notification_id': notification.id,
    #                         'customer': self.partner_id.id
    #                     })

    #             sale_order = self.env['sale.order'].create({
    #                 'partner_id': self.partner_id.id,
    #                 'iso_reference': self.iso_reference.id,
    #                 'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
    #                 'tipe_pembayaran': self.tipe_pembayaran,
    #                 'template_quotation' : self.template_quotation,
    #                 'dokumen_sosialisasi' : self.dokumen_sosialisasi,
    #                 'file_name' : self.file_name,
    #                 'file_name1' : self.file_name1,
    #             })

    #             for line in self.lines_audit_request:
    #                 self.env['sale.order.line'].create({
    #                     'order_id': sale_order.id,
    #                     'product_id': line.product_id.id,
    #                     'audit_tahapan': line.audit_tahapan,
    #                     'tahun' : line.tahun,  
    #                     'price_unit': line.price,
    #                     # 'product_uom_qty': 1.0,  
    #                     # 'tax_id': [(6, 0, line.product_id.taxes_id.ids)]  
    #                 })

    #             sale_order.action_confirm()

    #         else:
    #             raise UserError('Tidak ada standar ISO yang terkait.')
    #     else:
    #         raise UserError('Mohon tentukan tipe pembayaran.')

    #     return True


    # def create_sales(self):
    #     self.write({'state': 'approve_quot'})            

    #     return {
    #         'name': "Create Quotation",
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'tsi.wizard_audit_quotation',
    #         'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_quotation_view').id,
    #         'target': 'new'
    #     }

    # def create_quot(self):
    #     self.write({'state': 'approve_so'})            
    #     return {
    #         'name': "Create Quotation",
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'tsi.wizard_audit_quotation',
    #         'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_quotation_view').id,
    #         'target': 'new'
    #     }

class AuditRequestLines(models.Model):
    _name         = 'audit_request.line'
    _description  = 'Audit Request Line'
    _inherit      = ['mail.thread', 'mail.activity.mixin']

    reference_id  = fields.Many2one('tsi.audit.request', string="Reference")
    product_id    = fields.Many2one('product.product', string='Product', store=True)
    audit_tahapan = fields.Selection([
        ('Surveillance 1', 'Surveillance 1'),
        ('Surveillance 2', 'Surveillance 2'),
        ('Surveillance 3', 'Surveillance 3'),
        ('Surveillance 4', 'Surveillance 4'),
        ('Surveillance 5', 'Surveillance 5'),
        ('Surveillance 6', 'Surveillance 6'),
        ('Recertification', 'Recertification 1'),
        ('Recertification 2', 'Recertification 2'),
        ('Recertification 3', 'Recertification 3'),
    ], string='Audit Stage', index=True, tracking=True)
    price         = fields.Float(string='Price', store=True)
    up_value      = fields.Float(string='Up Value', store=True)
    loss_value    = fields.Float(string='Loss Value', store=True)
    tahun         = fields.Char("Tahun", tracking=True)
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)

    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for record in self:
            if record.price > 0:
                record.percentage = (record.fee / record.price) * 100
            else:
                record.percentage = 0

class AuditRequestSites(models.Model):
    _name = 'audit_request.site'
    _description = 'Audit Request Site'

    # site_id         = fields.Many2one('tsi.audit.request', string='Audit Request Sites', required=True, ondelete='cascade')
    tipe_site       = fields.Char('Type(HO, Factory etc)', tracking=True) 
    address         = fields.Char('Address', tracking=True) 
    effective_emp   = fields.Char('Total No. of Effective Employees', tracking=True) 
    total_emp       = fields.Char(string='Total No. of All Employees', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditRequestSites, self).create(vals)
        site = record.site_id
        site.message_post(body=f"Created Tipe: {record.tipe_site}, Address: {record.address}, Total No. of Effective Employees: {record.effective_emp}, Total No. of All Employees: {record.total_emp}")
        return record

    def write(self, vals):
        res = super(AuditRequestSites, self).write(vals)
        for record in self:
            site = record.site_id
            site.message_post(body=f"Updated Tipe: {record.tipe_site}, Address: {record.address}, Total No. of Effective Employees: {record.effective_emp}, Total No. of All Employees: {record.total_emp}")
        return res

    def unlink(self):
        for record in self:
            site = record.site_id
            site.message_post(body=f"Deleted Tipe: {record.tipe_site}, Address: {record.address}, Total No. of Effective Employees: {record.effective_emp}, Total No. of All Employees: {record.total_emp}")
        return super(AuditRequestSites, self).unlink()

class AuditRequestMandays(models.Model):
    _name = 'audit_request.mandays'
    _description = 'Audit Request Mandays'

    # mandays_id        = fields.Many2one('tsi.audit.request', string='Audit Request Mandays', required=True, ondelete='cascade')
    nama_site         = fields.Char(string='Nama Site', tracking=True)
    stage_1           = fields.Char(string='Stage 1', tracking=True)
    stage_2           = fields.Char(string='Stage 2', tracking=True)
    surveilance_1     = fields.Char(string='Surveillance 1', tracking=True)
    surveilance_2     = fields.Char(string='Surveillance 2', tracking=True)
    surveilance_3     = fields.Char(string='Surveillance 3', tracking=True)
    surveilance_4     = fields.Char(string='Surveillance 4', tracking=True)
    recertification   = fields.Char(string='Recertification', tracking=True)
    recertification_2 = fields.Char(string='Recertification 2', tracking=True)
    remarks           = fields.Char(string='Remarks', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditRequestMandays, self).create(vals)
        mandays = record.mandays_id
        mandays.message_post(body=f"Created Nama Site: {record.nama_site}, Stage 1: {record.stage_1}, Stage 2: {record.stage_2}, Surveillance 1: {record.surveilance_1}, Surveillance 2: {record.surveilance_2}, Surveillance 3: {record.surveilance_3}, Surveillance 4: {record.surveilance_4}, Recertification: {record.recertification}, Recertification 2: {record.recertification_2}, Remarks: {record.remarks}")
        return record

    def write(self, vals):
        res = super(AuditRequestMandays, self).write(vals)
        for record in self:
            mandays = record.mandays_id
            mandays.message_post(body=f"Updated Nama Site: {record.nama_site}, Stage 1: {record.stage_1}, Stage 2: {record.stage_2}, Surveillance 1: {record.surveilance_1}, Surveillance 2: {record.surveilance_2}, Surveillance 3: {record.surveilance_3}, Surveillance 4: {record.surveilance_4}, Recertification: {record.recertification}, Recertification 2: {record.recertification_2}, Remarks: {record.remarks}")
        return res

    def unlink(self):
        for record in self:
            mandays = record.mandays_id
            mandays.message_post(body=f"Deleted Nama Site: {record.nama_site}, Stage 1: {record.stage_1}, Stage 2: {record.stage_2}, Surveillance 1: {record.surveilance_1}, Surveillance 2: {record.surveilance_2}, Surveillance 3: {record.surveilance_3}, Surveillance 4: {record.surveilance_4}, Recertification: {record.recertification}, Recertification 2: {record.recertification_2}, Remarks: {record.remarks}")
        return super(AuditRequestMandays, self).unlink()