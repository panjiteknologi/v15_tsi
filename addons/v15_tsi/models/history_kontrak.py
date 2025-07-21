from odoo import models, fields, api, tools
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError

class HistoryKontrak(models.Model):
    _name           = "tsi.history_kontrak"
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = "Database CRM"
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    no_kontrak          = fields.Char(string='Nomor Kontrak', tracking=True)
    tanggal_kontrak     = fields.Date(string="Expiry Date", tracking=True)
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', readonly=False, tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False, tracking=True)
    nilai_kontrak       = fields.Float(string='Nilai Kontrak', tracking=True)
    # level               = fields.Char(string='Level', tracking=True, readonly=True)
    segment             = fields.Many2many('res.partner.category', string='Segment', related="partner_id.category_id", readonly=False, tracking=True)
    alasan              = fields.Many2one('crm.alasan', string="Alasan")
    closing_by          = fields.Selection([
                            ('konsultan',  'Konsultan'),
                            ('direct',   'Direct'),
                        ], string='Closing By')
    transport_by        = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Transport By')
    hotel_by            = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Akomodasi Hotel By')
    tipe_klien_transport = fields.Selection([
                            ('reimbursement',  'Reimbursement'),
                            ('order_klien',   'Oder By Klien'),
                        ], string='Tipe')
    tipe_klien_hotel    = fields.Selection([
                            ('reimbursement',  'Reimbursement'),
                            ('order_klien',   'Oder By Klien'),
                        ], string='Tipe')
    pic_crm             = fields.Selection([
                            ('dhea',  'Dhea'),
                            ('fauziah',   'Fauziah'),
                            ('mercy',   'Mercy'),
                            ('diara',   'Diara'),
                        ], string='PIC CRM')
    
    pic_direct          = fields.Char(string='PIC Direct', tracking=True)
    email_direct        = fields.Char(string='Email Direct', tracking=True)
    phone_direct        = fields.Char(string='No Telp Direct', tracking=True)

    pic_konsultan1       = fields.Many2one('res.partner', string='PIC Konsultan', tracking=True, store=True)
    pic_konsultan       = fields.Char(string='PIC Konsultan', tracking=True)
    email_konsultan     = fields.Char(string='Email Konsultan', tracking=True)
    phone_konsultan     = fields.Char(string='No Telp Konsultan', tracking=True)

    office_address      = fields.Char(string='Office Address', related="partner_id.office_address", readonly=False, tracking=True)
    invoicing_address   = fields.Char(string="Invoicing Address", related="partner_id.invoice_address", readonly=False, tracking=True)
    telp                = fields.Char(string='Telp', related="partner_id.phone", readonly=False, tracking=True)
    email               = fields.Char(string='Email', related="partner_id.email", readonly=False, tracking=True)
    website             = fields.Char(string='Website', related="partner_id.website", readonly=False, tracking=True)
    scope               = fields.Char(string='Scope', tracking=True)
    boundaries          = fields.Char(string='Boundaries', default="All related area, department & functions within scope")
    number_site         = fields.Char(string='Number of Site', related="partner_id.number_site", readonly="False", tracking=True)

    # ISO 9001
    show_9001          = fields.Boolean(string='Additional Info', default=False)
    ea_code_9001       = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_9001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]", tracking=True)
    accreditation_9001 = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 14001
    show_14001           = fields.Boolean(string='Additional Info', default=False)
    ea_code_14001        = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_14001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]", tracking=True)
    accreditation_14001  = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 45001
    show_45001              = fields.Boolean(string='Additional Info', default=False)
    ea_code_45001           = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_45001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]", tracking=True)
    accreditation_45001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 37001
    show_37001              = fields.Boolean(string='Additional Info', default=False)
    accreditation_37001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_37001           = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_37001', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)

    # ISO 13485
    show_13485          = fields.Boolean(string='Additional Info', default=False)
    accreditation_13485 = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_13485       = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_13485', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)

    # ISO 22000
    show_22000            = fields.Boolean(string='Additional Info', default=False)
    accreditation_22000   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_22000         = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_22000', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'ISO 22000:2018')]", tracking=True)

    # HACCP
    show_haccp            = fields.Boolean(string='Show HACCP', default=False)
    accreditation_haccp   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_haccp         = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_haccp', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'HACCP')]", tracking=True)

    # GMP
    show_gmp            = fields.Boolean(string='Show GMP', default=False)
    accreditation_gmp   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_gmp         = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_gmp', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)

    # SMK3
    show_smk            = fields.Boolean(string='Show SMK3', default=False)
    accreditation_smk   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_smk         = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_smk', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)

    # ISO 21000
    show_21000            = fields.Boolean(string='Additional Info', default=False)
    accreditation_21000   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_21000         = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_21000', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)

    # ISO 27001
    show_27001             = fields.Boolean(string='Additional Info', default=False)
    ea_code_27001          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_27001', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_27001    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 27001 : 2022
    show_27001_2022             = fields.Boolean(string='Additional Info', default=False)
    ea_code_27001_2022          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_27001_2022', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_27001_2022    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 27701
    show_27701             = fields.Boolean(string='Additional Info', default=False)
    ea_code_27701          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_27701', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_27701    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 27017
    show_27017             = fields.Boolean(string='Show 27017', default=False)
    ea_code_27017          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_27017', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_27017    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 27018
    show_27018             = fields.Boolean(string='Show 27018', default=False)
    ea_code_27018          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_27018', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_27018    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 31000
    show_31000             = fields.Boolean(string='Show 31000', default=False)
    ea_code_31000          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_31000', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_31000    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 22301
    show_22301             = fields.Boolean(string='Show 22301', default=False)
    ea_code_22301          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_22301', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_22301    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 9994
    show_9994             = fields.Boolean(string='Show 9994', default=False)
    ea_code_9994          = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_9994', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_9994    = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 37301
    show_37301              = fields.Boolean(string='Show 13485', default=False)
    accreditation_37301     = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    ea_code_37301           = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_37301', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)

    # ISO 21001
    show_21001          = fields.Boolean(string='Additional Info', default=False)
    ea_code_21001       = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_21001', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'ISO 21001:2018')]", tracking=True)
    accreditation_21001 = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISO 31001
    show_31001          = fields.Boolean(string='Additional Info', default=False)
    ea_code_31001       = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_31001', string="IAF Code", domain=[('name', '=', 'Not Applicable')], tracking=True)
    accreditation_31001 = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    # ISPO
    show_ispo          = fields.Boolean(string='Additional Info', default=False)
    ea_code_ispo       = fields.Many2many('tsi.ea_code', 'rel_history_kontrak_ea_ispo', string="IAF Code", tracking=True)
    accreditation_ispo = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)

    site_ids            = fields.One2many('crm.site.line', 'crm_site_id', string='Site Lines')
    site_ids_14001      = fields.One2many('crm.site.line', 'crm_site_id_14001', string='Site Lines')
    site_ids_45001      = fields.One2many('crm.site.line', 'crm_site_id_45001', string='Site Lines')
    site_ids_27001      = fields.One2many('crm.site.line', 'crm_site_id_27001', string='Site Lines')
    site_ids_27701      = fields.One2many('crm.site.line', 'crm_site_id_27701', string='Site Lines')
    site_ids_27017      = fields.One2many('crm.site.line', 'crm_site_id_27017', string='Site Lines')
    site_ids_27018      = fields.One2many('crm.site.line', 'crm_site_id_27018', string='Site Lines')
    site_ids_27001_2022 = fields.One2many('crm.site.line', 'crm_site_id_27001_2022', string='Site Lines')
    site_ids_haccp      = fields.One2many('crm.site.line', 'crm_site_id_haccp', string='Site Lines')
    site_ids_gmp        = fields.One2many('crm.site.line', 'crm_site_id_gmp', string='Site Lines')
    site_ids_22000      = fields.One2many('crm.site.line', 'crm_site_id_22000', string='Site Lines')
    site_ids_22301      = fields.One2many('crm.site.line', 'crm_site_id_22301', string='Site Lines')
    site_ids_31000      = fields.One2many('crm.site.line', 'crm_site_id_31000', string='Site Lines')
    site_ids_9994       = fields.One2many('crm.site.line', 'crm_site_id_9994', string='Site Lines')
    site_ids_37001      = fields.One2many('crm.site.line', 'crm_site_id_37001', string='Site Lines')
    site_ids_13485      = fields.One2many('crm.site.line', 'crm_site_id_13485', string='Site Lines')
    site_ids_smk        = fields.One2many('crm.site.line', 'crm_site_id_smk', string='Site Lines')
    site_ids_21000      = fields.One2many('crm.site.line', 'crm_site_id_21000', string='Site Lines')
    site_ids_37301      = fields.One2many('crm.site.line', 'crm_site_id_37301', string='Site Lines')
    site_ids_21001      = fields.One2many('crm.site.line', 'crm_site_id_21001', string='Site Lines')
    site_ids_31001      = fields.One2many('crm.site.line', 'crm_site_id_31001', string='Site Lines')

    site_ids_ispo        = fields.One2many('crm.site.line', 'crm_site_id_ispo', string='Site Lines')

    # Mandays Lines
    mandays_ids = fields.One2many('crm.mandays.line', 'crm_mandays_id', string='Mandays Lines')
    mandays_ids_14001      = fields.One2many('crm.mandays.line', 'crm_mandays_id_14001', string='Mandays Lines')
    mandays_ids_45001      = fields.One2many('crm.mandays.line', 'crm_mandays_id_45001', string='Mandays Lines')
    mandays_ids_27001      = fields.One2many('crm.mandays.line', 'crm_mandays_id_27001', string='Mandays Lines')
    mandays_ids_27701      = fields.One2many('crm.mandays.line', 'crm_mandays_id_27701', string='Mandays Lines')
    mandays_ids_27017      = fields.One2many('crm.mandays.line', 'crm_mandays_id_27017', string='Mandays Lines')
    mandays_ids_27018      = fields.One2many('crm.mandays.line', 'crm_mandays_id_27018', string='Mandays Lines')
    mandays_ids_27001_2022 = fields.One2many('crm.mandays.line', 'crm_mandays_id_27001_2022', string='Mandays Lines')
    mandays_ids_haccp      = fields.One2many('crm.mandays.line', 'crm_mandays_id_haccp', string='Mandays Lines')
    mandays_ids_gmp        = fields.One2many('crm.mandays.line', 'crm_mandays_id_gmp', string='Mandays Lines')
    mandays_ids_22000      = fields.One2many('crm.mandays.line', 'crm_mandays_id_22000', string='Mandays Lines')
    mandays_ids_22301      = fields.One2many('crm.mandays.line', 'crm_mandays_id_22301', string='Mandays Lines')
    mandays_ids_31000      = fields.One2many('crm.mandays.line', 'crm_mandays_id_31000', string='Mandays Lines')
    mandays_ids_9994       = fields.One2many('crm.mandays.line', 'crm_mandays_id_9994', string='Mandays Lines')
    mandays_ids_37001      = fields.One2many('crm.mandays.line', 'crm_mandays_id_37001', string='Mandays Lines')
    mandays_ids_13485      = fields.One2many('crm.mandays.line', 'crm_mandays_id_13485', string='Mandays Lines')
    mandays_ids_smk        = fields.One2many('crm.mandays.line', 'crm_mandays_id_smk', string='Mandays Lines')
    mandays_ids_21000      = fields.One2many('crm.mandays.line', 'crm_mandays_id_21000', string='Mandays Lines')
    mandays_ids_37301      = fields.One2many('crm.mandays.line', 'crm_mandays_id_37301', string='Mandays Lines')
    mandays_ids_21001      = fields.One2many('crm.mandays.line', 'crm_mandays_id_21001', string='Mandays Lines')
    mandays_ids_31001      = fields.One2many('crm.mandays.line', 'crm_mandays_id_31001', string='Mandays Lines')

    mandays_ids_ispo        = fields.One2many('crm.mandays.line', 'crm_mandays_id_ispo', string='Mandays Lines')

    alamat              = fields.Selection([
                            ('dalam_kota',  'Dalam Kota'),
                            ('luar_kota',   'Luar Kota'),
                        ], string='Alamat')
    category            = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',   'Silver'),
                            ('gold', 'Gold')
                        ], string='Category', related="partner_id.kategori", readonly=False, store=True)
    level_audit         = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2')
                        ], string='Level Audit ISO')
    level_audit_ispo    = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2'),
                            ('sv3', 'SV3'),
                            ('sv4', 'SV4')
                        ], string='Level Audit ISPO')
    # is_konsultan        = fields.Boolean(string='Konsultan', default=False)
    # is_direct           = fields.Boolean(string='Direct', default=False)
    # is_ia_retern        = fields.Boolean(string='IA Retern', default=False)
    akreditasi          = fields.Many2one('tsi.iso.accreditation', string='Akreditasi')
    hk_pic_ids          = fields.One2many('history_kontrak.pic', 'hiskon_id', string="PIC History Kotrak")
    pic                 = fields.Many2one('res.partner', string="PIC", tracking=True, related="partner_id.contact_client_ids.name_client", readonly=False)
    sales               = fields.Many2one('res.users', string='Sales Person', related="partner_id.user_id", readonly=False, tracking=True, store=True)
    associate           = fields.Many2one('res.partner', string="Associate", tracking=True , related="partner_id.custom_contact_idss.name_associates", readonly=False, store=True)
    status_tahun_aktif  = fields.Char(string='Status Tahun Aktif', tracking=True)
    referal             = fields.Char(string='Referal', tracking=True)
    show_tahapan      = fields.Boolean(string='Additional Info', default=False, tracking=True)
    show_initial        = fields.Boolean(string='Show Initial', default=False)
    show_survilance1    = fields.Boolean(string='Show Survilance 1', default=False)
    show_survilance2    = fields.Boolean(string='Show Survilance 2', default=False)
    show_survilance3    = fields.Boolean(string='Show Survilance 3', default=False)
    show_survilance4    = fields.Boolean(string='Show Survilance 4', default=False)
    show_recertification = fields.Boolean(string='Show Recertification', default=False)
    show_survilance5    = fields.Boolean(string='Show Survilance 5', default=False)
    show_survilance6    = fields.Boolean(string='Show Survilance 6', default=False)
    show_recertification2 = fields.Boolean(string='Show Recertification 2', default=False)
    show_recertification3 = fields.Boolean(string='Show Recertification 3', default=False)
    tahapan_ori_lines   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id', string="Lines 1 ", index=True, tracking=True)
    tahapan_ori_lines1   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id1', string="Lines 2 ", index=True, tracking=True)
    tahapan_ori_lines2   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id2', string="Lines 3 ", index=True, tracking=True)
    tahapan_ori_lines3   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id3', string="Lines 4 ", index=True, tracking=True)
    tahapan_ori_lines4   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id4', string="Lines 5 ", index=True, tracking=True)
    tahapan_ori_lines5   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id5', string="Lines 6 ", index=True, tracking=True)
    tahapan_ori_lines6   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id6', string="Lines 7 ", index=True, tracking=True)
    tahapan_ori_lines_re   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id_re', string="Lines 8 ", index=True, tracking=True)
    tahapan_ori_lines_re2   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id_re2', string="Lines 9 ", index=True, tracking=True)
    tahapan_ori_lines_re3   = fields.One2many('tsi.iso.mandays_app', 'tahapan_id_re3', string="Lines 10 ", index=True, tracking=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        index=True,
        default=lambda self: self.env.company, tracking=True)
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Nama Klien",
        change_default=True, index=True,
        domain="[('is_company', '=', True)]",
        ondelete='cascade',
        readonly=False,
        tracking=True)
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        compute='_compute_pricelist_id',
        store=True, readonly=False, precompute=True, check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.", tracking=True)
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_currency_id',
        store=True,
        precompute=True,
        ondelete='restrict', tracking=True)
    amount_total = fields.Monetary(string="IA", store=True, compute='_compute_amounts', tracking=4)
    amount_total_s1 = fields.Monetary(string="SV1", store=True, compute='_compute_amounts_s1', tracking=4)
    amount_total_s2 = fields.Monetary(string="SV2", store=True, compute='_compute_amounts_s2', tracking=4)
    amount_total_s3 = fields.Monetary(string="SV3", store=True, compute='_compute_amounts_s3', tracking=4)
    amount_total_s4 = fields.Monetary(string="SV4", store=True, compute='_compute_amounts_s4', tracking=4)
    amount_total_s5 = fields.Monetary(string="SV5", store=True, compute='_compute_amounts_s5', tracking=4)
    amount_total_s6 = fields.Monetary(string="SV6", store=True, compute='_compute_amounts_s6', tracking=4)
    amount_total_re = fields.Monetary(string="RC1", store=True, compute='_compute_amounts_re', tracking=4)
    amount_total_re2 = fields.Monetary(string="RC2", store=True, compute='_compute_amounts_re2', tracking=4)
    amount_total_re3 = fields.Monetary(string="RC3", store=True, compute='_compute_amounts_re3', tracking=4)
    amount_untaxed = fields.Monetary(string="Untaxed Amount", store=True, compute='_compute_amounts', tracking=5)
    amount_tax = fields.Monetary(string="Taxes", store=True, compute='_compute_amounts')

    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True)

    ispo_reference       = fields.Many2one('tsi.ispo', string="Application Form", readonly=True)
    review_reference_ispo    = fields.Many2many('tsi.ispo.review', string="Review Reference", readonly=True)

    show_iso_fields = fields.Boolean(compute='_compute_show_fields', store=False)
    show_ispo_fields = fields.Boolean(compute='_compute_show_fields', store=False)

    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', related='iso_reference.doctype', readonly=True, index=True)

    state           =fields.Selection([
                            ('draft', 'Draft'),
                            ('approve', 'Approve'),
                            ('reject', 'Reject'),
                            ('lanjut', 'Lanjut'),
                            ('lost','Loss'),
                            ('suspend', 'Suspend'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')
    
    state_klien           =fields.Selection([
                            ('draft', 'Draft'),
                            ('approve', 'Approve'),
                            ('reject', 'Reject'),
                            ('New', 'New'),
                            ('active', 'Active'),
                            ('lanjut', 'Lanjut'),
                            ('lost','Loss'),
                            ('suspend', 'Suspend'),
                            ('Re-Active', 'Re-Active'),
                            ('Double', 'Double'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, related="partner_id.status_klien")

    tgl_perkiraan_selesai = fields.Date(string="Plan of audit date",store=True)
    tgl_perkiraan_audit_selesai = fields.Selection(
        selection=lambda self: self.get_end_of_month_choices(),
        string="Plan of audit date"
    )
                        
    # ISO 9001
    price_baru_9001      = fields.Float(string='Current Price ISO 9001')
    price_lama_9001      = fields.Float(string='Previous Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Current Price ISO 14001')
    price_lama_14001      = fields.Float(string='Previous Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Current Price ISO 22000')
    price_lama_22000      = fields.Float(string='Previous Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 22001
    price_baru_22001      = fields.Float(string='Current Price ISO 22001')
    price_lama_22001      = fields.Float(string='Previous Price ISO 22001')
    up_value_22001        = fields.Float(string='Up Value ISO 22001')
    loss_value_22001      = fields.Float(string='Loss Value ISO 22001')

    # ISO 22301
    price_baru_22301      = fields.Float(string='Current Price ISO 22301')
    price_lama_22301      = fields.Float(string='Previous Price ISO 22301')
    up_value_22301        = fields.Float(string='Up Value ISO 22301')
    loss_value_22301      = fields.Float(string='Loss Value ISO 22301')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Current Price ISO 27001')
    price_lama_27001      = fields.Float(string='Previous Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 27701
    price_baru_27701      = fields.Float(string='Current Price ISO 27701')
    price_lama_27701      = fields.Float(string='Previous Price ISO 27701')
    up_value_27701        = fields.Float(string='Up Value ISO 27701')
    loss_value_27701      = fields.Float(string='Loss Value ISO 27701')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Current Price ISO 45001')
    price_lama_45001      = fields.Float(string='Previous Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Current Price ISO 37001')
    price_lama_37001      = fields.Float(string='Previous Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 37301
    price_baru_37301      = fields.Float(string='Current Price ISO 37301')
    price_lama_37301      = fields.Float(string='Previous Price ISO 37301')
    up_value_37301        = fields.Float(string='Up Value ISO 37301')
    loss_value_37301      = fields.Float(string='Loss Value ISO 37301')

    # ISO 31000
    price_baru_31000      = fields.Float(string='Current Price ISO 31000')
    price_lama_31000      = fields.Float(string='Previous Price ISO 31000')
    up_value_31000        = fields.Float(string='Up Value ISO 31000')
    loss_value_31000      = fields.Float(string='Loss Value ISO 31000')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Current Price ISO 13485')
    price_lama_13485      = fields.Float(string='Previous Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Current Price ISO 9994')
    price_lama_9994      = fields.Float(string='Previous Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Current Price ISPO')
    price_lama_ispo      = fields.Float(string='Previous Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')

    # HACCP
    price_baru_haccp      = fields.Float(string='Current Price HACCP')
    price_lama_haccp      = fields.Float(string='Previous Price HACCP')
    up_value_haccp        = fields.Float(string='Up Value HACCP')
    loss_value_haccp      = fields.Float(string='Loss Value HACCP')

    # GMP
    price_baru_gmp      = fields.Float(string='Current Price GMP')
    price_lama_gmp      = fields.Float(string='Previous Price GMP')
    up_value_gmp        = fields.Float(string='Up Value GMP')
    loss_value_gmp      = fields.Float(string='Loss Value GMP')

    # SMK3
    price_baru_smk3      = fields.Float(string='Current Price SMK3')
    price_lama_smk3      = fields.Float(string='Previous Price SMK3')
    up_value_smk3        = fields.Float(string='Up Value SMK3')
    loss_value_smk3      = fields.Float(string='Loss Value SMK3')

    # crm_accreditation       = fields.One2many('tsi.crm_accreditation', 'reference_id', string="Accreditation Lines", index=True, tracking=True)

    # @api.model
    # def create_new_crm(self):
    #     records = self.search([])
    #     current_time = datetime.now().date()
        
    #     for record in records:
    #         if record.tanggal_kontrak:
    #             tanggal_kontrak_dt = record.tanggal_kontrak
                
    #             if tanggal_kontrak_dt + timedelta(days=1) <= current_time <= tanggal_kontrak_dt + timedelta(weeks=26):
    #                 record.state = 'suspend'
    #                 record.action_suspend()
                
    #             elif current_time > tanggal_kontrak_dt + timedelta(weeks=26):
    #                 record.state = 'lost'
    #                 record.action_loss()

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
                obj.show_22301 = False
                obj.show_31000 = False
                obj.show_37001 = False
                obj.show_13485 = False
                obj.show_smk = False
                obj.show_21000 = False  
                obj.show_37301 = False
                obj.show_9994 = False
                obj.show_21001 = False
                obj.show_31001 = False
                obj.show_ispo = False               
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
                    if standard.name == 'ISPO' :
                        if obj.show_ispo != True :
                            obj.show_ispo = False
                        obj.show_ispo = True
                    elif standard.name == 'ISO 9001:2015' :
                        obj.show_9001 = True

    @api.depends('iso_standard_ids')
    def _compute_show_fields(self):
        iso_standards = self.iso_standard_ids.mapped('standard')

        self.show_iso_fields = any(
            standard in iso_standards for standard in [
                'iso',
            ]
        )
        self.show_ispo_fields = 'ispo' in iso_standards

    def generate_sales_order(self):
        self.env['sale.order'].create({
            'partner_id'        : self.partner_id.id,
            'iso_reference'     : self.iso_reference.id,
            'doctype'           : self.doctype
        })
        return True

    def set_to_revice(self):
        self.write({'state': 'lanjut'})
        audit_records = self.env['tsi.audit.request'].search([('partner_id', '=', self.partner_id.id)])
        audit_records.write({'state': 'revice'})         
        return True

    # def action_approve(self):
    #     self.write({'state': 'approve'})          
    #     return True
    
    # def action_reject(self):
    #     self.write({'state': 'reject'})          
    #     return True

    #action Loss
    def action_loss(self, alasan=None):
        for history in self:
            history.write({'alasan': alasan})
            # Cari atau buat catatan tsi.crm.loss berdasarkan partner_id
            loss_record = self.env['tsi.crm.loss'].search([('partner_id', '=', history.partner_id.id)], limit=1)
            if not loss_record:
                data = {
                    'partner_id': history.partner_id.id,
                    'contract_number': history.no_kontrak,
                    'contract_date': history.tanggal_kontrak,
                    'sales': history.sales.id,
                    'segment': [(6, 0, history.segment.ids)],
                    'iso_standard_ids': [(6, 0, history.iso_standard_ids.ids)] if history.iso_standard_ids else False,
                    'alasan': alasan,
                    'nilai_kontrak': history.nilai_kontrak,
                }

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 9001:2015'):
                    data.update({
                        'price_baru_9001': history.price_baru_9001,
                        'price_lama_9001': history.price_lama_9001,
                        'up_value_9001': history.up_value_9001,
                        'loss_value_9001': history.loss_value_9001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 14001:2015'):
                    data.update({
                        'price_baru_14001': history.price_baru_14001,
                        'price_lama_14001': history.price_lama_14001,
                        'up_value_14001': history.up_value_14001,
                        'loss_value_14001': history.loss_value_14001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22000:2018'):
                    data.update({
                        'price_baru_22000': history.price_baru_22000,
                        'price_lama_22000': history.price_lama_22000,
                        'up_value_22000': history.up_value_22000,
                        'loss_value_22000': history.loss_value_22000,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22001:2018'):
                    data.update({
                        'price_baru_22001': history.price_baru_22001,
                        'price_lama_22001': history.price_lama_22001,
                        'up_value_22001': history.up_value_22001,
                        'loss_value_22001': history.loss_value_22001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22301:2019'):
                    data.update({
                        'price_baru_22301': history.price_baru_22301,
                        'price_lama_22301': history.price_lama_22301,
                        'up_value_22301': history.up_value_22301,
                        'loss_value_22301': history.loss_value_22301,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO/IEC 27001:2022'):
                    data.update({
                        'price_baru_27001': history.price_baru_27001,
                        'price_lama_27001': history.price_lama_27001,
                        'up_value_27001': history.up_value_27001,
                        'loss_value_27001': history.loss_value_27001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 27701:2019'):
                    data.update({
                        'price_baru_27701': history.price_baru_27701,
                        'price_lama_27701': history.price_lama_27701,
                        'up_value_27701': history.up_value_27701,
                        'loss_value_27701': history.loss_value_27701,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 45001:2018'):
                    data.update({
                        'price_baru_45001': history.price_baru_45001,
                        'price_lama_45001': history.price_lama_45001,
                        'up_value_45001': history.up_value_45001,
                        'loss_value_45001': history.loss_value_45001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 37001:2016'):
                    data.update({
                        'price_baru_37001': history.price_baru_37001,
                        'price_lama_37001': history.price_lama_37001,
                        'up_value_37001': history.up_value_37001,
                        'loss_value_37001': history.loss_value_37001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 37301:2021'):
                    data.update({
                        'price_baru_37301': history.price_baru_37301,
                        'price_lama_37301': history.price_lama_37301,
                        'up_value_37301': history.up_value_37301,
                        'loss_value_37301': history.loss_value_37301,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 31000:2018'):
                    data.update({
                        'price_baru_31000': history.price_baru_31000,
                        'price_lama_31000': history.price_lama_31000,
                        'up_value_31000': history.up_value_31000,
                        'loss_value_31000': history.loss_value_31000,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 13485:2016'):
                    data.update({
                        'price_baru_13485': history.price_baru_13485,
                        'price_lama_13485': history.price_lama_13485,
                        'up_value_13485': history.up_value_13485,
                        'loss_value_13485': history.loss_value_13485,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 9994:2018'):
                    data.update({
                        'price_baru_9994': history.price_baru_9994,
                        'price_lama_9994': history.price_lama_9994,
                        'up_value_9994': history.up_value_9994,
                        'loss_value_9994': history.loss_value_9994,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISPO'):
                    data.update({
                        'price_baru_ispo': history.price_baru_ispo,
                        'price_lama_ispo': history.price_lama_ispo,
                        'up_value_ispo': history.up_value_ispo,
                        'loss_value_ispo': history.loss_value_ispo,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'HACCP'):
                    data.update({
                        'price_baru_haccp': history.price_baru_haccp,
                        'price_lama_haccp': history.price_lama_haccp,
                        'up_value_haccp': history.up_value_haccp,
                        'loss_value_haccp': history.loss_value_haccp,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'GMP'):
                    data.update({
                        'price_baru_gmp': history.price_baru_gmp,
                        'price_lama_gmp': history.price_lama_gmp,
                        'up_value_gmp': history.up_value_gmp,
                        'loss_value_gmp': history.loss_value_gmp,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'SMK3'):
                    data.update({
                        'price_baru_smk3': history.price_baru_smk3,
                        'price_lama_smk3': history.price_lama_smk3,
                        'up_value_smk3': history.up_value_smk3,
                        'loss_value_smk3': history.loss_value_smk3,
                    })

                loss_record = self.env['tsi.crm.loss'].create(data)

            # Clear existing crm_accreditation lines
            loss_record.crm_accreditations.unlink()

            # Update tahapan_audit based on the lines
            lines = []
            if history.show_initial and history.tahapan_ori_lines:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines, 'Initial Audit')
            if history.show_survilance1 and history.tahapan_ori_lines1:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines1, 'Surveillance 1')
            if history.show_survilance2 and history.tahapan_ori_lines2:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines2, 'Surveillance 2')
            if history.show_survilance3 and history.tahapan_ori_lines3:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines3, 'Surveillance 3')
            if history.show_survilance4 and history.tahapan_ori_lines4:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines4, 'Surveillance 4')
            if history.show_recertification and history.tahapan_ori_lines_re:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines_re, 'Recertification')

            total_nilai_ia = sum(line['nilai_ia'] for line in lines if line.get('nilai_ia'))

            # Update tahapan_audit with the correct value
            loss_record.write({
                'crm_accreditations': [(0, 0, line) for line in lines],
                'nilai_kontrak': total_nilai_ia,
            })

            # Set state to 'lost' on history kontrak
            history.write({
                'state': 'lost',
                'nilai_kontrak': total_nilai_ia,
            })

    def _prepare_loss_lines(self, tahapan_lines, tahapan_name):
        lines = []
        if tahapan_lines:
            for line in tahapan_lines:
                line_values = {
                    'accreditation': line.accreditation.id if line.accreditation else False,
                    'tahapan_audit': tahapan_name,
                    'iso_standard_ids': [(6, 0, line.standard.ids)] if line.standard else False,
                    'nilai_ia': False,  # Default value
                }
                # Set nilai_ia based on tahapan_name
                if tahapan_name == 'Initial Audit':
                    line_values['nilai_ia'] = line.mandays
                elif tahapan_name == 'Surveillance 1':
                    line_values['nilai_ia'] = line.mandays_s1
                elif tahapan_name == 'Surveillance 2':
                    line_values['nilai_ia'] = line.mandays_s2
                elif tahapan_name == 'Surveillance 3':
                    line_values['nilai_ia'] = line.mandays_s3
                elif tahapan_name == 'Surveillance 4':
                    line_values['nilai_ia'] = line.mandays_s4
                elif tahapan_name == 'Recertification':
                    line_values['nilai_ia'] = line.mandays_rs

                lines.append(line_values)
        return lines
    
    #Action Suspen
    def action_suspend(self, alasan=None):
        for history in self:
            history.write({'alasan': alasan})
            # Cari atau buat catatan tsi.crm.loss berdasarkan partner_id
            loss_record = self.env['tsi.crm.suspen'].search([('partner_id', '=', history.partner_id.id)], limit=1)
            if not loss_record:
                data = {
                    'partner_id': history.partner_id.id,
                    'contract_number': history.no_kontrak,
                    'contract_date': history.tanggal_kontrak,
                    'sales': history.sales.id,
                    'segment': [(6, 0, history.segment.ids)],
                    'iso_standard_ids': [(6, 0, history.iso_standard_ids.ids)] if history.iso_standard_ids else False,
                    'alasan': alasan,
                    'nilai_kontrak': history.nilai_kontrak,
                }

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 9001:2015'):
                    data.update({
                        'price_baru_9001': history.price_baru_9001,
                        'price_lama_9001': history.price_lama_9001,
                        'up_value_9001': history.up_value_9001,
                        'loss_value_9001': history.loss_value_9001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 14001:2015'):
                    data.update({
                        'price_baru_14001': history.price_baru_14001,
                        'price_lama_14001': history.price_lama_14001,
                        'up_value_14001': history.up_value_14001,
                        'loss_value_14001': history.loss_value_14001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22000:2018'):
                    data.update({
                        'price_baru_22000': history.price_baru_22000,
                        'price_lama_22000': history.price_lama_22000,
                        'up_value_22000': history.up_value_22000,
                        'loss_value_22000': history.loss_value_22000,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22001:2018'):
                    data.update({
                        'price_baru_22001': history.price_baru_22001,
                        'price_lama_22001': history.price_lama_22001,
                        'up_value_22001': history.up_value_22001,
                        'loss_value_22001': history.loss_value_22001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22301:2019'):
                    data.update({
                        'price_baru_22301': history.price_baru_22301,
                        'price_lama_22301': history.price_lama_22301,
                        'up_value_22301': history.up_value_22301,
                        'loss_value_22301': history.loss_value_22301,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO/IEC 27001:2022'):
                    data.update({
                        'price_baru_27001': history.price_baru_27001,
                        'price_lama_27001': history.price_lama_27001,
                        'up_value_27001': history.up_value_27001,
                        'loss_value_27001': history.loss_value_27001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 27701:2019'):
                    data.update({
                        'price_baru_27701': history.price_baru_27701,
                        'price_lama_27701': history.price_lama_27701,
                        'up_value_27701': history.up_value_27701,
                        'loss_value_27701': history.loss_value_27701,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 45001:2018'):
                    data.update({
                        'price_baru_45001': history.price_baru_45001,
                        'price_lama_45001': history.price_lama_45001,
                        'up_value_45001': history.up_value_45001,
                        'loss_value_45001': history.loss_value_45001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 37001:2016'):
                    data.update({
                        'price_baru_37001': history.price_baru_37001,
                        'price_lama_37001': history.price_lama_37001,
                        'up_value_37001': history.up_value_37001,
                        'loss_value_37001': history.loss_value_37001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 37301:2021'):
                    data.update({
                        'price_baru_37301': history.price_baru_37301,
                        'price_lama_37301': history.price_lama_37301,
                        'up_value_37301': history.up_value_37301,
                        'loss_value_37301': history.loss_value_37301,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 31000:2018'):
                    data.update({
                        'price_baru_31000': history.price_baru_31000,
                        'price_lama_31000': history.price_lama_31000,
                        'up_value_31000': history.up_value_31000,
                        'loss_value_31000': history.loss_value_31000,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 13485:2016'):
                    data.update({
                        'price_baru_13485': history.price_baru_13485,
                        'price_lama_13485': history.price_lama_13485,
                        'up_value_13485': history.up_value_13485,
                        'loss_value_13485': history.loss_value_13485,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 9994:2018'):
                    data.update({
                        'price_baru_9994': history.price_baru_9994,
                        'price_lama_9994': history.price_lama_9994,
                        'up_value_9994': history.up_value_9994,
                        'loss_value_9994': history.loss_value_9994,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISPO'):
                    data.update({
                        'price_baru_ispo': history.price_baru_ispo,
                        'price_lama_ispo': history.price_lama_ispo,
                        'up_value_ispo': history.up_value_ispo,
                        'loss_value_ispo': history.loss_value_ispo,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'HACCP'):
                    data.update({
                        'price_baru_haccp': history.price_baru_haccp,
                        'price_lama_haccp': history.price_lama_haccp,
                        'up_value_haccp': history.up_value_haccp,
                        'loss_value_haccp': history.loss_value_haccp,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'GMP'):
                    data.update({
                        'price_baru_gmp': history.price_baru_gmp,
                        'price_lama_gmp': history.price_lama_gmp,
                        'up_value_gmp': history.up_value_gmp,
                        'loss_value_gmp': history.loss_value_gmp,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'SMK3'):
                    data.update({
                        'price_baru_smk3': history.price_baru_smk3,
                        'price_lama_smk3': history.price_lama_smk3,
                        'up_value_smk3': history.up_value_smk3,
                        'loss_value_smk3': history.loss_value_smk3,
                    })

                loss_record = self.env['tsi.crm.suspen'].create(data)

            # Clear existing crm_accreditation lines
            loss_record.crm_accreditations.unlink()

            # Update tahapan_audit based on the lines
            lines = []
            if history.show_initial and history.tahapan_ori_lines:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines, 'Initial Audit')
            if history.show_survilance1 and history.tahapan_ori_lines1:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines1, 'Surveillance 1')
            if history.show_survilance2 and history.tahapan_ori_lines2:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines2, 'Surveillance 2')
            if history.show_survilance3 and history.tahapan_ori_lines3:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines3, 'Surveillance 3')
            if history.show_survilance4 and history.tahapan_ori_lines4:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines4, 'Surveillance 4')
            if history.show_recertification and history.tahapan_ori_lines_re:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines_re, 'Recertification')

            total_nilai_ia = sum(line['nilai_ia'] for line in lines if line.get('nilai_ia'))

            # Update nilai_kontrak di crm.loss
            loss_record.write({
                'crm_accreditations': [(0, 0, line) for line in lines],
                'nilai_kontrak': total_nilai_ia,
            })

            # Update nilai_kontrak di history
            history.write({
                'state': 'suspend',
                'nilai_kontrak': total_nilai_ia,
            })

    def _prepare_loss_lines(self, tahapan_lines, tahapan_name):
        lines = []
        if tahapan_lines:
            for line in tahapan_lines:
                line_values = {
                    'accreditation': line.accreditation.id if line.accreditation else False,
                    'tahapan_audit': tahapan_name,
                    'iso_standard_ids': [(6, 0, line.standard.ids)] if line.standard else False,
                    'nilai_ia': False,  # Default value
                }
                # Set nilai_ia based on tahapan_name
                if tahapan_name == 'Initial Audit':
                    line_values['nilai_ia'] = line.mandays
                elif tahapan_name == 'Surveillance 1':
                    line_values['nilai_ia'] = line.mandays_s1
                elif tahapan_name == 'Surveillance 2':
                    line_values['nilai_ia'] = line.mandays_s2
                elif tahapan_name == 'Surveillance 3':
                    line_values['nilai_ia'] = line.mandays_s3
                elif tahapan_name == 'Surveillance 4':
                    line_values['nilai_ia'] = line.mandays_s4
                elif tahapan_name == 'Recertification':
                    line_values['nilai_ia'] = line.mandays_rs

                lines.append(line_values)
        return lines
    
    #Action Lanjut
    def action_go_to_tsi_crm(self):
        for history in self:
            # Cari atau buat catatan tsi.crm.loss berdasarkan partner_id
            loss_record = self.env['tsi.crm.lanjut'].search([('partner_id', '=', history.partner_id.id)], limit=1)
            if not loss_record:
                data = {
                    'partner_id': history.partner_id.id,
                    'contract_number': history.no_kontrak,
                    'contract_date': history.tanggal_kontrak,
                    'sales': history.sales.id,
                    'segment': [(6, 0, history.segment.ids)],
                    'iso_standard_ids': [(6, 0, history.iso_standard_ids.ids)] if history.iso_standard_ids else False,
                    'nilai_kontrak': history.nilai_kontrak,
                }

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 9001:2015'):
                    data.update({
                        'price_baru_9001': history.price_baru_9001,
                        'price_lama_9001': history.price_lama_9001,
                        'up_value_9001': history.up_value_9001,
                        'loss_value_9001': history.loss_value_9001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 14001:2015'):
                    data.update({
                        'price_baru_14001': history.price_baru_14001,
                        'price_lama_14001': history.price_lama_14001,
                        'up_value_14001': history.up_value_14001,
                        'loss_value_14001': history.loss_value_14001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22000:2018'):
                    data.update({
                        'price_baru_22000': history.price_baru_22000,
                        'price_lama_22000': history.price_lama_22000,
                        'up_value_22000': history.up_value_22000,
                        'loss_value_22000': history.loss_value_22000,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22001:2018'):
                    data.update({
                        'price_baru_22001': history.price_baru_22001,
                        'price_lama_22001': history.price_lama_22001,
                        'up_value_22001': history.up_value_22001,
                        'loss_value_22001': history.loss_value_22001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 22301:2019'):
                    data.update({
                        'price_baru_22301': history.price_baru_22301,
                        'price_lama_22301': history.price_lama_22301,
                        'up_value_22301': history.up_value_22301,
                        'loss_value_22301': history.loss_value_22301,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO/IEC 27001:2022'):
                    data.update({
                        'price_baru_27001': history.price_baru_27001,
                        'price_lama_27001': history.price_lama_27001,
                        'up_value_27001': history.up_value_27001,
                        'loss_value_27001': history.loss_value_27001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 27701:2019'):
                    data.update({
                        'price_baru_27701': history.price_baru_27701,
                        'price_lama_27701': history.price_lama_27701,
                        'up_value_27701': history.up_value_27701,
                        'loss_value_27701': history.loss_value_27701,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 45001:2018'):
                    data.update({
                        'price_baru_45001': history.price_baru_45001,
                        'price_lama_45001': history.price_lama_45001,
                        'up_value_45001': history.up_value_45001,
                        'loss_value_45001': history.loss_value_45001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 37001:2016'):
                    data.update({
                        'price_baru_37001': history.price_baru_37001,
                        'price_lama_37001': history.price_lama_37001,
                        'up_value_37001': history.up_value_37001,
                        'loss_value_37001': history.loss_value_37001,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 37301:2021'):
                    data.update({
                        'price_baru_37301': history.price_baru_37301,
                        'price_lama_37301': history.price_lama_37301,
                        'up_value_37301': history.up_value_37301,
                        'loss_value_37301': history.loss_value_37301,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 31000:2018'):
                    data.update({
                        'price_baru_31000': history.price_baru_31000,
                        'price_lama_31000': history.price_lama_31000,
                        'up_value_31000': history.up_value_31000,
                        'loss_value_31000': history.loss_value_31000,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 13485:2016'):
                    data.update({
                        'price_baru_13485': history.price_baru_13485,
                        'price_lama_13485': history.price_lama_13485,
                        'up_value_13485': history.up_value_13485,
                        'loss_value_13485': history.loss_value_13485,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISO 9994:2018'):
                    data.update({
                        'price_baru_9994': history.price_baru_9994,
                        'price_lama_9994': history.price_lama_9994,
                        'up_value_9994': history.up_value_9994,
                        'loss_value_9994': history.loss_value_9994,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'ISPO'):
                    data.update({
                        'price_baru_ispo': history.price_baru_ispo,
                        'price_lama_ispo': history.price_lama_ispo,
                        'up_value_ispo': history.up_value_ispo,
                        'loss_value_ispo': history.loss_value_ispo,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'HACCP'):
                    data.update({
                        'price_baru_haccp': history.price_baru_haccp,
                        'price_lama_haccp': history.price_lama_haccp,
                        'up_value_haccp': history.up_value_haccp,
                        'loss_value_haccp': history.loss_value_haccp,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'GMP'):
                    data.update({
                        'price_baru_gmp': history.price_baru_gmp,
                        'price_lama_gmp': history.price_lama_gmp,
                        'up_value_gmp': history.up_value_gmp,
                        'loss_value_gmp': history.loss_value_gmp,
                    })

                if history.iso_standard_ids.filtered(lambda iso: iso.name == 'SMK3'):
                    data.update({
                        'price_baru_smk3': history.price_baru_smk3,
                        'price_lama_smk3': history.price_lama_smk3,
                        'up_value_smk3': history.up_value_smk3,
                        'loss_value_smk3': history.loss_value_smk3,
                    })

                loss_record = self.env['tsi.crm.lanjut'].create(data)

            # Clear existing crm_accreditation lines
            loss_record.crm_accreditations.unlink()

            # Update tahapan_audit based on the lines
            lines = []
            if history.show_initial and history.tahapan_ori_lines:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines, 'Initial Audit')
            if history.show_survilance1 and history.tahapan_ori_lines1:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines1, 'Surveillance 1')
            if history.show_survilance2 and history.tahapan_ori_lines2:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines2, 'Surveillance 2')
            if history.show_survilance3 and history.tahapan_ori_lines3:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines3, 'Surveillance 3')
            if history.show_survilance4 and history.tahapan_ori_lines4:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines4, 'Surveillance 4')
            if history.show_recertification and history.tahapan_ori_lines_re:
                lines += self._prepare_loss_lines(history.tahapan_ori_lines_re, 'Recertification')

            # total_nilai_ia = sum(line['nilai_ia'] for line in lines if line.get('nilai_ia'))

            # Update nilai_kontrak di crm.loss
            loss_record.write({
                'crm_accreditations': [(0, 0, line) for line in lines],
                # 'nilai_kontrak': total_nilai_ia,
            })

            # Update nilai_kontrak di history
            history.write({
                'state': 'lanjut',
                # 'nilai_kontrak': total_nilai_ia,
            })

    def _prepare_loss_lines(self, tahapan_lines, tahapan_name):
        lines = []
        if tahapan_lines:
            for line in tahapan_lines:
                line_values = {
                    'accreditation': line.accreditation.id if line.accreditation else False,
                    'tahapan_audit': tahapan_name,
                    'iso_standard_ids': [(6, 0, line.standard.ids)] if line.standard else False,
                    'nilai_ia': False,  # Default value
                }
                # Set nilai_ia based on tahapan_name
                if tahapan_name == 'Initial Audit':
                    line_values['nilai_ia'] = line.mandays
                elif tahapan_name == 'Surveillance 1':
                    line_values['nilai_ia'] = line.mandays_s1
                elif tahapan_name == 'Surveillance 2':
                    line_values['nilai_ia'] = line.mandays_s2
                elif tahapan_name == 'Surveillance 3':
                    line_values['nilai_ia'] = line.mandays_s3
                elif tahapan_name == 'Surveillance 4':
                    line_values['nilai_ia'] = line.mandays_s4
                elif tahapan_name == 'Recertification':
                    line_values['nilai_ia'] = line.mandays_rs

                lines.append(line_values)
        return lines

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

    def create_audit(self):
        nama_client = self.partner_id.id
        iso_standard_ids = self.iso_standard_ids
        iso_reference = self.iso_reference
        ispo_reference = self.ispo_reference
        sales_reference = self.sales_reference
        review_reference = self.review_reference
        review_reference_ispo = self.review_reference_ispo
        no_kontrak = self.no_kontrak
        closing_by = self.closing_by
        category = self.category
        pic_direct = self.pic_direct
        email_direct = self.email_direct
        phone_direct = self.phone_direct
        pic_konsultan1 = self.pic_konsultan1.id
        email_konsultan = self.email_konsultan
        phone_konsultan = self.phone_konsultan
        transport_by    = self.transport_by
        hotel_by    =   self.hotel_by
        tipe_klien_transport    =   self.tipe_klien_transport
        tipe_klien_hotel = self.tipe_klien_hotel
        pic_crm = self.pic_crm
        crm_reference   = self.id

        # Ambil EA Code dan Akreditasi
        ea_code_9001 = [(6, 0, self.ea_code_9001.ids)] if self.ea_code_9001 else False
        accreditation_9001 = self.accreditation_9001.id if self.accreditation_9001 else False

        ea_code_14001 = [(6, 0, self.ea_code_14001.ids)] if self.ea_code_14001 else False
        accreditation_14001 = self.accreditation_14001.id if self.accreditation_14001 else False
        
        ea_code_45001 = [(6, 0, self.ea_code_45001.ids)] if self.ea_code_45001 else False
        accreditation_45001 = self.accreditation_45001.id if self.accreditation_45001 else False

        ea_code_37001 = [(6, 0, self.ea_code_37001.ids)] if self.ea_code_37001 else False
        accreditation_37001 = self.accreditation_37001.id if self.accreditation_37001 else False

        ea_code_13485 = [(6, 0, self.ea_code_13485.ids)] if self.ea_code_13485 else False
        accreditation_13485 = self.accreditation_13485.id if self.accreditation_13485 else False

        ea_code_22000 = [(6, 0, self.ea_code_22000.ids)] if self.ea_code_22000 else False
        accreditation_22000 = self.accreditation_22000.id if self.accreditation_22000 else False

        ea_code_27001 = [(6, 0, self.ea_code_27001.ids)] if self.ea_code_27001 else False
        accreditation_27001 = self.accreditation_27001.id if self.accreditation_27001 else False

        ea_code_27001_2022 = [(6, 0, self.ea_code_27001_2022.ids)] if self.ea_code_27001_2022 else False
        accreditation_27001_2022 = self.accreditation_27001_2022.id if self.accreditation_27001_2022 else False

        ea_code_27701 = [(6, 0, self.ea_code_27701.ids)] if self.ea_code_27701 else False
        accreditation_27701 = self.accreditation_27701.id if self.accreditation_27701 else False

        ea_code_27017 = [(6, 0, self.ea_code_27017.ids)] if self.ea_code_27017 else False
        accreditation_27017 = self.accreditation_27017.id if self.accreditation_27017 else False

        ea_code_27018 = [(6, 0, self.ea_code_27018.ids)] if self.ea_code_27018 else False
        accreditation_27018 = self.accreditation_27018.id if self.accreditation_27018 else False

        ea_code_31000 = [(6, 0, self.ea_code_31000.ids)] if self.ea_code_31000 else False
        accreditation_31000 = self.accreditation_31000.id if self.accreditation_31000 else False

        ea_code_22301 = [(6, 0, self.ea_code_22301.ids)] if self.ea_code_22301 else False
        accreditation_22301 = self.accreditation_22301.id if self.accreditation_22301 else False

        ea_code_9994 = [(6, 0, self.ea_code_9994.ids)] if self.ea_code_9994 else False
        accreditation_9994 = self.accreditation_9994.id if self.accreditation_9994 else False

        ea_code_37301 = [(6, 0, self.ea_code_37301.ids)] if self.ea_code_37301 else False
        accreditation_37301 = self.accreditation_37301.id if self.accreditation_37301 else False

        ea_code_31001 = [(6, 0, self.ea_code_31001.ids)] if self.ea_code_31001 else False
        accreditation_31001 = self.accreditation_31001.id if self.accreditation_31001 else False

        ea_code_21001 = [(6, 0, self.ea_code_21001.ids)] if self.ea_code_21001 else False
        accreditation_21001 = self.accreditation_21001.id if self.accreditation_21001 else False

        ea_code_21000 = [(6, 0, self.ea_code_21000.ids)] if self.ea_code_21000 else False
        accreditation_21000 = self.accreditation_21000.id if self.accreditation_21000 else False

        ea_code_haccp = [(6, 0, self.ea_code_haccp.ids)] if self.ea_code_haccp else False
        accreditation_haccp = self.accreditation_haccp.id if self.accreditation_haccp else False

        ea_code_gmp = [(6, 0, self.ea_code_gmp.ids)] if self.ea_code_gmp else False
        accreditation_gmp = self.accreditation_gmp.id if self.accreditation_gmp else False

        ea_code_smk = [(6, 0, self.ea_code_smk.ids)] if self.ea_code_smk else False
        accreditation_smk = self.accreditation_smk.id if self.accreditation_smk else False

        ea_code_ispo = [(6, 0, self.ea_code_ispo.ids)] if self.ea_code_ispo else False
        accreditation_ispo = self.accreditation_ispo.id if self.accreditation_ispo else False

        sales = self.sales.id if self.sales else False
        scope = self.scope or ""
        boundaries = self.boundaries or ""

        line_items = []
        cycle  = ''
        # cycle1 = ''
        # cycle2 = ''
        # cycle3 = ''

        if self.tahapan_ori_lines1:
            cycle  = 'cycle1'
            # cycle1 = 'surveilance1'
            for tahapan_ori_line in self.tahapan_ori_lines1:
                standard_name = tahapan_ori_line.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s1_value = tahapan_ori_line.mandays_s1

                try:
                    mandays_s1_float = float(mandays_s1_value)
                except (ValueError, TypeError) as e:
                    mandays_s1_float = 0.0 
                
                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s1_float,
                    'audit_tahapan': 'Surveillance 1',
                }))

        if self.tahapan_ori_lines2:
            cycle  = 'cycle1'
            # cycle1 = 'surveilance2'
            for tahapan_ori_line2 in self.tahapan_ori_lines2:
                standard_name = tahapan_ori_line2.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s2_value = tahapan_ori_line2.mandays_s2

                try:
                    mandays_s2_float = float(mandays_s2_value)
                except (ValueError, TypeError) as e:
                    mandays_s2_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s2_float,
                    'audit_tahapan': 'Surveillance 2',
                }))

        if self.tahapan_ori_lines3:
            cycle  = 'cycle2'
            # cycle2 = 'surveilance3'
            for tahapan_ori_line3 in self.tahapan_ori_lines3:
                standard_name = tahapan_ori_line3.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s3_value = tahapan_ori_line3.mandays_s3

                try:
                    mandays_s3_float = float(mandays_s3_value)
                except (ValueError, TypeError) as e:
                    mandays_s3_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s3_float,
                    'audit_tahapan': 'Surveillance 3',
                }))

        if self.tahapan_ori_lines4:
            cycle  = 'cycle2'
            # cycle2 = 'surveilance4'
            for tahapan_ori_line4 in self.tahapan_ori_lines4:
                standard_name = tahapan_ori_line4.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s4_value = tahapan_ori_line4.mandays_s4

                try:
                    mandays_s4_float = float(mandays_s4_value)
                except (ValueError, TypeError) as e:
                    mandays_s4_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s4_float,
                    'audit_tahapan': 'Surveillance 4',
                }))

        if self.tahapan_ori_lines_re:
            cycle  = 'cycle1'
            # cycle1 = 'recertification1'
            for tahapan_ori_line_re in self.tahapan_ori_lines_re:
                standard_name = tahapan_ori_line_re.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_re_value = tahapan_ori_line_re.mandays_rs

                try:
                    mandays_re_float = float(mandays_re_value)
                except (ValueError, TypeError) as e:
                    mandays_re_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_re_float,
                    'audit_tahapan': 'Recertification',
                }))

        if self.tahapan_ori_lines5:
            cycle  = 'cycle3'
            # cycle3 = 'surveilance5'
            for tahapan_ori_line5 in self.tahapan_ori_lines5:
                standard_name = tahapan_ori_line5.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s5_value = tahapan_ori_line5.mandays_s5

                try:
                    mandays_s5_float = float(mandays_s5_value)
                except (ValueError, TypeError) as e:
                    mandays_s5_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s5_float,
                    'audit_tahapan': 'Surveillance 5',
                }))

        if self.tahapan_ori_lines6:
            cycle  = 'cycle3'
            # cycle3 = 'surveilance6'
            for tahapan_ori_line6 in self.tahapan_ori_lines6:
                standard_name = tahapan_ori_line6.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_s6_value = tahapan_ori_line6.mandays_s6

                try:
                    mandays_s6_float = float(mandays_s6_value)
                except (ValueError, TypeError) as e:
                    mandays_s6_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_s6_float,
                    'audit_tahapan': 'Surveillance 6',
                }))

        if self.tahapan_ori_lines_re2:
            cycle  = 'cycle2'
            # cycle2 = 'recertification2'
            for tahapan_ori_line_re2 in self.tahapan_ori_lines_re2:
                standard_name = tahapan_ori_line_re2.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_re2_value = tahapan_ori_line_re2.mandays_rs2

                try:
                    mandays_re2_float = float(mandays_re2_value)
                except (ValueError, TypeError) as e:
                    mandays_re2_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_re2_float,
                    'audit_tahapan': 'Recertification 2',
                }))

        if self.tahapan_ori_lines_re3:
            cycle  = 'cycle3'
            # cycle3 = 'recertification3'
            for tahapan_ori_line_re3 in self.tahapan_ori_lines_re3:
                standard_name = tahapan_ori_line_re3.standard.name
                product = self.env['product.product'].search([('name', '=', standard_name)], limit=1)
                mandays_re3_value = tahapan_ori_line_re3.mandays_rs3

                try:
                    mandays_re3_float = float(mandays_re3_value)
                except (ValueError, TypeError) as e:
                    mandays_re3_float = 0.0 

                line_items.append((0, 0, {
                    'product_id': product.id if product else False,
                    'price_lama': mandays_re3_float,
                    'audit_tahapan': 'Recertification 3',
                }))

        # site_lines = []
        # site_partners = self.env['tsi.site_partner'].search([('partner_id', '=', nama_client)])
        # for site in site_partners:
        #     site_lines.append((0, 0, {
        #         'tipe_site': site.jenis,
        #         'address': site.alamat,
        #         'effective_emp': site.effective_emp,
        #         'total_emp': site.jumlah_karyawan,
        #     }))
        # ISO 9001
        site_lines = []
        for site in self.site_ids:
            site_lines.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 14001
        site_lines_14001 = []
        for site in self.site_ids_14001:
            site_lines_14001.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 45001
        site_lines_45001 = []
        for site in self.site_ids_45001:
            site_lines_45001.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 27001
        site_lines_27001 = []
        for site in self.site_ids_27001:
            site_lines_27001.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 27701
        site_lines_27701 = []
        for site in self.site_ids_27701:
            site_lines_27701.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 27017
        site_lines_27017 = []
        for site in self.site_ids_27017:
            site_lines_27017.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 27018
        site_lines_27018 = []
        for site in self.site_ids_27018:
            site_lines_27018.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 27001_2022
        site_lines_27001_2022 = []
        for site in self.site_ids_27001_2022:
            site_lines_27001_2022.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # HACCP
        site_lines_haccp = []
        for site in self.site_ids_haccp:
            site_lines_haccp.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # GMP
        site_lines_gmp = []
        for site in self.site_ids_gmp:
            site_lines_gmp.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 22000
        site_lines_22000 = []
        for site in self.site_ids_22000:
            site_lines_22000.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 22301
        site_lines_22301 = []
        for site in self.site_ids_22301:
            site_lines_22301.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 31000
        site_lines_31000 = []
        for site in self.site_ids_31000:
            site_lines_31000.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 9994
        site_lines_9994 = []
        for site in self.site_ids_9994:
            site_lines_9994.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 37001
        site_lines_37001 = []
        for site in self.site_ids_37001:
            site_lines_37001.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 13485
        site_lines_13485 = []
        for site in self.site_ids_13485:
            site_lines_13485.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # SMK
        site_lines_smk = []
        for site in self.site_ids_smk:
            site_lines_smk.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 21000
        site_lines_21000 = []
        for site in self.site_ids_21000:
            site_lines_21000.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 37301
        site_lines_37301 = []
        for site in self.site_ids_37301:
            site_lines_37301.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 21001
        site_lines_21001 = []
        for site in self.site_ids_21001:
            site_lines_21001.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISO 31001
        site_lines_31001 = []
        for site in self.site_ids_31001:
            site_lines_31001.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        # ISPO
        site_lines_ispo = []
        for site in self.site_ids_ispo:
            site_lines_ispo.append((0, 0, {
                'tipe_site': site.tipe_site,
                'address': site.address,
                'effective_emp': site.effective_emp,
                'total_emp': site.total_emp,
            }))
        
        # ISO 9001
        mandays_lines = []
        for mandays in self.mandays_ids:
            mandays_lines.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 14001
        mandays_lines_14001 = []
        for mandays in self.mandays_ids_14001:
            mandays_lines_14001.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 45001
        mandays_lines_45001 = []
        for mandays in self.mandays_ids_45001:
            mandays_lines_45001.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 27001
        mandays_lines_27001 = []
        for mandays in self.mandays_ids_27001:
            mandays_lines_27001.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 27701
        mandays_lines_27701 = []
        for mandays in self.mandays_ids_27701:
            mandays_lines_27701.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 27017
        mandays_lines_27017 = []
        for mandays in self.mandays_ids_27017:
            mandays_lines_27017.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 27018
        mandays_lines_27018 = []
        for mandays in self.mandays_ids_27018:
            mandays_lines_27018.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 27001_2022
        mandays_lines_27001_2022 = []
        for mandays in self.mandays_ids_27001_2022:
            mandays_lines_27001_2022.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # HACCP
        mandays_lines_haccp = []
        for mandays in self.mandays_ids_haccp:
            mandays_lines_haccp.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # GMP
        mandays_lines_gmp = []
        for mandays in self.mandays_ids_gmp:
            mandays_lines_gmp.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 22000
        mandays_lines_22000 = []
        for mandays in self.mandays_ids_22000:
            mandays_lines_22000.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 22301
        mandays_lines_22301 = []
        for mandays in self.mandays_ids_22301:
            mandays_lines_22301.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 31000
        mandays_lines_31000 = []
        for mandays in self.mandays_ids_31000:
            mandays_lines_31000.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 9994
        mandays_lines_9994 = []
        for mandays in self.mandays_ids_9994:
            mandays_lines_9994.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 37001
        mandays_lines_37001 = []
        for mandays in self.mandays_ids_37001:
            mandays_lines_37001.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 13485
        mandays_lines_13485 = []
        for mandays in self.mandays_ids_13485:
            mandays_lines_13485.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # SMK
        mandays_lines_smk = []
        for mandays in self.mandays_ids_smk:
            mandays_lines_smk.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 21000
        mandays_lines_21000 = []
        for mandays in self.mandays_ids_21000:
            mandays_lines_21000.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 37301
        mandays_lines_37301 = []
        for mandays in self.mandays_ids_37301:
            mandays_lines_37301.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 21001
        mandays_lines_21001 = []
        for mandays in self.mandays_ids_21001:
            mandays_lines_21001.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISO 31001
        mandays_lines_31001 = []
        for mandays in self.mandays_ids_31001:
            mandays_lines_31001.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))
        # ISPO
        mandays_lines_ispo = []
        for mandays in self.mandays_ids_ispo:
            mandays_lines_ispo.append((0, 0, {
                'nama_site': mandays.nama_site,
                'stage_1': mandays.stage_1,
                'stage_2': mandays.stage_2,
                'surveilance_1': mandays.surveilance_1,
                'surveilance_2': mandays.surveilance_2,
                'surveilance_3': mandays.surveilance_3,
                'surveilance_4': mandays.surveilance_4,
                'recertification': mandays.recertification,
                'recertification_2': mandays.recertification_2,                
                'remarks': mandays.remarks,
            }))

        wizard_audit = self.env['tsi.wizard_audit'].create({
            'crm_reference': crm_reference,
            'partner_id': nama_client,
            'iso_standard_ids': iso_standard_ids,
            'iso_reference': iso_reference.id if iso_reference else False,
            'ispo_reference': ispo_reference.id if ispo_reference else False,
            'sales_reference': sales_reference.id if sales_reference else False,
            'review_reference': [(6, 0, review_reference.ids)] if review_reference else False,
            'review_reference_ispo': [(6, 0, review_reference_ispo.ids)] if review_reference_ispo else False,
            'ea_code_9001': ea_code_9001,
            'accreditation_9001': accreditation_9001,
            'ea_code_14001': ea_code_14001,
            'accreditation_14001': accreditation_14001,
            'ea_code_45001': ea_code_45001,
            'accreditation_45001': accreditation_45001,
            'ea_code_37001': ea_code_37001,
            'accreditation_37001': accreditation_37001,
            'ea_code_13485': ea_code_13485,
            'accreditation_13485': accreditation_13485,
            'ea_code_22000': ea_code_22000,
            'accreditation_22000': accreditation_22000,
            'ea_code_27001': ea_code_27001,
            'accreditation_27001': accreditation_27001,
            'ea_code_27001_2022': ea_code_27001_2022,
            'accreditation_27001_2022': accreditation_27001_2022,
            'ea_code_27701': ea_code_27701,
            'accreditation_27701': accreditation_27701,
            'ea_code_27017': ea_code_27017,
            'accreditation_27017': accreditation_27017,
            'ea_code_27018': ea_code_27018,
            'accreditation_27018': accreditation_27018,
            'ea_code_31000': ea_code_31000,
            'accreditation_31000': accreditation_31000,
            'ea_code_22301': ea_code_22301,
            'accreditation_22301': accreditation_22301,
            'ea_code_9994': ea_code_9994,
            'accreditation_9994': accreditation_9994,
            'ea_code_37301': ea_code_37301,
            'accreditation_37301': accreditation_37301,
            'ea_code_31001': ea_code_31001,
            'accreditation_31001': accreditation_31001,
            'ea_code_21001': ea_code_21001,
            'accreditation_21001': accreditation_21001,
            'ea_code_21000': ea_code_21000,
            'accreditation_21000': accreditation_21000,
            'ea_code_haccp': ea_code_haccp,
            'accreditation_haccp': accreditation_haccp,
            'ea_code_smk': ea_code_smk,
            'accreditation_smk': accreditation_smk,
            'ea_code_gmp': ea_code_gmp,
            'accreditation_gmp': accreditation_gmp,
            'ea_code_ispo': ea_code_ispo,
            'accreditation_ispo': accreditation_ispo,
            'scope': scope,
            'boundaries': boundaries,
            'sales': sales,
            'line_ids': line_items,
            # Site perstandard
            'site_ids': site_lines,
            'site_ids_14001': site_lines_14001,
            'site_ids_45001': site_lines_45001,
            'site_ids_27001': site_lines_27001,
            'site_ids_27701': site_lines_27701,
            'site_ids_27017': site_lines_27017,
            'site_ids_27018': site_lines_27018,
            'site_ids_27001_2022': site_lines_27001_2022,
            'site_ids_haccp': site_lines_haccp,
            'site_ids_gmp': site_lines_gmp,
            'site_ids_22000': site_lines_22000,
            'site_ids_22301': site_lines_22301,
            'site_ids_31000': site_lines_31000,
            'site_ids_9994': site_lines_9994,
            'site_ids_37001': site_lines_37001,
            'site_ids_13485': site_lines_13485,
            'site_ids_smk': site_lines_smk,
            'site_ids_21000': site_lines_21000,
            'site_ids_37301': site_lines_37301,
            'site_ids_21001': site_lines_21001,
            'site_ids_31001': site_lines_31001,
            'site_ids_ispo': site_lines_ispo,
            # Mandays perstandard
            'mandays_ids': mandays_lines,
            'mandays_ids_14001': mandays_lines_14001,
            'mandays_ids_45001': mandays_lines_45001,
            'mandays_ids_27001': mandays_lines_27001,
            'mandays_ids_27701': mandays_lines_27701,
            'mandays_ids_27017': mandays_lines_27017,
            'mandays_ids_27018': mandays_lines_27018,
            'mandays_ids_27001_2022': mandays_lines_27001_2022,
            'mandays_ids_haccp': mandays_lines_haccp,
            'mandays_ids_gmp': mandays_lines_gmp,
            'mandays_ids_22000': mandays_lines_22000,
            'mandays_ids_22301': mandays_lines_22301,
            'mandays_ids_31000': mandays_lines_31000,
            'mandays_ids_9994': mandays_lines_9994,
            'mandays_ids_37001': mandays_lines_37001,
            'mandays_ids_13485': mandays_lines_13485,
            'mandays_ids_smk': mandays_lines_smk,
            'mandays_ids_21000': mandays_lines_21000,
            'mandays_ids_37301': mandays_lines_37301,
            'mandays_ids_21001': mandays_lines_21001,
            'mandays_ids_31001': mandays_lines_31001,
            'mandays_ids_ispo': mandays_lines_ispo,
            'cycle': cycle,
            'tgl_perkiraan_selesai': self.tgl_perkiraan_selesai,
            'tgl_perkiraan_audit_selesai': self.tgl_perkiraan_audit_selesai,
            'no_kontrak': no_kontrak,
            'closing_by': closing_by,
            'category': category,
            'pic_direct': pic_direct,
            'email_direct': email_direct,
            'phone_direct': phone_direct,
            'pic_konsultan1': pic_konsultan1,
            'email_konsultan': email_konsultan,
            'phone_konsultan': phone_konsultan,
            'transport_by': transport_by,
            'hotel_by': hotel_by,
            'tipe_klien_transport': tipe_klien_transport,
            'tipe_klien_hotel': tipe_klien_hotel,
            'pic_crm': pic_crm
        })

        wizard_audit._onchange_partner_id()

        return {
            'name': "Create Audit",
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit',
            'res_id': wizard_audit.id,
            'target': 'new',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_view').id,
            'context': {
                'default_crm_reference': self.id,
            },
        }

    def create_wizard_lanjut(self):
        # Initialize line items and other data
        line_items = []

        # Collect data for tahapan_ori_lines1
        if self.tahapan_ori_lines1:
            for tahapan_line in self.tahapan_ori_lines1:
                standard_name = tahapan_line.standard.name
                mandays_s1 = tahapan_line.mandays_s1 or 0

                try:
                    mandays_s1_float = float(mandays_s1)
                except (ValueError, TypeError):
                    mandays_s1_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s1,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s1,
                    'tahapan_audit': 'Surveillance 1',
                    'nilai': mandays_s1_float,
                }))

        # Collect data for tahapan_ori_lines2
        if self.tahapan_ori_lines2:
            for tahapan_line in self.tahapan_ori_lines2:
                standard_name = tahapan_line.standard.name
                mandays_s2 = tahapan_line.mandays_s2 or 0

                try:
                    mandays_s2_float = float(mandays_s2)
                except (ValueError, TypeError):
                    mandays_s2_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s2,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s2,
                    'tahapan_audit': 'Surveillance 2',
                    'nilai': mandays_s2_float,
                }))

        # Collect data for tahapan_ori_lines3
        if self.tahapan_ori_lines3:
            for tahapan_line in self.tahapan_ori_lines3:
                standard_name = tahapan_line.standard.name
                mandays_s3 = tahapan_line.mandays_s3 or 0

                try:
                    mandays_s3_float = float(mandays_s3)
                except (ValueError, TypeError):
                    mandays_s3_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s3,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s3,
                    'tahapan_audit': 'Surveillance 3',
                    'nilai': mandays_s3_float,
                }))

        # Collect data for tahapan_ori_lines4
        if self.tahapan_ori_lines4:
            for tahapan_line in self.tahapan_ori_lines4:
                standard_name = tahapan_line.standard.name
                mandays_s4 = tahapan_line.mandays_s4 or 0

                try:
                    mandays_s4_float = float(mandays_s4)
                except (ValueError, TypeError):
                    mandays_s4_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s4,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s4,
                    'tahapan_audit': 'Surveillance 4',
                    'nilai': mandays_s4_float,
                }))

        # Collect data for tahapan_ori_lines5
        if self.tahapan_ori_lines5:
            for tahapan_line in self.tahapan_ori_lines5:
                standard_name = tahapan_line.standard.name
                mandays_s5 = tahapan_line.mandays_s5 or 0

                try:
                    mandays_s5_float = float(mandays_s5)
                except (ValueError, TypeError):
                    mandays_s5_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s5,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s5,
                    'tahapan_audit': 'Surveillance 5',
                    'nilai': mandays_s5_float,
                }))

        # Collect data for tahapan_ori_lines6
        if self.tahapan_ori_lines6:
            for tahapan_line in self.tahapan_ori_lines6:
                standard_name = tahapan_line.standard.name
                mandays_s6 = tahapan_line.mandays_s6 or 0

                try:
                    mandays_s6_float = float(mandays_s6)
                except (ValueError, TypeError):
                    mandays_s6_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s6,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s6,
                    'tahapan_audit': 'Surveillance 6',
                    'nilai': mandays_s6_float,
                }))

        # Collect data for tahapan_ori_lines_re
        if self.tahapan_ori_lines_re:
            for tahapan_line in self.tahapan_ori_lines_re:
                standard_name = tahapan_line.standard.name
                mandays_re = tahapan_line.mandays_rs or 0

                try:
                    mandays_re_float = float(mandays_re)
                except (ValueError, TypeError):
                    mandays_re_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re,
                    'tahapan_audit': 'Recertification 1',
                    'nilai': mandays_re_float,
                }))

        # Collect data for tahapan_ori_lines_re2
        if self.tahapan_ori_lines_re2:
            for tahapan_line in self.tahapan_ori_lines_re2:
                standard_name = tahapan_line.standard.name
                mandays_re2 = tahapan_line.mandays_rs2 or 0

                try:
                    mandays_re2_float = float(mandays_re2)
                except (ValueError, TypeError):
                    mandays_re2_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accre2ditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re2,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re2,
                    'tahapan_audit': 'Recertification 2',
                    'nilai': mandays_re2_float,
                }))

        # Collect data for tahapan_ori_lines_re3
        if self.tahapan_ori_lines_re3:
            for tahapan_line in self.tahapan_ori_lines_re3:
                standard_name = tahapan_line.standard.name
                mandays_re3 = tahapan_line.mandays_rs3 or 0

                try:
                    mandays_re3_float = float(mandays_re3)
                except (ValueError, TypeError):
                    mandays_re3_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re3,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re3,
                    'tahapan_audit': 'Recertification 3',
                    'nilai': mandays_re3_float,
                }))

        # Create the wizard
        wizard_lanjut = self.env['tsi.wizard_lanjut'].create({
            'partner_id': self.partner_id.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            'sales': self.sales.id,
            'associate': self.associate.id,
            'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            'pic': self.pic.id,
            'akreditasi': self.akreditasi.id,
            'alamat': self.alamat,
            'closing_by': self.closing_by,
            'level_audit': self.level_audit,
            'level_audit_ispo': self.level_audit_ispo,
            'referal': self.referal,
            'line_ids': line_items,
        })

        return {
            'name': "CRM Lanjut",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_lanjut',
            'res_id': wizard_lanjut.id,
            'view_id': self.env.ref('v15_tsi.tsi_wizard_lanjut_view').id,
            'target': 'new',
        }

    def create_wizard_suspend(self):
        # Initialize line items and other data
        line_items = []

        # Collect data for tahapan_ori_lines1
        if self.tahapan_ori_lines1:
            for tahapan_line in self.tahapan_ori_lines1:
                standard_name = tahapan_line.standard.name
                mandays_s1 = tahapan_line.mandays_s1 or 0

                try:
                    mandays_s1_float = float(mandays_s1)
                except (ValueError, TypeError):
                    mandays_s1_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s1,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s1,
                    'tahapan_audit': 'Surveillance 1',
                    'nilai': mandays_s1_float,
                }))

        # Collect data for tahapan_ori_lines2
        if self.tahapan_ori_lines2:
            for tahapan_line in self.tahapan_ori_lines2:
                standard_name = tahapan_line.standard.name
                mandays_s2 = tahapan_line.mandays_s2 or 0

                try:
                    mandays_s2_float = float(mandays_s2)
                except (ValueError, TypeError):
                    mandays_s2_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s2,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s2,
                    'tahapan_audit': 'Surveillance 2',
                    'nilai': mandays_s2_float,
                }))

        # Collect data for tahapan_ori_lines3
        if self.tahapan_ori_lines3:
            for tahapan_line in self.tahapan_ori_lines3:
                standard_name = tahapan_line.standard.name
                mandays_s3 = tahapan_line.mandays_s3 or 0

                try:
                    mandays_s3_float = float(mandays_s3)
                except (ValueError, TypeError):
                    mandays_s3_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s3,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s3,
                    'tahapan_audit': 'Surveillance 3',
                    'nilai': mandays_s3_float,
                }))

        # Collect data for tahapan_ori_lines4
        if self.tahapan_ori_lines4:
            for tahapan_line in self.tahapan_ori_lines4:
                standard_name = tahapan_line.standard.name
                mandays_s4 = tahapan_line.mandays_s4 or 0

                try:
                    mandays_s4_float = float(mandays_s4)
                except (ValueError, TypeError):
                    mandays_s4_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s4,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s4,
                    'tahapan_audit': 'Surveillance 4',
                    'nilai': mandays_s4_float,
                }))

        # Collect data for tahapan_ori_lines5
        if self.tahapan_ori_lines5:
            for tahapan_line in self.tahapan_ori_lines5:
                standard_name = tahapan_line.standard.name
                mandays_s5 = tahapan_line.mandays_s5 or 0

                try:
                    mandays_s5_float = float(mandays_s5)
                except (ValueError, TypeError):
                    mandays_s5_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s5,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s5,
                    'tahapan_audit': 'Surveillance 5',
                    'nilai': mandays_s5_float,
                }))

        # Collect data for tahapan_ori_lines6
        if self.tahapan_ori_lines6:
            for tahapan_line in self.tahapan_ori_lines6:
                standard_name = tahapan_line.standard.name
                mandays_s6 = tahapan_line.mandays_s6 or 0

                try:
                    mandays_s6_float = float(mandays_s6)
                except (ValueError, TypeError):
                    mandays_s6_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s6,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s6,
                    'tahapan_audit': 'Surveillance 6',
                    'nilai': mandays_s6_float,
                }))

        # Collect data for tahapan_ori_lines_re
        if self.tahapan_ori_lines_re:
            for tahapan_line in self.tahapan_ori_lines_re:
                standard_name = tahapan_line.standard.name
                mandays_re = tahapan_line.mandays_rs or 0

                try:
                    mandays_re_float = float(mandays_re)
                except (ValueError, TypeError):
                    mandays_re_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re,
                    'tahapan_audit': 'Recertification 1',
                    'nilai': mandays_re_float,
                }))

        # Collect data for tahapan_ori_lines_re2
        if self.tahapan_ori_lines_re2:
            for tahapan_line in self.tahapan_ori_lines_re2:
                standard_name = tahapan_line.standard.name
                mandays_re2 = tahapan_line.mandays_rs2 or 0

                try:
                    mandays_re2_float = float(mandays_re2)
                except (ValueError, TypeError):
                    mandays_re2_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re2,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re2,
                    'tahapan_audit': 'Recertification 2',
                    'nilai': mandays_re2_float,
                }))

        # Collect data for tahapan_ori_lines_re3
        if self.tahapan_ori_lines_re3:
            for tahapan_line in self.tahapan_ori_lines_re3:
                standard_name = tahapan_line.standard.name
                mandays_re3 = tahapan_line.mandays_rs3 or 0

                try:
                    mandays_re3_float = float(mandays_re3)
                except (ValueError, TypeError):
                    mandays_re3_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re3,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re3,
                    'tahapan_audit': 'Recertification 3',
                    'nilai': mandays_re3_float,
                }))

        # Create the wizard
        wizard_suspend = self.env['tsi.wizard_suspend'].create({
            'partner_id': self.partner_id.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            'sales': self.sales.id,
            'associate': self.associate.id,
            'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            'pic': self.pic.id,
            'akreditasi': self.akreditasi.id,
            'alamat': self.alamat,
            'closing_by': self.closing_by,
            'level_audit': self.level_audit,
            'level_audit_ispo': self.level_audit_ispo,
            'referal': self.referal,
            'line_ids': line_items,
        })

        return {
            'name': "CRM Suspend",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_suspend',
            'res_id': wizard_suspend.id,
            'view_id': self.env.ref('v15_tsi.tsi_wizard_suspend_view').id,
            'target': 'new',
        }

    def create_wizard_loss(self):
        # Initialize line items and other data
        line_items = []

        # Collect data for tahapan_ori_lines1
        if self.tahapan_ori_lines1:
            for tahapan_line in self.tahapan_ori_lines1:
                standard_name = tahapan_line.standard.name
                mandays_s1 = tahapan_line.mandays_s1 or 0

                try:
                    mandays_s1_float = float(mandays_s1)
                except (ValueError, TypeError):
                    mandays_s1_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s1,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s1,
                    'tahapan_audit': 'Surveillance 1',
                    'nilai': mandays_s1_float,
                }))

        # Collect data for tahapan_ori_lines2
        if self.tahapan_ori_lines2:
            for tahapan_line in self.tahapan_ori_lines2:
                standard_name = tahapan_line.standard.name
                mandays_s2 = tahapan_line.mandays_s2 or 0

                try:
                    mandays_s2_float = float(mandays_s2)
                except (ValueError, TypeError):
                    mandays_s2_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s2,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s2,
                    'tahapan_audit': 'Surveillance 2',
                    'nilai': mandays_s2_float,
                }))

        # Collect data for tahapan_ori_lines3
        if self.tahapan_ori_lines3:
            for tahapan_line in self.tahapan_ori_lines3:
                standard_name = tahapan_line.standard.name
                mandays_s3 = tahapan_line.mandays_s3 or 0

                try:
                    mandays_s3_float = float(mandays_s3)
                except (ValueError, TypeError):
                    mandays_s3_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s3,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s3,
                    'tahapan_audit': 'Surveillance 3',
                    'nilai': mandays_s3_float,
                }))

        # Collect data for tahapan_ori_lines4
        if self.tahapan_ori_lines4:
            for tahapan_line in self.tahapan_ori_lines4:
                standard_name = tahapan_line.standard.name
                mandays_s4 = tahapan_line.mandays_s4 or 0

                try:
                    mandays_s4_float = float(mandays_s4)
                except (ValueError, TypeError):
                    mandays_s4_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s4,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s4,
                    'tahapan_audit': 'Surveillance 4',
                    'nilai': mandays_s4_float,
                }))

        # Collect data for tahapan_ori_lines5
        if self.tahapan_ori_lines5:
            for tahapan_line in self.tahapan_ori_lines5:
                standard_name = tahapan_line.standard.name
                mandays_s5 = tahapan_line.mandays_s5 or 0

                try:
                    mandays_s5_float = float(mandays_s5)
                except (ValueError, TypeError):
                    mandays_s5_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s5,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s5,
                    'tahapan_audit': 'Surveillance 5',
                    'nilai': mandays_s5_float,
                }))

        # Collect data for tahapan_ori_lines6
        if self.tahapan_ori_lines6:
            for tahapan_line in self.tahapan_ori_lines6:
                standard_name = tahapan_line.standard.name
                mandays_s6 = tahapan_line.mandays_s6 or 0

                try:
                    mandays_s6_float = float(mandays_s6)
                except (ValueError, TypeError):
                    mandays_s6_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_s6,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_s6,
                    'tahapan_audit': 'Surveillance 6',
                    'nilai': mandays_s6_float,
                }))

        # Collect data for tahapan_ori_lines_re
        if self.tahapan_ori_lines_re:
            for tahapan_line in self.tahapan_ori_lines_re:
                standard_name = tahapan_line.standard.name
                mandays_re = tahapan_line.mandays_rs or 0

                try:
                    mandays_re_float = float(mandays_re)
                except (ValueError, TypeError):
                    mandays_re_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re,
                    'tahapan_audit': 'Recertification 1',
                    'nilai': mandays_re_float,
                }))

        # Collect data for tahapan_ori_lines_re2
        if self.tahapan_ori_lines_re2:
            for tahapan_line in self.tahapan_ori_lines_re2:
                standard_name = tahapan_line.standard.name
                mandays_re2 = tahapan_line.mandays_rs2 or 0

                try:
                    mandays_re2_float = float(mandays_re2)
                except (ValueError, TypeError):
                    mandays_re2_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re2,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re2,
                    'tahapan_audit': 'Recertification 2',
                    'nilai': mandays_re2_float,
                }))

        # Collect data for tahapan_ori_lines_re3
        if self.tahapan_ori_lines_re3:
            for tahapan_line in self.tahapan_ori_lines_re3:
                standard_name = tahapan_line.standard.name
                mandays_re3 = tahapan_line.mandays_rs3 or 0

                try:
                    mandays_re3_float = float(mandays_re3)
                except (ValueError, TypeError):
                    mandays_re3_float = 0.0

                line_items.append((0, 0, {
                    'iso_standard_ids': [(6, 0, tahapan_line.standard.ids)],
                    'accreditation': tahapan_line.accreditation.id,
                    'nomor_kontrak' : tahapan_line.nomor_kontrak_re3,
                    'tanggal_kontrak' : tahapan_line.tanggal_kontrak_re3,
                    'tahapan_audit': 'Recertification 3',
                    'nilai': mandays_re3_float,
                }))

        # Create the wizard
        wizard_loss = self.env['tsi.wizard_loss'].create({
            'partner_id': self.partner_id.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            'sales': self.sales.id,
            'associate': self.associate.id,
            'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            'pic': self.pic.id,
            'akreditasi': self.akreditasi.id,
            'alamat': self.alamat,
            'closing_by': self.closing_by,
            'level_audit': self.level_audit,
            'level_audit_ispo': self.level_audit_ispo,
            'referal': self.referal,
            'line_ids': line_items,
        })

        return {
            'name': "CRM Loss",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_loss',
            'res_id': wizard_loss.id,
            'view_id': self.env.ref('v15_tsi.tsi_wizard_loss_view').id,
            'target': 'new',
        }

    def action_create_partner_certificate(self):
        certificate_data = []
        tahun_masuk_entries = {}

        for history in self:
            partner = history.partner_id
            mandays_lines = (
                history.tahapan_ori_lines + 
                history.tahapan_ori_lines1 + 
                history.tahapan_ori_lines2 + 
                history.tahapan_ori_lines3 + 
                history.tahapan_ori_lines4 +
                history.tahapan_ori_lines5 + 
                history.tahapan_ori_lines6 + 
                history.tahapan_ori_lines_re +
                history.tahapan_ori_lines_re2 +
                history.tahapan_ori_lines_re3
            )

            for line in mandays_lines:
                cert_type = None
                cert_dates = {}

                if line.tahapan_id:
                    cert_type = 'initial audit'
                    cert_dates = {
                        'no_sertifikat': line.nomor_ia,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat,
                        'initial_date': line.tanggal_sertifikat1,
                        'issue_date': line.tanggal_sertifikat2,
                        'validity_date': line.tanggal_sertifikat3
                    }
                elif line.tahapan_id1:
                    cert_type = 'Surveillance 1'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s1,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_s1,
                        'initial_date': line.initial_sertifikat_s_2,
                        'issue_date': line.issue_sertifikat_s_3,
                        'validity_date': line.validity_sertifikat_s_4
                    }
                elif line.tahapan_id2:
                    cert_type = 'Surveillance 2'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s2,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_s2,
                        'initial_date': line.tanggal_sertifikat_initial_s2,
                        'issue_date': line.tanggal_sertifikat_issued_s2,
                        'validity_date': line.tanggal_sertifikat_validty_s2
                    }
                elif line.tahapan_id3:
                    cert_type = 'Surveillance 3'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s3,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_s3,
                        'initial_date': line.initial_tanggal_sertifikat_s3,
                        'issue_date': line.issued_tanggal_sertifikat_s3,
                        'validity_date': line.validty_tanggal_sertifikat_s3
                    }
                elif line.tahapan_id4:
                    cert_type = 'Surveillance 4'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s4,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_s4,
                        'initial_date': line.initiall_s4,
                        'issue_date': line.issued_s4,
                        'validity_date': line.validity_s4
                    }
                elif line.tahapan_id5:
                    cert_type = 'Surveillance 5'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s5,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_s5,
                        'initial_date': line.initial_tanggal_sertifikat_s5,
                        'issue_date': line.issued_tanggal_sertifikat_s5,
                        'validity_date': line.validty_tanggal_sertifikat_s5
                    }
                elif line.tahapan_id6:
                    cert_type = 'Surveillance 6'
                    cert_dates = {
                        'no_sertifikat': line.nomor_s6,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_s6,
                        'initial_date': line.initiall_s6,
                        'issue_date': line.issued_s6,
                        'validity_date': line.validity_s6
                    }
                elif line.tahapan_id_re:
                    cert_type = 'Recertification'
                    cert_dates = {
                        'no_sertifikat': line.nomor_re,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_rs,
                        'initial_date': line.tanggal_sertifikat_initial_rs,
                        'issue_date': line.tanggal_sertifikat__issued_rs,
                        'validity_date': line.tanggal_sertifikat_validty_rs
                    }
                elif line.tahapan_id_re2:
                    cert_type = 'Recertification 2'
                    cert_dates = {
                        'no_sertifikat': line.nomor_re2,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_rs2,
                        'initial_date': line.tanggal_sertifikat_initial_rs2,
                        'issue_date': line.tanggal_sertifikat__issued_rs2,
                        'validity_date': line.tanggal_sertifikat_validty_rs2
                    }
                elif line.tahapan_id_re3:
                    cert_type = 'Recertification 3'
                    cert_dates = {
                        'no_sertifikat': line.nomor_re3,
                        'standard': line.standard.id,
                        'expiry_date': line.tanggal_sertifikat_rs3,
                        'initial_date': line.tanggal_sertifikat_initial_rs3,
                        'issue_date': line.tanggal_sertifikat__issued_rs3,
                        'validity_date': line.tanggal_sertifikat_validty_rs3
                    }

                if cert_type:
                    # Prepare certificate entry
                    certificate_entry = {
                        'partner_id': partner.id,
                        'no_sertifikat': cert_dates.get('no_sertifikat'),
                        'standard': cert_dates.get('standard'),
                        'initial_date': cert_dates.get('initial_date'),
                        'issue_date': cert_dates.get('issue_date'),
                        'validity_date': cert_dates.get('validity_date'),
                        'expiry_date': cert_dates.get('expiry_date'),
                        'tahapan_audit': cert_type
                    }
                    # Add certificate entry if it does not already exist
                    existing_certificates = self.env['tsi.partner.certificate'].search([
                        ('partner_id', '=', partner.id),
                        ('no_sertifikat', '=', cert_dates.get('no_sertifikat')),
                        ('tahapan_audit', '=', cert_type)
                    ])
                    
                    if not existing_certificates:
                        certificate_data.append(certificate_entry)

                    # Prepare data for tahun_masuk
                    issue_year = cert_dates.get('issue_date').year if cert_dates.get('issue_date') else None
                    tahun_masuk_entry = {
                        'partner_id': partner.id,
                        'iso_standard_ids': [(6, 0, line.standard.ids)],
                        'issue_date': cert_dates.get('issue_date'),
                        'certification_year': issue_year if issue_year else '',
                    }
                    iso_standard_ids_tuple = tuple(line.standard.ids)
                    if iso_standard_ids_tuple in tahun_masuk_entries:
                        tahun_masuk_entries[iso_standard_ids_tuple].append(tahun_masuk_entry)
                    else:
                        tahun_masuk_entries[iso_standard_ids_tuple] = [tahun_masuk_entry]

        # Create new partner certificates if they do not exist already
        if certificate_data:
            self.env['tsi.partner.certificate'].create(certificate_data)

        # Do not delete old tahun_masuk entries, only add new ones
        if tahun_masuk_entries:
            for entries in tahun_masuk_entries.values():
                for entry in entries:
                    # Check if a similar entry already exists
                    existing_tahun_masuk = self.env['tsi.tahun_masuk'].search([
                        ('partner_id', '=', entry['partner_id']),
                        ('iso_standard_ids', 'in', entry['iso_standard_ids'][0][2])
                    ])

                    if not existing_tahun_masuk:
                        self.env['tsi.tahun_masuk'].create(entry)

        return True

    @api.onchange('tahapan_audit_ids')
    def _onchange_tahapan(self):
        for obj in self:
            if obj.tahapan_audit_ids :
                obj.show_initial         = False
                obj.show_survilance1     = False
                obj.show_survilance2     = False
                obj.show_survilance3     = False
                obj.show_survilance4     = False                
                obj.show_recertification = False
                obj.show_survilance5     = False
                obj.show_survilance6     = False                
                obj.show_recertification2 = False
                obj.show_recertification3 = False
                for tahapan in obj.tahapan_audit_ids :
                    if tahapan.name == 'Initial Audit' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_initial = True
                    if tahapan.name == 'Surveillance 1' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance1 = True
                    if tahapan.name == 'Surveillance 2' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance2 = True
                    if tahapan.name == 'Surveillance 3' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance3 = True
                    if tahapan.name == 'Surveillance 4' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance4 = True
                    if tahapan.name == 'Recertification 1' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_recertification = True
                    if tahapan.name == 'Surveillance 5' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance5 = True
                    if tahapan.name == 'Surveillance 6' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_survilance6 = True
                    if tahapan.name == 'Recertification 2' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_recertification2 = True
                    if tahapan.name == 'Recertification 3' :
                        if obj.show_tahapan != True :
                            obj.show_tahapan = False
                        obj.show_recertification3 = True
                    # else :
                    #    obj.show_recertification = True
    
    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):
        for tahapan in self:
            if tahapan.partner_id:
                tahapan.pricelist_id = False
                continue
            tahapan = tahapan.with_company(tahapan.company_id)
            tahapan.pricelist_id = tahapan.partner_id.property_product_pricelist
    
    @api.depends('pricelist_id', 'company_id')
    def _compute_currency_id(self):
        for tahapan in self:
            tahapan.currency_id = tahapan.pricelist_id.currency_id or tahapan.company_id.currency_id
    
    @api.depends('tahapan_ori_lines.mandays')
    def _compute_amounts(self):
        """Compute the total amounts of the SO."""
        for tahapan in self:
            tahapan_ori_lines = tahapan.tahapan_ori_lines.filtered(lambda x: not x.display_type)

            if tahapan.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines.mapped('mandays'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan.amount_total = tahapan.amount_untaxed

    @api.depends('tahapan_ori_lines1.mandays_s1')
    def _compute_amounts_s1(self):
        """Compute the total amounts of the SO."""
        for tahapans1 in self:
            tahapan_ori_lines1 = tahapans1.tahapan_ori_lines1.filtered(lambda x: not x.display_type)

            if tahapans1.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines1
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans1.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines1.mapped('mandays_s1'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans1.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans1.amount_total_s1 = tahapans1.amount_untaxed

    @api.depends('tahapan_ori_lines2.mandays_s2')
    def _compute_amounts_s2(self):
        """Compute the total amounts of the SO."""
        for tahapans2 in self:
            tahapan_ori_lines2 = tahapans2.tahapan_ori_lines2.filtered(lambda x: not x.display_type)

            if tahapans2.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines2
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines2.mapped('mandays_s2'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans2.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans2.amount_total_s2 = tahapans2.amount_untaxed

    @api.depends('tahapan_ori_lines3.mandays_s3')
    def _compute_amounts_s3(self):
        """Compute the total amounts of the SO."""
        for tahapans3 in self:
            tahapan_ori_lines3 = tahapans3.tahapan_ori_lines3.filtered(lambda x: not x.display_type)

            if tahapans3.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines3.mapped('mandays_s3'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans3.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans3.amount_total_s3 = tahapans3.amount_untaxed

    @api.depends('tahapan_ori_lines4.mandays_s4')
    def _compute_amounts_s4(self):
        """Compute the total amounts of the SO."""
        for tahapans4 in self:
            tahapan_ori_lines4 = tahapans4.tahapan_ori_lines4.filtered(lambda x: not x.display_type)

            if tahapans4.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines4
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans4.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines4.mapped('mandays_s4'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans4.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans4.amount_total_s4 = tahapans4.amount_untaxed

    @api.depends('tahapan_ori_lines_re.mandays_rs')
    def _compute_amounts_re(self):
        """Compute the total amounts of the SO."""
        for tahapan_re in self:
            tahapan_ori_lines_re = tahapan_re.tahapan_ori_lines_re.filtered(lambda x: not x.display_type)

            if tahapan_re.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines_re
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan_re.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines_re.mapped('mandays_rs'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan_re.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan_re.amount_total_re = tahapan_re.amount_untaxed

    @api.depends('tahapan_ori_lines5.mandays_s5')
    def _compute_amounts_s5(self):
        """Compute the total amounts of the SO."""
        for tahapans5 in self:
            tahapan_ori_lines5 = tahapans5.tahapan_ori_lines5.filtered(lambda x: not x.display_type)

            if tahapans5.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines5
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines5.mapped('mandays_s5'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans5.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans5.amount_total_s5 = tahapans5.amount_untaxed

    @api.depends('tahapan_ori_lines6.mandays_s6')
    def _compute_amounts_s6(self):
        """Compute the total amounts of the SO."""
        for tahapans6 in self:
            tahapan_ori_lines6 = tahapans6.tahapan_ori_lines6.filtered(lambda x: not x.display_type)

            if tahapans6.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines6
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapans6.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines6.mapped('mandays_s6'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapans6.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapans6.amount_total_s6 = tahapans6.amount_untaxed

    @api.depends('tahapan_ori_lines_re2.mandays_rs2')
    def _compute_amounts_re2(self):
        """Compute the total amounts of the SO."""
        for tahapan_re2 in self:
            tahapan_ori_lines_re2 = tahapan_re2.tahapan_ori_lines_re2.filtered(lambda x: not x.display_type)

            if tahapan_re2.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines_re2
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan_re2.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines_re2.mapped('mandays_rs2'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan_re2.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan_re2.amount_total_re2 = tahapan_re2.amount_untaxed

    @api.depends('tahapan_ori_lines_re3.mandays_rs3')
    def _compute_amounts_re3(self):
        """Compute the total amounts of the SO."""
        for tahapan_re3 in self:
            tahapan_ori_lines_re3 = tahapan_re3.tahapan_ori_lines_re3.filtered(lambda x: not x.display_type)

            if tahapan_re3.company_id.tax_calculation_rounding_method == 'round_globally':
                tax_results = self.env['account.tax']._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                    for line in tahapan_ori_lines_re3
                ])
                totals = tax_results['totals']
                amount_untaxed = totals.get(tahapan_re3.currency_id, {}).get('amount_untaxed', 0.0)
                # amount_tax = totals.get(tahapan.currency_id, {}).get('amount_tax', 0.0)
            else:
                amount_untaxed = sum(tahapan_ori_lines_re3.mapped('mandays_rs3'))
                # amount_tax = sum(order_lines.mapped('price_tax'))

            tahapan_re3.amount_untaxed = amount_untaxed
            # order.amount_tax = amount_tax
            tahapan_re3.amount_total_re3 = tahapan_re3.amount_untaxed

    def open_pic_hk_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'PIC History Kontrak',
            'res_model': 'history_kontrak.pic.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }

    def unlink(self):
        raise UserError("Data tidak bisa dihapus!")

class CRMSiteLine(models.Model):
    _name = 'crm.site.line'
    _description = 'CRM Site Line'

    crm_site_id               = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_14001      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_45001      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_27001      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_27701      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_27017      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_27018      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_27001_2022 = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_haccp      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_gmp        = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_22000      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_22301      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_31000      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_9994       = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_37001      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_13485      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_smk        = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_21000      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_37301      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_21001      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')
    crm_site_id_31001      = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')

    crm_site_id_ispo        = fields.Many2one('tsi.history_kontrak', string='CRM Site', ondelete='cascade')

    tipe_site       = fields.Char('Type(HO, Factory etc)', tracking=True) 
    address         = fields.Char('Address', tracking=True) 
    effective_emp   = fields.Char('Total No. of Effective Employees', tracking=True) 
    total_emp       = fields.Char(string='Total No. of All Employees', tracking=True)

    @api.model
    def create(self, vals):
        record = super(CRMSiteLine, self).create(vals)

        related_fields = [field for field in self._fields if field.startswith('crm_site_id')]
        for field_name in related_fields:
            history_kontrak = record[field_name]
            if history_kontrak:
                standard_name = self._get_standard_name(field_name)
                message = self._prepare_message(record, action="Created", standard_name=standard_name)
                history_kontrak.message_post(body=message)

        return record

    def write(self, vals):
        res = super(CRMSiteLine, self).write(vals)
        for record in self:
            related_fields = [field for field in self._fields if field.startswith('crm_site_id')]
            for field_name in related_fields:
                history_kontrak = record[field_name]
                if history_kontrak:
                    standard_name = self._get_standard_name(field_name)
                    message = self._prepare_message(record, action="Updated", standard_name=standard_name)
                    history_kontrak.message_post(body=message)

        return res

    def unlink(self):
        for record in self:
            related_fields = [field for field in self._fields if field.startswith('crm_site_id')]
            for field_name in related_fields:
                history_kontrak = record[field_name]
                if history_kontrak:
                    standard_name = self._get_standard_name(field_name)
                    message = self._prepare_message(record, action="Deleted", standard_name=standard_name)
                    history_kontrak.message_post(body=message)

        return super(CRMSiteLine, self).unlink()

    def _prepare_message(self, record, action, standard_name):
        fields_to_include = ['tipe_site', 'address', 'effective_emp', 'total_emp']
        details = ", ".join([f"{field.replace('_', ' ').title()}: {getattr(record, field) or '-'}" for field in fields_to_include])
        return f"{action} - {standard_name}: {details}"

    def _get_standard_name(self, field_name):
        if field_name == 'crm_site_id':
            return "ISO 9001"
        elif '_' in field_name:
            standard_code = field_name.split('_')[-1]
            return f"ISO {standard_code}"
        return "Unknown Standard"

class CRMMandaysLine(models.Model):
    _name = 'crm.mandays.line'
    _description = 'CRM Mandays Line'

    crm_mandays_id    = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_14001      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_45001      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_27001      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_27701      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_27017      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_27018      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_27001_2022 = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_haccp      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_gmp        = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_22000      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_22301      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_31000      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_9994       = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_37001      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_13485      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_smk        = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_21000      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_37301      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_21001      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')
    crm_mandays_id_31001      = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')

    crm_mandays_id_ispo       = fields.Many2one('tsi.history_kontrak', string='CRM Mandays', ondelete='cascade')

    nama_site         = fields.Char(string='Nama Site', tracking=True)
    stage_1           = fields.Char(string='Stage 1', tracking=True)
    stage_2           = fields.Char(string='Stage 2', tracking=True)
    surveilance_1     = fields.Char(string='Surveillance 1', tracking=True)
    surveilance_2     = fields.Char(string='Surveillance 2', tracking=True)
    surveilance_3     = fields.Char(string='Surveillance 3', tracking=True)
    surveilance_4     = fields.Char(string='Surveillance 4', tracking=True)
    recertification   = fields.Char(string='Recertification 1', tracking=True)
    recertification_2 = fields.Char(string='Recertification 2', tracking=True)
    remarks           = fields.Char(string='Remarks', tracking=True)

    @api.model
    def create(self, vals):
        record = super(CRMMandaysLine, self).create(vals)

        related_fields = [field for field in self._fields if field.startswith('crm_mandays_id')]
        for field_name in related_fields:
            history_kontrak = record[field_name]
            if history_kontrak:
                standard_name = self._get_standard_name(field_name)
                message = self._prepare_message(record, action="Created", standard_name=standard_name)
                history_kontrak.message_post(body=message)

        return record

    def write(self, vals):
        res = super(CRMMandaysLine, self).write(vals)
        for record in self:
            related_fields = [field for field in self._fields if field.startswith('crm_mandays_id')]
            for field_name in related_fields:
                history_kontrak = record[field_name]
                if history_kontrak:
                    standard_name = self._get_standard_name(field_name)
                    message = self._prepare_message(record, action="Updated", standard_name=standard_name)
                    history_kontrak.message_post(body=message)

        return res

    def unlink(self):
        for record in self:
            related_fields = [field for field in self._fields if field.startswith('crm_mandays_id')]
            for field_name in related_fields:
                history_kontrak = record[field_name]
                if history_kontrak:
                    standard_name = self._get_standard_name(field_name)
                    message = self._prepare_message(record, action="Deleted", standard_name=standard_name)
                    history_kontrak.message_post(body=message)

        return super(CRMMandaysLine, self).unlink()

    def _prepare_message(self, record, action, standard_name):
        fields_to_include = [
            'nama_site', 'stage_1', 'stage_2', 'surveilance_1', 'surveilance_2',
            'surveilance_3', 'surveilance_4', 'recertification', 'recertification_2', 'remarks'
        ]
        details = ", ".join([f"{field.replace('_', ' ').title()}: {getattr(record, field) or '-'}" for field in fields_to_include])
        return f"{action} - {standard_name}: {details}"

    def _get_standard_name(self, field_name):   
        if field_name == 'crm_mandays_id':
            return "ISO 9001"
        elif '_' in field_name:
            standard_code = field_name.split('_')[-1]
            return f"ISO {standard_code}"
        return "Unknown Standard"   

class MandaysSalesGraph(models.Model):
    _name = 'tsi.harga.sales.graph'
    _description = 'Harga Sales Graph View'
    _auto = False

    state =fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('lanjut', 'Lanjut'),
            ('lost','Loss'),
            ('suspend', 'Suspend'),
            ], string='Status')
    sales = fields.Many2one('res.users', string="Sales", store=True)
    associate = fields.Many2one('res.partner', string="Associate", store=True)
    category = fields.Selection([
                ('bronze',  'Bronze'),
                ('silver',   'Silver'),
                ('gold', 'Gold')
                ], string='Category', store=True)
    closing_by = fields.Selection([
                ('konsultan',  'Konsultan'),
                ('direct',   'Direct'),
                ], string='Closing By')
    referal = fields.Char(string='Referal')
    tanggal_kontrak_ia = fields.Date(string="Tanggal Kontrak IA")
    mandays = fields.Integer(string='Mandays')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT 
                    ma.id AS id, 
                    ma.tanggal_kontrak_ia AS tanggal_kontrak_ia,
                    hk.sales AS sales,
                    hk.associate AS associate,
                    hk.closing_by AS closing_by,
                    hk.state AS state,
                    hk.category AS category,
                    hk.referal AS referal,
                    ma.mandays AS mandays
                FROM tsi_iso_mandays_app ma
                LEFT JOIN tsi_history_kontrak hk ON (
                    ma.tahapan_id = hk.id OR
                    ma.tahapan_id1 = hk.id OR
                    ma.tahapan_id2 = hk.id OR
                    ma.tahapan_id3 = hk.id OR
                    ma.tahapan_id4 = hk.id OR
                    ma.tahapan_id_re = hk.id
                )
                WHERE ma.tanggal_kontrak_ia IS NOT NULL
                ORDER BY ma.tanggal_kontrak_ia
            )
        """)

class HistoryKontrakPIC(models.Model):
    _name = 'history_kontrak.pic'
    _description = 'History Kontrak PIC'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    hiskon_id = fields.Many2one('tsi.history_kontrak', string="History Kontrak PIC", tracking=True)
    name_pic = fields.Many2one('res.partner', string="PIC", domain="[('is_company', '=', False)]", tracking=True)
    phone_pic = fields.Char(string="Phone", tracking=True)
    email_pic = fields.Char(string="Email", tracking=True)
    address_pic = fields.Char(string="Address", tracking=True)
    jabatan = fields.Char(string="Jabatan", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Partner", tracking=True)

    @api.model
    def create(self, vals):
        record = super(HistoryKontrakPIC, self).create(vals)
        
        # Get the related company (res.partner) from tsi.history_kontrak
        company = record.hiskon_id.partner_id  # Assuming `partner_id` is the company field in `tsi.history_kontrak`
        
        if company:
            # Create or update the corresponding ResPartnerContactClient record
            contact_client = self.env['res.partner.contact.client'].search([
                ('name_client', '=', record.name_pic.id),
                ('partner_id', '=', company.id)
            ])
            if contact_client:
                contact_client.write({
                    'phone_client': record.phone_pic,
                    'email_client': record.email_pic,
                    'address_client': record.address_pic,
                    'jabatan': record.jabatan,
                })
            else:
                self.env['res.partner.contact.client'].create({
                    'name_client': record.name_pic.id,
                    'phone_client': record.phone_pic,
                    'email_client': record.email_pic,
                    'address_client': record.address_pic,
                    'jabatan': record.jabatan,
                    'partner_id': company.id,
                })

        # Post message to the history contract
        record.hiskon_id.message_post(body=f"Created/Updated PIC: {record.name_pic.name}, Phone: {record.phone_pic}, Email: {record.email_pic}, Address: {record.address_pic}, Jabatan: {record.jabatan}")
        return record

    def write(self, vals):
        res = super(HistoryKontrakPIC, self).write(vals)
        for record in self:
            # Get the related company (res.partner) from tsi.history_kontrak
            company = record.hiskon_id.partner_id  # Assuming `partner_id` is the company field in `tsi.history_kontrak`

            if company:
                # Update the corresponding ResPartnerContactClient record
                contact_client = self.env['res.partner.contact.client'].search([
                    ('name_client', '=', record.name_pic.id),
                    ('partner_id', '=', company.id)
                ])
                if contact_client:
                    contact_client.write({
                        'phone_client': record.phone_pic,
                        'email_client': record.email_pic,
                        'address_client': record.address_pic,
                        'jabatan': record.jabatan,
                    })

            # Post message to the history contract
            record.hiskon_id.message_post(body=f"Updated PIC: {record.name_pic.name}, Phone: {record.phone_pic}, Email: {record.email_pic}, Address: {record.address_pic}, Jabatan: {record.jabatan}")
        return res

class HistoryKontrakPICWizard(models.TransientModel):
    _name = 'history_kontrak.pic.wizard'
    _description = 'PIC History Kontrak'

    pic_id = fields.Many2one('res.partner', string="PIC", domain="[('is_company', '=', False)]")
    phone_pic = fields.Char(string="Phone")
    email_pic = fields.Char(string="Email")
    address_pic = fields.Char(string="Address")
    jabatan = fields.Char(string="Jabatan")

    @api.onchange('pic_id')
    def _onchange_name_pic(self):
        if self.pic_id:
            self.address_pic = self.pic_id.office_address
            self.phone_pic = self.pic_id.phone
            self.email_pic = self.pic_id.email
            self.jabatan = self.pic_id.function
        else:
            self.address_pic = False
            self.phone_pic = False
            self.email_pic = False
            self.jabatan = False

    def action_save(self):
        # Retrieve the partner ID from the context
        partner_id = self.env.context.get('default_partner_id')
        
        if partner_id:
            # Get the partner record
            partner = self.env['res.partner'].browse(partner_id)
            
            # Update the partner record with data from the wizard
            if self.pic_id:
                self.pic_id.write({
                    'phone': self.phone_pic,
                    'email': self.email_pic,
                    'office_address': self.address_pic,
                    'function': self.jabatan,
                })
            
            # Create a new record in history_kontrak.pic
            self.env['history_kontrak.pic'].create({
                'hiskon_id': partner_id,  # Assuming partner_id is linked to history_kontrak
                'name_pic': self.pic_id.id,
                'phone_pic': self.phone_pic,
                'email_pic': self.email_pic,
                'address_pic': self.address_pic,
                'jabatan': self.jabatan,
                'partner_id': self.pic_id.id,
            })
            
        return {'type': 'ir.actions.act_window_close'}

class CRMAlasan(models.Model):
    _name           = 'crm.alasan'
    _description    = 'Alasan (CRM)'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)

# class LossAlasanWizard(models.TransientModel):
#     _name = 'loss.alasan.wizard'
#     _description = 'Loss Alasan Wizard'

#     def _get_default_standard(self):
#         return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

#     alasan              = fields.Many2one('crm.alasan', string="Alasan")
#     iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standard)
#     # line_ids            = fields.One2many('line.wizard.nilai', 'wizard_id', string='Audit Lines')

#     def confirm_loss(self):
#         active_ids = self.env.context.get('active_ids', [])
#         histories = self.env['tsi.history_kontrak'].browse(active_ids)
#         for history in histories:
#             history.action_loss(alasan=self.alasan.id)

# class SuspendAlasanWizard(models.TransientModel):
#     _name = 'suspend.alasan.wizard'
#     _description = 'Suspend Alasan Wizard'

#     def _get_default_standard(self):
#         return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

#     alasan              = fields.Many2one('crm.alasan', string="Alasan")
#     iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True,   default=_get_default_standard)

#     def confirm_suspend(self):
#         active_ids = self.env.context.get('active_ids', [])
#         histories = self.env['tsi.history_kontrak'].browse(active_ids)
#         for history in histories:
#             history.action_suspend(alasan=self.alasan.id)