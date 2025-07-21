from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, timedelta, date

_logger = logging.getLogger(__name__)

class WizardAudit(models.TransientModel):
    _name = 'tsi.wizard_audit'
    _description = 'Create Audit'

    def _get_default_partner(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).partner_id

    def _get_default_iso(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids')),],limit=1).iso_reference

    def _get_default_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).ispo_reference

    def _get_default_sales(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).sales_reference

    def _get_default_review(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).review_reference

    def _get_default_review_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).review_reference_ispo

    def _get_default_iso(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

    def _get_default_show_iso(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).show_iso_fields

    def _get_default_show_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).show_ispo_fields

    def _get_default_crm(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).id

    # audit_stage = fields.Selection([
    #                         ('surveilance1',     'Surveillance 1'),
    #                         ('surveilance2',     'Surveillance 2'),
    #                         ('surveilance3',     'Surveillance 3'),
    #                         ('surveilance4',     'Surveillance 4'),
    #                         ('recertification', 'Recertification'),
    #                     ], string='Audit Stage', required=True)

    cycle               = fields.Selection([
                            ('cycle1',     'Cycle 1'),
                            ('cycle2',     'Cycle 2'),
                            ('cycle3',     'Cycle 3'),
                        ], string='Cycle', tracking=True)

    cycle1              = fields.Selection([
                            ('surveilance1',     'Surveillance 1'),
                            ('surveilance2',     'Surveillance 2'),
                            ('recertification', 'Recertification 1'),
                        ], string='Audit Stage', tracking=True)

    cycle2              = fields.Selection([
                            ('surveilance3',     'Surveillance 3'),
                            ('surveilance4',     'Surveillance 4'),
                            ('recertification2', 'Recertification 2'),
                        ], string='Audit Stage', tracking=True)

    cycle3              = fields.Selection([
                            ('surveilance5',     'Surveillance 5'),
                            ('surveilance6',     'Surveillance 6'),
                            ('recertification3', 'Recertification 3'),
                        ], string='Audit Stage', tracking=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', default=_get_default_iso)

    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True,   default=_get_default_partner)
    invoicing_address   = fields.Char(string="Invoicing Address", )
    office_address      = fields.Char(string='Office Address')
    site_address        = fields.Char(string='Site Project Address')
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    telp                = fields.Char(string='Telp')
    email               = fields.Char(string='Email')
    website             = fields.Char(string='Website')
    cellular            = fields.Char(string='Cellular')
    scope               = fields.Char(string='Scope')
    boundaries          = fields.Char(string='Boundaries')
    number_site         = fields.Char(string='Number of Site')
    total_emp           = fields.Char(string='Total Employee')
    total_emp_site      = fields.Char(string='Total Employee Site Project')
    mandays             = fields.Char(string='Mandays')
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    is_amendment = fields.Boolean(string="Is Amendment Contract?")
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract")
    upload_contract        = fields.Binary('Upload Kontrak')
    # dokumen_sosialisasi        = fields.Binary('Organization Chart')
    file_name       = fields.Char('Filename', tracking=True)
    upload_npwp        = fields.Binary('Upload NPWP')
    file_name1       = fields.Char('Filename NPWP', tracking=True)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran', tracking=True)
    sales               = fields.Many2one('res.users', string='Sales Person',store=True)
    closing_by = fields.Selection([
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
    category = fields.Selection([
                ('bronze',  'Bronze'),
                ('silver',   'Silver'),
                ('gold', 'Gold')
                ], string='Category', store=True)
    pic_direct          = fields.Char(string='PIC Direct', tracking=True)
    email_direct        = fields.Char(string='Email Direct', tracking=True)
    phone_direct        = fields.Char(string='No Telp Direct', tracking=True)

    pic_konsultan1       = fields.Many2one('res.partner', string='PIC Konsultan', tracking=True, store=True)
    pic_konsultan       = fields.Char(string='PIC Konsultan', tracking=True)
    email_konsultan     = fields.Char(string='Email Konsultan', tracking=True)
    phone_konsultan     = fields.Char(string='No Telp Konsultan', tracking=True)

    note                = fields.Text(string='Note', tracking=True)

    # ISO 9001
    show_9001          = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_9001       = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_9001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_9001 = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 14001
    show_14001           = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_14001        = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_14001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_14001  = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 45001
    show_45001              = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_45001           = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_45001', string="IAF Code", domain="[('iso_standard_ids.name', 'in', ['ISO 9001:2015', ' ISO 14001:2015', 'ISO 45001:2018'])]")
    accreditation_45001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 37001
    show_37001              = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_37001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_37001           = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_37001', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # ISO 13485
    show_13485          = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_13485 = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_13485       = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_13485', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # ISO 22000
    show_22000            = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_22000   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_22000         = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_22000', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'ISO 22000:2018')]")

    # ISO 21000
    show_21000            = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_21000   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_21000         = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_21000', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # HACCP
    show_haccp            = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_haccp   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_haccp         = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_haccp', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'HACCP')]")

    # SMK
    show_smk            = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_smk   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_smk         = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_smk', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # GMP
    show_gmp            = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_gmp   = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_gmp         = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_gmp', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # ISO 27001
    show_27001             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_27001          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_27001', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_27001    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 27001 : 2022
    show_27001_2022             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_27001_2022          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_27001_2022', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_27001_2022    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 27701
    show_27701             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_27701          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_27701', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_27701    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 27017
    show_27017             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_27017          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_27017', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_27017    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 27018
    show_27018             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_27018          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_27018', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_27018    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 31000
    show_31000             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_31000          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_31000', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_31000    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 22301
    show_22301             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_22301          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_22301', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_22301    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 9994
    show_9994             = fields.Boolean(compute="_compute_show_fields", store=True)
    ea_code_9994          = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_9994', domain=[('name', '=', 'Not Applicable')], string="IAF Code")
    accreditation_9994    = fields.Many2one('tsi.iso.accreditation', string="Accreditation")

    # ISO 37301
    show_37301              = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_37301     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_37301           = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_37301', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # ISO 31001
    show_31001              = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_31001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_31001           = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_31001', domain=[('name', '=', 'Not Applicable')], string="IAF Code")

    # ISO 21001
    show_21001              = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_21001     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_21001           = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_21001', string="IAF Code", domain="[('iso_standard_ids.name', '=', 'ISO 21001:2018')]")

    # ISPO
    show_ispo              = fields.Boolean(compute="_compute_show_fields", store=True)
    accreditation_ispo     = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    ea_code_ispo           = fields.Many2many('tsi.ea_code', 'rel_wizard_audit_ea_ispo', string="IAF Code")

    line_ids    = fields.One2many('wizard.audit.line', 'wizard_id', string='Audit Lines')

    # Site Lines
    site_ids            = fields.One2many('wizard.site.line', 'wizard_site_id', string='Site Lines')
    site_ids_14001      = fields.One2many('wizard.site.line', 'wizard_site_id_14001', string='Site Lines')
    site_ids_45001      = fields.One2many('wizard.site.line', 'wizard_site_id_45001', string='Site Lines')
    site_ids_27001      = fields.One2many('wizard.site.line', 'wizard_site_id_27001', string='Site Lines')
    site_ids_27701      = fields.One2many('wizard.site.line', 'wizard_site_id_27701', string='Site Lines')
    site_ids_27017      = fields.One2many('wizard.site.line', 'wizard_site_id_27017', string='Site Lines')
    site_ids_27018      = fields.One2many('wizard.site.line', 'wizard_site_id_27018', string='Site Lines')
    site_ids_27001_2022 = fields.One2many('wizard.site.line', 'wizard_site_id_27001_2022', string='Site Lines')
    site_ids_haccp      = fields.One2many('wizard.site.line', 'wizard_site_id_haccp', string='Site Lines')
    site_ids_gmp        = fields.One2many('wizard.site.line', 'wizard_site_id_gmp', string='Site Lines')
    site_ids_22000      = fields.One2many('wizard.site.line', 'wizard_site_id_22000', string='Site Lines')
    site_ids_22301      = fields.One2many('wizard.site.line', 'wizard_site_id_22301', string='Site Lines')
    site_ids_31000      = fields.One2many('wizard.site.line', 'wizard_site_id_31000', string='Site Lines')
    site_ids_9994       = fields.One2many('wizard.site.line', 'wizard_site_id_9994', string='Site Lines')
    site_ids_37001      = fields.One2many('wizard.site.line', 'wizard_site_id_37001', string='Site Lines')
    site_ids_13485      = fields.One2many('wizard.site.line', 'wizard_site_id_13485', string='Site Lines')
    site_ids_smk        = fields.One2many('wizard.site.line', 'wizard_site_id_smk', string='Site Lines')
    site_ids_21000      = fields.One2many('wizard.site.line', 'wizard_site_id_21000', string='Site Lines')
    site_ids_37301      = fields.One2many('wizard.site.line', 'wizard_site_id_37301', string='Site Lines')
    site_ids_21001      = fields.One2many('wizard.site.line', 'wizard_site_id_21001', string='Site Lines')
    site_ids_31001      = fields.One2many('wizard.site.line', 'wizard_site_id_31001', string='Site Lines')

    site_ids_ispo      = fields.One2many('wizard.site.line', 'wizard_site_id_ispo', string='Site Lines')

    # Mandays Lines
    mandays_ids            = fields.One2many('wizard.mandays.line', 'wizard_mandays_id', string='Mandays Lines')
    mandays_ids_14001      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_14001', string='Mandays Lines')
    mandays_ids_45001      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_45001', string='Mandays Lines')
    mandays_ids_27001      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_27001', string='Mandays Lines')
    mandays_ids_27701      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_27701', string='Mandays Lines')
    mandays_ids_27017      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_27017', string='Mandays Lines')
    mandays_ids_27018      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_27018', string='Mandays Lines')
    mandays_ids_27001_2022 = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_27001_2022', string='Mandays Lines')
    mandays_ids_haccp      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_haccp', string='Mandays Lines')
    mandays_ids_gmp        = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_gmp', string='Mandays Lines')
    mandays_ids_22000      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_22000', string='Mandays Lines')
    mandays_ids_22301      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_22301', string='Mandays Lines')
    mandays_ids_31000      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_31000', string='Mandays Lines')
    mandays_ids_9994       = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_9994', string='Mandays Lines')
    mandays_ids_37001      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_37001', string='Mandays Lines')
    mandays_ids_13485      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_13485', string='Mandays Lines')
    mandays_ids_smk        = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_smk', string='Mandays Lines')
    mandays_ids_21000      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_21000', string='Mandays Lines')
    mandays_ids_37301      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_37301', string='Mandays Lines')
    mandays_ids_21001      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_21001', string='Mandays Lines')
    mandays_ids_31001      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_31001', string='Mandays Lines')

    mandays_ids_ispo      = fields.One2many('wizard.mandays.line', 'wizard_mandays_id_ispo', string='Mandays Lines')

    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True, default=_get_default_iso)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True, default=_get_default_sales)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True, default=_get_default_review)
    crm_reference       = fields.Many2one('tsi.history_kontrak', string="CRM Reference", readonly=True, default=_get_default_crm)
    ispo_reference       = fields.Many2one('tsi.ispo', string="Application Form", readonly=True, default=_get_default_ispo)
    review_reference_ispo    = fields.Many2many('tsi.ispo.review', string="Review Reference", readonly=True, default=_get_default_review_ispo)

    show_iso_fields = fields.Boolean(readonly=True, default=_get_default_show_iso, store=False)
    show_ispo_fields = fields.Boolean(readonly=True, default=_get_default_show_ispo, store=False)

    tgl_perkiraan_selesai = fields.Date(string="Plan of audit date",store=True)
    tgl_perkiraan_audit_selesai = fields.Selection(
        selection=lambda self: self.get_end_of_month_choices(),
        string="Plan of audit date"
    )

    @api.model
    def default_get(self, fields):
        res = super(WizardAudit, self).default_get(fields)
        res['crm_reference'] = self.env.context.get('default_crm_reference')
        return res

    @api.depends('iso_standard_ids')
    def _compute_show_fields(self):
        for obj in self:
            # Reset all show fields
            obj.show_14001 = obj.show_45001 = obj.show_27001 = obj.show_27701 = False
            obj.show_27017 = obj.show_27018 = obj.show_27001_2022 = obj.show_haccp = False
            obj.show_22000 = obj.show_22301 = obj.show_31000 = obj.show_37001 = False
            obj.show_13485 = obj.show_smk = obj.show_21000 = obj.show_37301 = False
            obj.show_9994 = obj.show_9001 = obj.show_31001 = obj.show_21001 = obj.show_gmp = obj.show_ispo = False  

            for standard in obj.iso_standard_ids:
                if standard.name == 'ISO 14001:2015':
                    obj.show_14001 = True
                if standard.name == 'ISO 45001:2018':
                    obj.show_45001 = True
                if standard.name == 'ISO/IEC 27001:2013':
                    obj.show_27001 = True
                if standard.name == 'ISO/IEC 27001:2022':
                    obj.show_27001_2022 = True
                if standard.name == 'ISO/IEC 27701:2019':
                    obj.show_27701 = True
                if standard.name == 'ISO/IEC 27017:2015':
                    obj.show_27017 = True
                if standard.name == 'ISO/IEC 27018:2019':
                    obj.show_27018 = True
                if standard.name == 'ISO 22000:2018':
                    obj.show_22000 = True
                if standard.name == 'ISO 22301:2019':
                    obj.show_22301 = True
                if standard.name == 'HACCP':
                    obj.show_haccp = True
                if standard.name == 'GMP':
                    obj.show_gmp = True
                if standard.name == 'ISO 31000:2018':
                    obj.show_31000 = True
                if standard.name == 'ISO 13485:2016':
                    obj.show_13485 = True
                if standard.name == 'ISO 37301:2021':
                    obj.show_37301 = True
                if standard.name == 'ISO 9994:2018':
                    obj.show_9994 = True
                if standard.name == 'ISO 37001:2016':
                    obj.show_37001 = True
                if standard.name == 'SMK3':
                    obj.show_smk = True
                if standard.name == 'ISO 21000:2018':
                    obj.show_21000 = True
                if standard.name == 'ISO 21001:2018':
                    obj.show_21001 = True
                if standard.name == 'ISO 31001:2018':
                    obj.show_31001 = True   
                if standard.name == 'ISO 9001:2015':
                    obj.show_9001 = True
                if standard.name == 'ISPO':
                    obj.show_ispo = True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Isi otomatis beberapa field dari partner ke sale.order
            self.office_address = self.partner_id.office_address
            self.invoicing_address = self.partner_id.invoice_address
            self.email = self.partner_id.email
            self.telp = self.partner_id.phone
            self.website = self.partner_id.website
            self.cellular = self.partner_id.mobile
            # self.scope = self.partner_id.scope
            # self.boundaries = self.partner_id.boundaries
            self.number_site = self.partner_id.number_site
            self.total_emp = self.partner_id.total_emp

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

    # @api.onchange('partner_id')
    # def on_change_state(self):
    #     for record in self:
    #         if record.partner_id:
    #             record.office_address = record.partner_id.street

    def send(self):
        if self.partner_id:
            original_data = self.env['tsi.history_kontrak'].search([('id', 'in', self.env.context.get('active_ids'))], limit=1)

            changes_log = []

            updates = {}
            if self.office_address != original_data.partner_id.office_address:
                updates['office_address'] = self.office_address
                changes_log.append(f"Office Address from {original_data.partner_id.office_address} to {self.office_address}")
            if self.invoicing_address != original_data.partner_id.invoice_address:
                updates['invoice_address'] = self.invoicing_address
                changes_log.append(f"Invoicing Address from {original_data.partner_id.invoice_address} to {self.invoicing_address}")
            if self.email != original_data.partner_id.email:
                updates['email'] = self.email
                changes_log.append(f"Email from {original_data.partner_id.email} to {self.email}")
            if self.telp != original_data.partner_id.phone:
                updates['phone'] = self.telp
                changes_log.append(f"Phone from {original_data.partner_id.phone} to {self.telp}")
            if self.website != original_data.partner_id.website:
                updates['website'] = self.website
                changes_log.append(f"Website from {original_data.partner_id.website} to {self.website}")
            if self.cellular != original_data.partner_id.mobile:
                updates['mobile'] = self.cellular
                changes_log.append(f"Cellular from {original_data.partner_id.mobile} to {self.cellular}")
            if self.scope != original_data.partner_id.scope:
                updates['scope'] = self.scope
                changes_log.append(f"Scope from {original_data.partner_id.scope} to {self.scope}")
            if self.boundaries != original_data.partner_id.boundaries:
                updates['boundaries'] = self.boundaries
                changes_log.append(f"Boundaries from {original_data.partner_id.boundaries} to {self.boundaries}")
            if self.number_site != original_data.partner_id.number_site:
                updates['number_site'] = self.number_site
                changes_log.append(f"Number of Sites from {original_data.partner_id.number_site} to {self.number_site}")
            # if self.total_emp != original_data.partner_id.total_emp:
            #     updates['total_emp'] = self.total_emp
            #     changes_log.append(f"Total Employees from {original_data.partner_id.total_emp} to {self.total_emp}")

            if updates:
                self.partner_id.write(updates)

            for iso_standard in self.iso_standard_ids:
                audit_request_data = {
                    'cycle': self.cycle,
                    'audit_stage': self.cycle1,
                    'audit_stage2': self.cycle2,
                    'audit_stage3': self.cycle3,
                    'tgl_perkiraan_audit_selesai': self.tgl_perkiraan_audit_selesai,
                    'iso_standard_ids': [(6, 0, [iso_standard.id])],
                    'partner_id': self.partner_id.id,
                    'office_address': self.office_address,
                    'site_address': self.site_address,
                    'invoicing_address': self.invoicing_address,
                    'sales': self.sales.id,
                    'telp': self.telp,
                    'email': self.email,
                    'website': self.website,
                    'cellular': self.cellular,
                    'scope': self.scope,
                    'boundaries': self.boundaries,
                    'number_site': self.number_site,
                    'no_kontrak': self.no_kontrak,
                    'total_emp': self.total_emp,
                    'total_emp_site': self.total_emp_site,
                    'mandays': self.mandays,
                    'reference': self.crm_reference.id,
                    'is_amendment': self.is_amendment,
                    'contract_type': self.contract_type,
                    'upload_contract': self.upload_contract,
                    'file_name': self.file_name,
                    'tipe_pembayaran': self.tipe_pembayaran,
                    'upload_npwp': self.upload_npwp,
                    'file_name1': self.file_name1,
                    'issue_date': fields.Date.today(),
                    'closing_by': self.closing_by,
                    'category': self.category,
                    'pic_direct': self.pic_direct,
                    'email_direct': self.email_direct,
                    'phone_direct': self.phone_direct,
                    'pic_konsultan1': self.pic_konsultan1.id,
                    'email_konsultan': self.email_konsultan,
                    'phone_konsultan': self.phone_konsultan,
                    'note': self.note,
                    'user_id': self.env.user.id,
                    'phone_konsultan': self.phone_konsultan,
                    'transport_by': self.transport_by,
                    'hotel_by': self.hotel_by,
                    'tipe_klien_transport': self.tipe_klien_transport,
                    'tipe_klien_hotel': self.tipe_klien_hotel,
                    'pic_crm': self.pic_crm,
                }

                if iso_standard.name == "ISPO":
                    audit_request_data.update({
                        'show_ispo': True,
                        'ea_code_ispo': [(6, 0, self.ea_code_ispo.ids)],
                        'accreditation_ispo': self.accreditation_ispo.id,
                        'ispo_reference': self.ispo_reference.id, 
                        'review_reference_ispo': self.review_reference_ispo,
                    })
                    audit_form = self.env['tsi.audit.request.ispo'].sudo(self.env.user).create(audit_request_data)
                else:
                    standard_field_map = {
                        "ISO 9001:2015": "9001",
                        "ISO 14001:2015": "14001",
                        "ISO 45001:2018": "45001",
                        "ISO 37001:2016": "37001",
                        "ISO 13485:2016": "13485",
                        "SMK3": "smk",
                        "ISO 22000:2018": "22000",
                        "ISO 21000:2018": "21000",
                        "GMP": "gmp",
                        "HACCP": "haccp",
                        "ISO/IEC 27001:2013": "27001",
                        "ISO/IEC 27001:2022": "27001_2022",
                        "ISO/IEC 27701:2019": "27701",
                        "ISO/IEC 27017:2015": "27017",
                        "ISO/IEC 27018:2019": "27018",
                        "ISO 31000:2018": "31000",
                        "ISO 22301:2019": "22301",
                        "ISO 9994:2018": "9994",
                        "ISO 37301:2021": "37301",
                        "ISO 31001:2018": "31001",
                        "ISO 21001:2018": "21001",
                    }
                    if iso_standard.name in standard_field_map:
                        key = standard_field_map[iso_standard.name]
                        audit_request_data.update({
                            f'show_{key}': True,
                            f'ea_code_{key}': [(6, 0, getattr(self, f'ea_code_{key}').ids)],
                            f'accreditation_{key}': getattr(self, f'accreditation_{key}').id,
                        })
                    audit_request_data.update({
                        'iso_reference': self.iso_reference.id,
                        'review_reference': self.review_reference,
                    })
                    audit_form = self.env['tsi.audit.request'].sudo(self.env.user).create(audit_request_data)
                
                product = self.env['product.product'].search([('name', 'ilike', iso_standard.name)], limit=1)
                if not product:
                    product = self.env['product.product'].create({
                        'name': iso_standard.name,
                        'type': 'service',
                        'list_price': 0.0,
                    })
                
                specific_lines = self.line_ids.filtered(lambda l: l.product_id == product)
                for line in specific_lines:
                    price_value = line.price_baru if line.price_baru else line.price_lama
                    line_data = {
                        'product_id': product.id,
                        'audit_tahapan': line.audit_tahapan,
                        'price': price_value,
                        'up_value': line.up_value,
                        'loss_value': line.loss_value,
                        'tahun': line.tahun,
                        'fee': line.fee,
                        'percentage': line.percentage,
                        'reference_id': audit_form.id
                    }
                    if iso_standard.name == "ISPO":
                        self.env['audit_request_ispo.line'].create(line_data)
                    else:
                        self.env['audit_request.line'].create(line_data)
                
                for site in self.site_ids:
                    site_partner = self.env['tsi.site_partner'].search([
                        ('partner_id', '=', self.partner_id.id),
                        ('jenis', '=', site.tipe_site)
                    ], limit=1)
                    if site_partner:
                        site_partner.write({
                            'alamat': site.address,
                            'jumlah_karyawan': site.total_emp,
                            'effective_emp': site.effective_emp,
                        })
                    else:
                        self.env['tsi.site_partner'].create({
                            'partner_id': self.partner_id.id,
                            'jenis': site.tipe_site,
                            'alamat': site.address,
                            'jumlah_karyawan': site.total_emp,
                            'effective_emp': site.effective_emp,
                        })
                
                if changes_log:
                    message = '\n'.join(changes_log)
                    audit_form.message_post(body=f"Change :\n{message}")

            partner_name = self.partner_id.name or "Customer"

            # Menentukan apakah ISO atau ISPO
            if any(iso_standard.name == "ISPO" for iso_standard in self.iso_standard_ids):
                message = f"{partner_name} berhasil ke Audit Request ISPO!"
            else:
                message = f"{partner_name} berhasil ke Audit Request ISO!"

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Sukses!',
                    'message': message,
                    'sticky': False,
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'}
                }
            }

