from odoo import models, fields, api, _
import odoo
from odoo.http import request

from datetime import datetime
from datetime import timedelta
from odoo import fields

import logging
_logger = logging.getLogger(__name__)

class PengajuanMarketing(models.Model):
    _name           = "tsi.pengajuan.marketing"
    _description    = "Pengajuan Fee Marketing"
    _order          = 'id DESC'
    _inherit        = ["mail.thread", "mail.activity.mixin"]

    user_id = fields.Many2one('res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user, domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    name = fields.Char(string="Document No", required=True, readonly=True, tracking=True, default='New')
    issue_date = fields.Date(string="Issue Date", default=fields.Date.today, tracking=True, store=True)
    sales_person = fields.Many2one('res.users', string='Sales Person',store=True, readonly=False, tracking=True)
    customer = fields.Many2one('res.partner', string="Klien", domain="[('is_company', '=', True)]", tracking=True)
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True, domain="[('standard', 'in', ['iso'])]")
    tahap_audit = fields.Selection([
                    ('initial_audit',    'Initial Audit'),
                    ('surveilance1',     'Surveillance 1'),
                    ('surveilance2',     'Surveillance 2'),
                    ('surveilance3',     'Surveillance 3'),
                    ('surveilance4',     'Surveillance 4'),
                    ('recertification', 'Recertification'),
                ], string='Tahap Audit', tracking=True, store=True)
    tanggal_pelunasan = fields.Date(string="Tanggal Pelunasan", tracking=True, store=True)
    nilai_bersih = fields.Float(string='Nilai Bersih', tracking=True, store=True)
    formatted_nilai_bersih = fields.Char(string="Nilai Bersih (Format)", compute='_compute_formatted_nilai_bersih')
    fee_marketing = fields.Selection([
                    ('0%',     '0%'),
                    ('2%',     '2%'),
                    ('3%',     '3%'),
                    ('4%',     '4%'),
                    ('5%',     '5%'),
                    ('6%',     '6%'),
                    ('7%',     '7%'),
                    ('8%',     '8%'),
                    ('9%',     '9%'),
                    ('10%',    '10%'),
                ], string='Fee Marketing', tracking=True, store=True)
    total_fee_marketing = fields.Float(string='Total Fee Marketing', tracking=True, store=True, compute='_compute_total_fee_marketing')
    formatted_total_fee_marketing = fields.Char(string="Total Fee Marketing (Format)", compute='_compute_formatted_total_fee_marketing')
    currency_id = fields.Many2one('res.currency', string='Currency')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reject', 'Reject'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ], string='Status', tracking=True, default='draft')
    note = fields.Text(string='Peraturan Fee Marketing', tracking=True)
    standard_names = fields.Char(string='Standard Names', compute='_compute_standard_names', store=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tsi.pengajuan.marketing') or 'New'
        return super(PengajuanMarketing, self).create(vals)

    @api.depends('iso_standard_ids')
    def _compute_standard_names(self):
        for record in self:
            record.standard_names = ', '.join(record.iso_standard_ids.mapped('name'))

    def format_total_fee_marketing(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('total_fee_marketing')
    def _compute_formatted_total_fee_marketing(self):
        for rec in self:
            rec.formatted_total_fee_marketing = self.format_total_fee_marketing(rec.total_fee_marketing)

    def format_nilai_bersih(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('nilai_bersih')
    def _compute_formatted_nilai_bersih(self):
        for rec in self:
            rec.formatted_nilai_bersih = self.format_nilai_bersih(rec.nilai_bersih)

    @api.depends('nilai_bersih', 'fee_marketing')
    def _compute_total_fee_marketing(self):
        for rec in self:
            if rec.nilai_bersih and rec.fee_marketing:
                # Ubah '5%' menjadi 0.05
                persen = float(rec.fee_marketing.strip('%')) / 100
                rec.total_fee_marketing = rec.nilai_bersih * persen
            else:
                rec.total_fee_marketing = 0.0   

    def action_done(self):
        self.write({'state': 'done'})

    def action_reject(self):
        self.write({'state': 'reject'})

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

            PermintaanDana = self.env['tsi.permintaan.dana']
            PermintaanDanaLine = self.env['tsi.permintaan.dana.line']
            today = fields.Date.context_today(rec)
            seven_days_ago = today - timedelta(days=7)

            # Nama jenis permintaan ini
            jenis_permintaan = 'Permintaan Fee Marketing'

            # Cek apakah sudah ada permintaan dana dengan line yang cocok (ket & tanggal dalam 7 hari)
            existing_request = PermintaanDana.search([
                ('issue_date', '>=', seven_days_ago),
                ('lines.ket', '=', jenis_permintaan),
            ], limit=1)

            # Data untuk line baru
            line_vals = {
                'ket': jenis_permintaan,
                'customer': rec.customer.id,
                'nominal': rec.total_fee_marketing,
                'state': 'draft',
            }

            if existing_request:
                # Jika sudah ada, tambahkan line baru ke record tersebut
                line_vals['permintaan_dana_id'] = existing_request.id
                PermintaanDanaLine.create(line_vals)
            else:
                # Jika tidak ada, buat record permintaan dana baru beserta line-nya
                new_request = PermintaanDana.create({
                    'issue_date': today,
                    'lines': [(0, 0, line_vals)],
                })

class PerjalananDinas(models.Model):
    _name           = "tsi.perjalanan.dinas"
    _description    = "Perjalanan Dinas"
    _order          = 'id DESC'
    _rec_name       = 'customer'
    _inherit        = ["mail.thread", "mail.activity.mixin"]

    user_id = fields.Many2one('res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user, domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    # name = fields.Char(string="Document No", required=True, readonly=True, tracking=True, default='New')
    customer = fields.Many2one('res.partner', string="Klien", domain="[('is_company', '=', True)]", tracking=True)
    # nama_auditor = fields.Many2one('mandays.auditor', string='Nama Auditor',store=True, readonly=False, tracking=True)
    auditor = fields.Many2one('mandays.auditor', string='Nama Auditor',store=True, readonly=False, tracking=True)
    jabatan      = fields.Selection([
                    ('operation_ict',     'Operation ICT'),
                    ('operation_xms',     'Operation XMS'),
                ], string='Jabatan', tracking=True, store=True)
    tanggal      = fields.Date(string="Tanggal", tracking=True, store=True)
    tujuan_perjalanan = fields.Char(string='Tujuan Perjalanan Dinas', tracking=True, store=True)
    lama_tugas = fields.Char(string='Lama Bertugas', tracking=True, store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('reject', 'Reject'),
        ('approved', 'Approved'),
        ('done', 'Done'),
        ], string='Status', tracking=True, default='draft')

    lines = fields.One2many('tsi.perjalanan.dinas.line', 'perjalanan_id', string='Detail Biaya')

    total_jumlah = fields.Float(string='Total', compute='_compute_total_jumlah', store=True)

    formatted_total_jumlah = fields.Char(string="Total (Format)", compute='_compute_formatted_total_jumlah')

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['lines'] = [
            (0, 0, {'nama': 'Transport'}),
            (0, 0, {'nama': 'Akomodasi'}),
            (0, 0, {'nama': 'Tunjangan Dinas', 'biaya': 150000}),
            (0, 0, {'nama': 'Tunjangan Lain (MANDAYS)'}),
        ]
        return res

    def format_total_jumlah(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('total_jumlah')
    def _compute_formatted_total_jumlah(self):
        for rec in self:
            rec.formatted_total_jumlah = self.format_total_jumlah(rec.total_jumlah)

    @api.depends('lines.jumlah')
    def _compute_total_jumlah(self):
        for rec in self:
            rec.total_jumlah = sum(rec.lines.mapped('jumlah'))

    def action_done(self):
        self.write({'state': 'done'})

    def action_reject(self):
        self.write({'state': 'reject'})

    def action_approved(self):
        for rec in self:
            rec.state = 'approved'

            PermintaanDana = self.env['tsi.permintaan.dana']
            PermintaanDanaLine = self.env['tsi.permintaan.dana.line']
            today = fields.Date.context_today(rec)
            seven_days_ago = today - timedelta(days=7)

            # Nama jenis permintaan ini
            jenis_permintaan = 'Perjalanan Dinas'

            # Cek apakah sudah ada permintaan dana dengan line yang cocok (ket & tanggal dalam 7 hari)
            existing_request = PermintaanDana.search([
                ('issue_date', '>=', seven_days_ago),
                ('lines.ket', '=', jenis_permintaan),
            ], limit=1)

            # Data untuk line baru
            line_vals = {
                'ket': jenis_permintaan,
                'customer': rec.customer.id,
                'nominal': rec.total_jumlah,
                'state': 'draft',
            }

            if existing_request:
                # Jika sudah ada, tambahkan line baru ke record tersebut
                line_vals['permintaan_dana_id'] = existing_request.id
                PermintaanDanaLine.create(line_vals)
            else:
                # Jika tidak ada, buat record permintaan dana baru beserta line-nya
                new_request = PermintaanDana.create({
                    'issue_date': today,
                    'lines': [(0, 0, line_vals)],
                })

class PerjalananDinasLine(models.Model):
    _name = 'tsi.perjalanan.dinas.line'
    _description = 'Detail Biaya Perjalanan Dinas'

    perjalanan_id = fields.Many2one('tsi.perjalanan.dinas', string='Perjalanan Dinas', ondelete='cascade')
    nama = fields.Char(string='Nama')
    uraian = fields.Text(string='Uraian')
    biaya = fields.Float(string='Biaya')
    hari = fields.Float(string='Hari')
    jumlah = fields.Float(string='Jumlah', compute='_compute_jumlah', store=True)

    formatted_biaya = fields.Char(string="Total Biaya (Format)", compute='_compute_formatted_biaya')
    formatted_hari = fields.Char(string="Total Hari (Format)", compute='_compute_formatted_hari')
    formatted_jumlah = fields.Char(string="Total Jumlah (Format)", compute='_compute_formatted_jumlah')

    def format_jumlah(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('jumlah')
    def _compute_formatted_jumlah(self):
        for rec in self:
            rec.formatted_jumlah = self.format_jumlah(rec.jumlah)

    def format_hari(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('hari')
    def _compute_formatted_hari(self):
        for rec in self:
            rec.formatted_hari = self.format_hari(rec.hari)

    def format_biaya(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('biaya')
    def _compute_formatted_biaya(self):
        for rec in self:
            rec.formatted_biaya = self.format_biaya(rec.biaya)

    @api.depends('biaya', 'hari')
    def _compute_jumlah(self):
        for line in self:
            line.jumlah = line.biaya * line.hari

class PengajuanMandays(models.Model):
    _name           = "tsi.pengajuan.mandays"
    _description    = "Pengajuan Mandays"
    _order          = 'id DESC'
    _rec_name       = 'auditor'
    _inherit        = ["mail.thread", "mail.activity.mixin"]

    user_id = fields.Many2one('res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user, domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    name = fields.Char(string="Document No", required=True, readonly=True, tracking=True, default='New')
    issue_date = fields.Date(string="Issue Date", default=fields.Date.today, tracking=True, store=True)
    auditor = fields.Many2one('mandays.auditor', string='Nama Auditor',store=True, readonly=False, tracking=True)
    total_jumlah = fields.Float(string='Total', compute='_compute_total_jumlah', store=True)

    lines = fields.One2many('tsi.pengajuan.mandays.line', 'mandays_id', string='Uraian Kebutuhan')

    formatted_total_jumlah = fields.Char(string="Total (Format)", compute='_compute_formatted_total_jumlah')

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('reject', 'Reject'),
    #     ('approved', 'Approved'),
    #     ('done', 'Done'),
    #     ], string='Status', tracking=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tsi.pengajuan.mandays') or 'New'
        return super(PengajuanMandays, self).create(vals)

    def format_total_jumlah(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('total_jumlah')
    def _compute_formatted_total_jumlah(self):
        for rec in self:
            rec.formatted_total_jumlah = self.format_total_jumlah(rec.total_jumlah)

    @api.depends('lines.jumlah')
    def _compute_total_jumlah(self):
        for rec in self:
            rec.total_jumlah = sum(rec.lines.mapped('jumlah'))

class PengajuanMandaysLine(models.Model):
    _name           = "tsi.pengajuan.mandays.line"
    _description    = "Pengajuan Mandays Line"

    mandays_id = fields.Many2one('tsi.pengajuan.mandays', string='Pengajuan Mandays', ondelete='cascade')
    customer = fields.Many2one('res.partner', string="Klien", domain="[('is_company', '=', True)]", tracking=True)
    audit_date   = fields.Date(string='Tanggal Audit', tracking=True)
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    audit_type  = fields.Selection([
                    ('Stage-01',     'ST1'),
                    ('Stage-02', 'ST2'),
                    ('surveilance1',    'S1'),
                    ('surveilance2',    'S2'),
                    ('recertification',    'RC'),
                ], tracking=True)
    volume       = fields.Char(string="Volume", tracking=True)
    satuan       = fields.Char(string="Satuan", tracking=True)
    biaya_satuan = fields.Float(string='Biaya Satuan', related="mandays_id.auditor.harga_mandays", readonly=False, tracking=True)
    jumlah       = fields.Float(string='Jumlah', compute="_compute_jumlah", store=True, tracking=True)

    formatted_biaya_satuan = fields.Char(string="Total (Format)", compute='_compute_formatted_biaya_satuan')
    formatted_jumlah = fields.Char(string="Total (Format)", compute='_compute_formatted_jumlah')
    standard_names = fields.Char(string='Standard Names', compute='_compute_standard_names', store=True)

    @api.depends('iso_standard_ids')
    def _compute_standard_names(self):
        for record in self:
            record.standard_names = ', '.join(record.iso_standard_ids.mapped('name'))

    def format_jumlah(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('jumlah')
    def _compute_formatted_jumlah(self):
        for rec in self:
            rec.formatted_jumlah = self.format_jumlah(rec.jumlah)

    def format_biaya_satuan(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('biaya_satuan')
    def _compute_formatted_biaya_satuan(self):
        for rec in self:
            rec.formatted_biaya_satuan = self.format_biaya_satuan(rec.biaya_satuan)

    @api.depends('biaya_satuan', 'volume')
    def _compute_jumlah(self):
        for rec in self:
            try:
                volume_float = float(rec.volume) if rec.volume else 0.0
            except ValueError:
                volume_float = 0.0
            rec.jumlah = rec.biaya_satuan * volume_float

class PermintaanDana(models.Model):
    _name           = "tsi.permintaan.dana"
    _description    = "Permintaan Dana"
    _order          = 'id DESC'
    _inherit        = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Document No", required=True, readonly=True, tracking=True, default='New')
    issue_date = fields.Date(string="Issue Date", default=fields.Date.today, tracking=True, store=True)
    total_nominal = fields.Float(string='Total', compute='_compute_total_nominal', store=True)

    lines = fields.One2many('tsi.permintaan.dana.line', 'permintaan_dana_id', string='Detail Permintaan Dana')

    formatted_total_nominal = fields.Char(string="Total (Format)", compute='_compute_formatted_total_nominal')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tsi.permintaan.dana') or 'New'
        return super(PermintaanDana, self).create(vals)

    def format_total_nominal(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('total_nominal')
    def _compute_formatted_total_nominal(self):
        for rec in self:
            rec.formatted_total_nominal = self.format_total_nominal(rec.total_nominal)

    def move_expired_hold_lines(self):
        PermintaanDana = self.env['tsi.permintaan.dana']
        PermintaanDanaLine = self.env['tsi.permintaan.dana.line']

        all_requests = PermintaanDana.search([])

        for req in all_requests:
            expired_date = req.issue_date + timedelta(days=7)

            for line in req.lines:
                if line.state != 'hold':
                    continue

                # Sudah lewat 7 hari dari issue_date parent
                if fields.Date.today() < expired_date:
                    continue

                future_req = PermintaanDana.search([('issue_date', '=', expired_date)], limit=1)

                if not future_req:
                    future_req = PermintaanDana.create({
                        'issue_date': expired_date,
                        'lines': [],
                    })

                PermintaanDanaLine.create({
                    'permintaan_dana_id': future_req.id,
                    'ket': line.ket,
                    'customer': line.customer.id,
                    'nominal': line.nominal,
                    'note': line.note,
                    'state': 'draft',
                })

                # Hapus line lama
                line.unlink()

    @api.depends('lines.nominal')
    def _compute_total_nominal(self):
        for rec in self:
            rec.total_nominal = sum(rec.lines.mapped('nominal'))

class PermintaanDanaLine(models.Model):
    _name = 'tsi.permintaan.dana.line'
    _description = 'Detail Permintaan Dana'

    permintaan_dana_id = fields.Many2one('tsi.permintaan.dana', string='Perjalanan Dinas', ondelete='cascade')
    ket = fields.Char(string="Keterangan", required=True, readonly=True, tracking=True)
    customer = fields.Many2one('res.partner', string="Perusahaan", domain="[('is_company', '=', True)]", tracking=True)
    nominal = fields.Float(string='Nominal')
    note = fields.Text(string='Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hold', 'Hold'),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
        ], string='Status', tracking=True, default='draft')

    formatted_nominal = fields.Char(string="Total (Format)", compute='_compute_formatted_nominal')

    def format_nominal(self, amount):
        if amount is None:
            return '0'
        return '{:,.0f}'.format(amount).replace(',', '.')

    @api.depends('nominal')
    def _compute_formatted_nominal(self):
        for rec in self:
            rec.formatted_nominal = self.format_nominal(rec.nominal)

class PNLProject(models.Model):
    _name           = "tsi.pnl.project"
    _description    = "PNL Project"
    _order          = 'id DESC'
    _rec_name       = 'partner_id'
    _inherit        = ["mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one('res.partner', string="Customer", domain="[('is_company', '=', True)]", tracking=True)
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True, domain="[('standard', 'in', ['iso'])]")
    sales_person = fields.Many2one('res.users', string='Sales Person',store=True, readonly=False, tracking=True)
    fee_cashback = fields.Float(string='Fee Eksternal', tracking=True, store=True)
    biaya_pajak = fields.Float(string='Biaya Pajak', tracking=True, store=True)
    biaya_mandays = fields.Float(string='Biaya Mandays', tracking=True, store=True)
    fee_marketing = fields.Float(string='Fee Marketing', tracking=True, store=True)
    tunjangan_dinas = fields.Float(string='Tunjangan Dinas', tracking=True, store=True)
    price_unit = fields.Float(string='Nilai Kontrak', tracking=True, store=True)

    biaya_transport = fields.Float(string='Biaya Transport', tracking=True, store=True)
    biaya_akreditasi = fields.Float(string='Biaya Akreditasi', tracking=True, store=True)
    biaya_tak_terduga = fields.Float(string='Biaya Tak Terduga', tracking=True, store=True)
    total_biaya = fields.Float(string='Total Pengeluaran', tracking=True, store=True, compute='_compute_total_biaya')
    profit = fields.Float(string='Profit', tracking=True, store=True, compute='_compute_profit')
    percentage = fields.Float(string='Percentage', tracking=True, store=True, compute='_compute_percentage')

    @api.model
    def load_views(self, views, options=None):  
        self.create_pnl_on_open()
           
        return super(PNLProject, self).load_views(views, options)

    @api.depends('profit', 'price_unit')
    def _compute_percentage(self):
        for rec in self:
            if rec.price_unit:  # Hindari pembagian dengan nol
                rec.percentage = rec.profit / rec.price_unit
            else:
                rec.percentage = 0.0  # Atau Anda bisa set None, tergantung kebutuhan

    @api.depends('price_unit', 'total_biaya')   
    def _compute_profit(self):
        for rec in self:
            if rec.total_biaya:
                rec.profit = (rec.price_unit - rec.total_biaya)
            else:
                rec.profit = 0

    @api.depends(
        'fee_cashback', 'fee_marketing', 'biaya_pajak',
        'tunjangan_dinas', 'biaya_transport',
        'biaya_akreditasi', 'biaya_tak_terduga'
    )
    def _compute_total_biaya(self):
        for rec in self:
            rec.total_biaya = (
                rec.fee_cashback
                + rec.fee_marketing
                + rec.biaya_pajak
                + rec.tunjangan_dinas
                + rec.biaya_transport
                + rec.biaya_akreditasi
                + rec.biaya_tak_terduga
            )

    def create_pnl_on_open(self):
        partners = self.env['res.partner'].sudo().search([("is_company", "=", True)])

        for partner in partners:
            isos = self.env["tsi.iso"].search([
                ('customer', '=', partner.id),
                ('state_sales', 'in', ['waiting_verify_operation', 'sent', 'sale']),
                ('iso_standard_ids', '!=', False),
            ])

            for iso in isos:
                standards = iso.iso_standard_ids
                if not standards:
                    continue

                total_fee_cashback = sum(iso_line.fee for iso_line in iso.lines_initial)
                total_price_unit = sum(iso_line.price for iso_line in iso.lines_initial)

                total_biaya_pajak = 0.0
                for line in iso.lines_initial:
                    pajak = line.price - (line.price / 1.11) if line.in_pajak else line.price * 0.11
                    total_biaya_pajak += pajak

                total_price_unit -= total_biaya_pajak

                # ✅ Ambil fee_marketing dari pengajuan.marketing
                fee_marketing = 0.0
                pengajuan_list = self.env['tsi.pengajuan.marketing'].search([
                    ('customer', '=', partner.id),
                    ('state', '=', 'approved'),
                ])
                for pengajuan in pengajuan_list:
                    if set(pengajuan.iso_standard_ids.ids) == set(standards.ids):
                        fee_marketing = pengajuan.total_fee_marketing
                        break

                # ✅ Ambil sales_person dari iso langsung
                sales = iso.sales_person.id if iso.sales_person else False

                tunjangan_dinas = 0.0
                total_biaya_mandays = 0.0
                programs = self.env['ops.program'].search([
                    ('customer', '=', partner.id)
                ])

                program_aktuals = self.env['ops.program.aktual'].search([
                    ('reference_id', 'in', programs.ids),
                    ('mandayss', '!=', False)
                ])

                perjalanan = self.env['tsi.perjalanan.dinas'].search([
                    ('customer', '=', partner.id),
                    ('state', '=', 'approved'),
                ])

                for p in perjalanan:
                    for line in p.lines:
                        if line.nama == 'Tunjangan Dinas':
                            tunjangan_dinas += line.jumlah

                    for auditor in p.auditor:
                        harga = auditor.harga_mandays
                        employee = auditor.name_auditor

                        if not employee:
                            continue

                        matched_aktuals = program_aktuals.filtered(lambda a: (
                            a.reference_id.customer.id == partner.id and (
                                a.lead_auditor.id == employee.id or
                                a.auditor.id == employee.id or
                                a.auditor_2.id == employee.id or
                                a.auditor_3.id == employee.id or
                                a.expert.id == employee.id
                            )
                        ))

                        for matched in matched_aktuals:
                            try:
                                mandays_count = float(matched.mandayss)
                                total_biaya_mandays += harga * mandays_count
                            except ValueError:
                                continue

                existing_pnl = self.env['tsi.pnl.project'].search([
                    ('partner_id', '=', partner.id),
                    ('iso_standard_ids', '=', standards.ids),
                ], limit=1)

                vals = {
                    "partner_id": partner.id,
                    "iso_standard_ids": [(6, 0, standards.ids)],
                    "price_unit": total_price_unit,
                    "fee_cashback": total_fee_cashback,
                    "biaya_pajak": total_biaya_pajak,
                    "fee_marketing": fee_marketing,
                    "tunjangan_dinas": tunjangan_dinas,
                    "biaya_mandays": total_biaya_mandays,
                    "sales_person": sales,
                }

                if existing_pnl:
                    existing_pnl.write(vals)
                else:
                    self.env['tsi.pnl.project'].create(vals)

