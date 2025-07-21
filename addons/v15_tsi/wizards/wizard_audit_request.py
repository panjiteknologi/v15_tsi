from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

logger = logging.getLogger(__name__)

class WizardAuditRequest(models.TransientModel):
    _name = 'tsi.wizard_audit_request'
    _description = 'Wizard Audit Request'

    def _get_default_partner(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).partner_id

    def _get_default_tipe_pembayaran(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).tipe_pembayaran

    def _get_default_plan_of_audit_date(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).tgl_perkiraan_audit_selesai

    def _get_default_sales(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve']), ('sales', '!=', False)], order='id asc', limit=1).sales
    
    def _get_default_nomor_kontrak(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).no_kontrak

    def _get_default_iso_reference(self):
        return self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).iso_reference
    
    # def _get_default_lines_request(self):
    #     request = self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids'))])
    #     lines_request = request.mapped('lines_audit_request')
    #     return lines_request

    def _get_default_lines_request(self):
        
        requests = self.env['tsi.audit.request'].search([('id', 'in', self.env.context.get('active_ids'))])
        if requests:
            lines_request = requests.mapped('lines_audit_request')
            return lines_request
        return False

    def _get_default_standards(self):
        all_standards = self.env['tsi.audit.request'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])])
        standards = all_standards.mapped('iso_standard_ids')
        return standards
    
    # Method untuk mendapatkan default untuk is_amendment
    def _get_default_is_amendment(self):
        # Ambil nilai is_amendment dari tsi.audit.request
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            # Cari audit request yang aktif
            requests = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if requests:
                return requests.is_amendment
        # Default untuk kontrak baru adalah False
        return False

    # Method untuk mendapatkan default untuk contract_type
    def _get_default_contract_type(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            # Cari audit request yang aktif
            requests = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if requests:
                # Ambil contract_type dari audit request yang ditemukan
                contract_type = requests.contract_type
                if contract_type:
                    return contract_type
        # Jika tidak ada request yang aktif, anggap ini adalah kontrak baru
        return 'new'

    def _get_default_upload_npwp(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.upload_npwp
        return False

    def _get_default_file_name1(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.file_name1
        return False

    def _get_default_upload_contract(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.upload_contract
        return False

    def _get_default_file_name(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.file_name
        return False

    def _get_default_reference(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            return active_ids
        return []

    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)
    request_ids 	= fields.Many2many('audit_request.line', string='Lines Audit Request',  default=_get_default_lines_request)
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request',  default=_get_default_reference)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standards)
    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True, default=_get_default_iso_reference)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran', readonly=True, default=_get_default_tipe_pembayaran)
    sales               = fields.Many2one('res.users', string='Sales Person',store=True, readonly=True, default=_get_default_sales)
    no_kontrak          = fields.Char(string='Nomor Kontrak', default=_get_default_nomor_kontrak)
    is_amendment = fields.Boolean(string="Is Amendment Contract?", default=_get_default_is_amendment)
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract", default=_get_default_contract_type)
    upload_npwp = fields.Binary('Upload NPWP', default=_get_default_upload_npwp)
    file_name1 = fields.Char('Filename NPWP', tracking=True, default=_get_default_file_name1)
    upload_contract = fields.Binary('Upload Kontrak', default=_get_default_upload_contract)
    file_name = fields.Char('Filename', tracking=True, default=_get_default_file_name)
    tgl_perkiraan_audit_selesai = fields.Selection(
        selection=lambda self: self.env['tsi.audit.request'].fields_get()['tgl_perkiraan_audit_selesai']['selection'],
        string="Plan of audit date",
        default=_get_default_plan_of_audit_date
    )

    def send(self):

        # partner_associate = self.env['res.partner'].search([
        #     ('name', '=', self.associate_name.strip())
        # ], limit=1)

        # if not partner_associate and self.associate_name:
        #     partner_associate = self.env['res.partner'].create({
        #         'name': self.associate_name.strip(),
        #         'is_company': False,
        #         'company_type': 'person',
        #     })

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'reference_request_ids': [(6, 0, self.reference_request_ids.ids)],
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tipe_pembayaran': self.tipe_pembayaran,
            'iso_reference': self.iso_reference.id,
            'contract_type': self.contract_type,
            'nomor_kontrak': self.no_kontrak,
            'nomor_quotation': self.no_kontrak,
            'sales_person': self.sales.id if self.sales else self.env.user.id,
            'template_quotation': self.upload_contract,
            'file_name': self.file_name,
            'upload_npwp': self.upload_npwp,
            'file_namenpwp': self.file_name1,
            'tgl_perkiraan_audit_selesai': self.tgl_perkiraan_audit_selesai
        })

        for line in self.request_ids:
            product = line.product_id

            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': line.product_id.id,
                'audit_tahapan': line.audit_tahapan,
                'tahun': line.tahun,
                'price_unit': line.price,
            })

        # sale_order.action_confirm()
        sale_order.write({'state': 'sent'})

        audit_requests = self.env['tsi.audit.request'].search([
            ('id', 'in', self.env.context.get('active_ids'))
        ])
        audit_requests.write({'sale_order_id': sale_order.id})
        
        return True