class WizardAuditLine(models.TransientModel):
    _name = 'wizard.audit.line'
    _description = 'Wizard Audit Line'

    wizard_id = fields.Many2one('tsi.wizard_audit', string='Wizard', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
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
    price_lama = fields.Float(string='Oldest Price')
    price_baru = fields.Float(string='Latest Price')
    up_value = fields.Float(string='Up Value', compute='_compute_value_difference', store=True)
    loss_value = fields.Float(string='Loss Value', compute='_compute_value_difference', store=True)
    tahun = fields.Char(string='Tahun')
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)

    @api.depends('price_baru', 'fee')
    def _compute_percentage(self):
        for record in self:
            if record.price_baru > record.fee:
                record.percentage = record.fee / (record.price_baru - record.fee)
            else:
                record.percentage = 0

    @api.depends('price_baru', 'price_lama')
    def _compute_value_difference(self):
        for record in self:
            if record.price_baru and record.price_lama:
                if record.price_baru > record.price_lama:
                    record.up_value = record.price_baru - record.price_lama
                    record.loss_value = 0.0
                elif record.price_baru < record.price_lama:
                    record.loss_value = record.price_lama - record.price_baru
                    record.up_value = 0.0
                else:
                    record.up_value = 0.0
                    record.loss_value = 0.0
            else:
                record.up_value = 0.0
                record.loss_value = 0.0

class WizardSiteLine(models.TransientModel):
    _name = 'wizard.site.line'
    _description = 'Wizard Site Line'

    wizard_site_id            = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_14001      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_45001      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_27001      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_27701      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_27017      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_27018      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_27001_2022 = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_haccp      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_gmp        = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_22000      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_22301      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_31000      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_9994       = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_37001      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_13485      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_smk        = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_21000      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_37301      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_21001      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')
    wizard_site_id_31001      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')

    wizard_site_id_ispo      = fields.Many2one('tsi.wizard_audit', string='Wizard Site', ondelete='cascade')

    tipe_site       = fields.Char('Type(HO, Factory etc)', tracking=True) 
    address         = fields.Char('Address', tracking=True) 
    effective_emp   = fields.Char('Total No. of Effective Employees', tracking=True) 
    total_emp       = fields.Char(string='Total No. of All Employees', tracking=True)

class WizardMandaysLine(models.TransientModel):
    _name = 'wizard.mandays.line'
    _description = 'Wizard Mandays Line'

    wizard_mandays_id               = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_14001         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_45001         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_27001         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_27701         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_27017         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_27018         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_27001_2022    = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_haccp         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_gmp           = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_22000         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_22301         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_31000         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_9994          = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_37001         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_13485         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_smk           = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_21000         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_37301         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_21001         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')
    wizard_mandays_id_31001         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')

    wizard_mandays_id_ispo         = fields.Many2one('tsi.wizard_audit', string='Wizard Mandays', ondelete='cascade')

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