class WizardAuditRequestISPO(models.TransientModel):
    _name = 'tsi.wizard_audit_request.ispo'
    _description = 'Wizard Audit Request ISPO'

    def _get_default_partner(self):
        return self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).partner_id

    def _get_default_tipe_pembayaran(self):
        return self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).tipe_pembayaran

    def _get_default_plan_of_audit_date(self):
        return self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).tgl_perkiraan_audit_selesai
    
    def _get_default_nomor_kontrak(self):
        return self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).no_kontrak

    def _get_default_ispo_reference(self):
        return self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])], limit=1).ispo_reference
    
    # def _get_default_lines_request(self):
    #     request = self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids'))])
    #     lines_request = request.mapped('lines_audit_request')
    #     return lines_request

    def _get_default_lines_request(self):
        
        requests = self.env['tsi.audit.request.ispo'].search([('id', 'in', self.env.context.get('active_ids'))])
        if requests:
            lines_request = requests.mapped('lines_audit_request')
            return lines_request
        return False

    def _get_default_standards(self):
        all_standards = self.env['tsi.audit.request.ispo'].search([('id','in',self.env.context.get('active_ids')),('state', 'in', ['request', 'approve'])])
        standards = all_standards.mapped('iso_standard_ids')
        return standards
    
    # Method untuk mendapatkan default untuk is_amendment
    def _get_default_is_amendment(self):
        # Ambil nilai is_amendment dari tsi.audit.request.ispo
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            # Cari audit request yang aktif
            requests = self.env['tsi.audit.request.ispo'].search([('id', 'in', active_ids)], limit=1)
            if requests:
                return requests.is_amendment
        # Default untuk kontrak baru adalah False
        return False

    # Method untuk mendapatkan default untuk contract_type
    def _get_default_contract_type(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            # Cari audit request yang aktif
            requests = self.env['tsi.audit.request.ispo'].search([('id', 'in', active_ids)], limit=1)
            if requests:
                # Ambil contract_type dari audit request yang ditemukan
                contract_type = requests.contract_type
                if contract_type:
                    return contract_type
        # Jika tidak ada request yang aktif, anggap ini adalah kontrak baru
        return 'new'

    def _get_default_upload_npwp(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request.ispo'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.upload_npwp
        return False

    def _get_default_file_name1(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request.ispo'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.file_name1
        return False

    def _get_default_upload_contract(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request.ispo'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.upload_contract
        return False

    def _get_default_file_name(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            request = self.env['tsi.audit.request.ispo'].search([('id', 'in', active_ids)], limit=1)
            if request:
                return request.file_name
        return False

    def _get_default_reference(self):
        active_ids = self.env.context.get('active_ids')
        if active_ids:
            return active_ids
        return []

    partner_id      = fields.Many2one('res.partner', 'Customer', readonly=True,   default=_get_default_partner)
    request_ids 	= fields.Many2many('audit_request_ispo.line', string='Lines Audit Request',  default=_get_default_lines_request)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_standards)
    ispo_reference       = fields.Many2one('tsi.ispo', string="Application Form", readonly=True, default=_get_default_ispo_reference)
    reference_request_ispo_ids = fields.Many2many('tsi.audit.request.ispo', string='Audit Request',  default=_get_default_reference)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran', readonly=True, default=_get_default_tipe_pembayaran)
    no_kontrak          = fields.Char(string='Nomor Kontrak', default=_get_default_nomor_kontrak)
    is_amendment = fields.Boolean(string="Is Amendment Contract?", default=_get_default_is_amendment)
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract", default=_get_default_contract_type)
    upload_npwp = fields.Binary('Upload NPWP', default=_get_default_upload_npwp)
    file_name1 = fields.Char('Filename NPWP', tracking=True, default=_get_default_file_name1)
    upload_contract = fields.Binary('Upload Kontrak', default=_get_default_upload_contract)
    file_name = fields.Char('Filename', tracking=True, default=_get_default_file_name)
    tgl_perkiraan_audit_selesai = fields.Selection(
        selection=lambda self: self.env['tsi.audit.request.ispo'].fields_get()['tgl_perkiraan_audit_selesai']['selection'],
        string="Plan of audit date",
        default=_get_default_plan_of_audit_date
    )

    def send(self):

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'reference_request_ispo_ids': [(6, 0, self.reference_request_ispo_ids.ids)],
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tipe_pembayaran': self.tipe_pembayaran,
            'ispo_reference': self.ispo_reference.id,
            'contract_type': self.contract_type,
            'nomor_kontrak': self.no_kontrak,
            'nomor_quotation': self.no_kontrak,
            'template_quotation': self.upload_contract,
            'file_name': self.file_name,
            'upload_npwp': self.upload_npwp,
            'file_namenpwp': self.file_name1,
            'tgl_perkiraan_audit_selesai': self.tgl_perkiraan_audit_selesai
        })

        for line in self.request_ids:
            product = line.product_id

            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': line.product_id.id,
                'audit_tahapan': line.audit_tahapan,
                'tahun': line.tahun,
                'price_unit': line.price,
            })

        # sale_order.action_confirm()
        sale_order.write({'state': 'sent'})

        audit_requests_ispo = self.env['tsi.audit.request.ispo'].search([
            ('id', 'in', self.env.context.get('active_ids'))
        ])
        audit_requests_ispo.write({'sale_order_id': sale_order.id})
        
        return True