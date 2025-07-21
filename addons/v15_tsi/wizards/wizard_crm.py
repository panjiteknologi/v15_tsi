from odoo import models, fields, api
import logging
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning
from datetime import datetime, date

_logger = logging.getLogger(__name__)

class WizardLanjutCRM(models.TransientModel):
    _name = 'tsi.wizard_lanjut'
    _description = 'Wizard Lanjut'

    def _get_default_partner(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).partner_id

    def _get_default_standard(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

    def _get_default_tahapan(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).tahapan_audit_ids

    def _get_default_sales(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).sales

    def _get_default_associate(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).associate

    def _get_default_category(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).category

    def _get_default_segment(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).segment

    def _get_default_tahun_aktif(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).status_tahun_aktif

    def _get_default_pic(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).pic

    def _get_default_closingby(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).closing_by

    def _get_default_alamat(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).alamat

    def _get_default_akreditasi(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).akreditasi

    def _get_default_level_audit(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).level_audit

    def _get_default_level_audit_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).level_audit_ispo

    def _get_default_referal(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).referal

    line_ids = fields.One2many('tsi.wizard_lanjut_line', 'lanjut_id', string='Lines CRM Lanjut')

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False,   default=_get_default_standard)
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', tracking=True, readonly=False, default=_get_default_tahapan)
    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True,   default=_get_default_partner)
    sales               = fields.Many2one('res.users', string='Sales Person', tracking=True, store=True, readonly=True, default=_get_default_sales)
    associate           = fields.Many2one('res.partner', string="Associate", tracking=True , store=True, readonly=True, default=_get_default_associate)
    category            = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',   'Silver'),
                            ('gold', 'Gold')
                        ], string='Category', default=_get_default_category, readonly=True)
    segment             = fields.Many2many('res.partner.category', string='Segment', tracking=True, readonly=True, default=_get_default_segment)
    status_tahun_aktif  = fields.Char(string='Status Tahun Aktif', tracking=True, readonly=True, default=_get_default_tahun_aktif)
    pic                 = fields.Many2one('res.partner', string="PIC", tracking=True, readonly=True, default=_get_default_pic)
    closing_by          = fields.Selection([
                            ('konsultan',  'Konsultan'),
                            ('direct',   'Direct'),
                        ], string='Closing By', readonly=True, default=_get_default_closingby)
    alamat              = fields.Selection([
                            ('dalam_kota',  'Dalam Kota'),
                            ('luar_kota',   'Luar Kota'),
                        ], string='Alamat', readonly=True, default=_get_default_alamat)
    akreditasi          = fields.Many2one('tsi.iso.accreditation', string='Akreditasi', readonly=True, default=_get_default_akreditasi)
    level_audit         = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2')
                        ], string='Level Audit ISO', readonly=True, default=_get_default_level_audit)
    level_audit_ispo    = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2'),
                            ('sv3', 'SV3'),
                            ('sv4', 'SV4')
                        ], string='Level Audit ISPO', readonly=True, default=_get_default_level_audit_ispo)
    referal             = fields.Char(string='Referal', tracking=True, readonly=True, default=_get_default_referal)

    def send(self):

        total_nilai = 0.0
        for line in self.line_ids:
            total_nilai += line.nilai

        # Ambil hanya record unik berdasarkan (nomor_kontrak, tanggal_kontrak)
        unique_lines = {(line.nomor_kontrak, line.tanggal_kontrak) for line in self.line_ids}

        # Ambil salah satu data (karena sudah unik)
        selected_line = next(iter(unique_lines), (False, False))

        # Ambil hanya satu nomor_kontrak dan tanggal_kontrak dari data unik
        selected_nomor_kontrak, selected_tanggal_kontrak = selected_line

        crm_lanjut_vals = {
            'partner_id': self.partner_id.id,
            'sales': self.sales.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            # 'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            # 'accreditation': self.akreditasi.id,
            # 'associate': self.associate.id,
            # 'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            # 'pic': self.pic.id,
            # 'closing_by': self.closing_by,
            # 'alamat': self.alamat,
            # 'level_audit': self.level_audit,
            # 'level_audit_ispo': self.level_audit_ispo,
            # 'referal': self.referal,
            'nilai_kontrak': total_nilai,
            'contract_number': selected_nomor_kontrak,
            'contract_date': selected_tanggal_kontrak,
        }

        crm_lanjut = self.env['tsi.crm.lanjut'].create(crm_lanjut_vals)

        total_nilai = 0.0
        for line in self.line_ids:
            crm_accreditation_vals = {
                'lanjut_id': crm_lanjut.id,
                'iso_standard_ids': [(6, 0, line.iso_standard_ids.ids)],
                'accreditation': line.accreditation.id,
                'tahapan_audit': line.tahapan_audit,
                'nilai_ia': line.nilai,
            }

            self.env['tsi.crm_accreditation'].create(crm_accreditation_vals)

            total_nilai += line.nilai

        history_kontrak = self.env['tsi.history_kontrak'].search([('id', 'in', self.env.context.get('active_ids'))], limit=1)

        if history_kontrak:
            history_kontrak.write({
                'state': 'lanjut',
                'nilai_kontrak': total_nilai,
            })

        partner_name = self.partner_id.name or "Customer"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses!',
                'message': f'{partner_name} berhasil ke CRM Lanjut!',
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

class WizardLanjutCRMLine(models.TransientModel):
    _name = 'tsi.wizard_lanjut_line'
    _description = 'Wizard Lanjut Line'

    lanjut_id = fields.Many2one('tsi.wizard_lanjut', string='Wizard', required=True, ondelete='cascade')
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards')
    accreditation   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    nomor_kontrak   = fields.Char('Nomor Kontrak')
    tanggal_kontrak = fields.Date('Tanggal Kontrak')
    tahapan_audit   = fields.Char('Tahapan Audit', tracking=True)
    nilai           = fields.Integer('Nilai Kontrak', tracking=True)

class WizardSuspendCRM(models.TransientModel):
    _name = 'tsi.wizard_suspend'
    _description = 'Wizard Suspend'

    def _get_default_partner(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).partner_id

    def _get_default_standard(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

    def _get_default_tahapan(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).tahapan_audit_ids

    def _get_default_sales(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).sales

    def _get_default_associate(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).associate

    def _get_default_category(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).category

    def _get_default_segment(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).segment

    def _get_default_tahun_aktif(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).status_tahun_aktif

    def _get_default_pic(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).pic

    def _get_default_closingby(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).closing_by

    def _get_default_alamat(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).alamat

    def _get_default_akreditasi(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).akreditasi

    def _get_default_level_audit(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).level_audit

    def _get_default_level_audit_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).level_audit_ispo

    def _get_default_referal(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).referal

    line_ids = fields.One2many('tsi.wizard_suspend_line', 'suspend_id', string='Lines CRM Suspend')

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False,   default=_get_default_standard)
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', tracking=True, readonly=False, default=_get_default_tahapan)
    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True,   default=_get_default_partner)
    sales               = fields.Many2one('res.users', string='Sales Person', tracking=True, store=True, readonly=True, default=_get_default_sales)
    associate           = fields.Many2one('res.partner', string="Associate", tracking=True , store=True, readonly=True, default=_get_default_associate)
    category            = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',   'Silver'),
                            ('gold', 'Gold')
                        ], string='Category', default=_get_default_category, readonly=True)
    segment             = fields.Many2many('res.partner.category', string='Segment', tracking=True, readonly=True, default=_get_default_segment)
    status_tahun_aktif  = fields.Char(string='Status Tahun Aktif', tracking=True, readonly=True, default=_get_default_tahun_aktif)
    pic                 = fields.Many2one('res.partner', string="PIC", tracking=True, readonly=True, default=_get_default_pic)
    closing_by          = fields.Selection([
                            ('konsultan',  'Konsultan'),
                            ('direct',   'Direct'),
                        ], string='Closing By', readonly=True, default=_get_default_closingby)
    alamat              = fields.Selection([
                            ('dalam_kota',  'Dalam Kota'),
                            ('luar_kota',   'Luar Kota'),
                        ], string='Alamat', readonly=True, default=_get_default_alamat)
    akreditasi          = fields.Many2one('tsi.iso.accreditation', string='Akreditasi', readonly=True, default=_get_default_akreditasi)
    level_audit         = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2')
                        ], string='Level Audit ISO', readonly=True, default=_get_default_level_audit)
    level_audit_ispo    = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2'),
                            ('sv3', 'SV3'),
                            ('sv4', 'SV4')
                        ], string='Level Audit ISPO', readonly=True, default=_get_default_level_audit_ispo)
    referal             = fields.Char(string='Referal', tracking=True, readonly=True, default=_get_default_referal)
    alasan              = fields.Many2one('crm.alasan', string="Alasan")

    def send(self):

        total_nilai = 0.0
        for line in self.line_ids:
            total_nilai += line.nilai

        # Ambil hanya record unik berdasarkan (nomor_kontrak, tanggal_kontrak)
        unique_lines = {(line.nomor_kontrak, line.tanggal_kontrak) for line in self.line_ids}

        # Ambil salah satu data (karena sudah unik)
        selected_line = next(iter(unique_lines), (False, False))

        # Ambil hanya satu nomor_kontrak dan tanggal_kontrak dari data unik
        selected_nomor_kontrak, selected_tanggal_kontrak = selected_line

        crm_suspend_vals = {
            'partner_id': self.partner_id.id,
            'sales': self.sales.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            # 'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            # 'accreditation': self.akreditasi.id,
            # 'associate': self.associate.id,
            # 'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            # 'pic': self.pic.id,
            # 'closing_by': self.closing_by,
            # 'alamat': self.alamat,
            # 'level_audit': self.level_audit,
            # 'level_audit_ispo': self.level_audit_ispo,
            # 'referal': self.referal,
            'alasan': self.alasan.id,
            'nilai_kontrak': total_nilai,
            'contract_number': selected_nomor_kontrak,
            'contract_date': selected_tanggal_kontrak,
        }

        crm_suspend = self.env['tsi.crm.suspen'].create(crm_suspend_vals)

        total_nilai = 0.0
        for line in self.line_ids:
            crm_accreditation_vals = {
                'suspend_id': crm_suspend.id,
                'iso_standard_ids': [(6, 0, line.iso_standard_ids.ids)],
                'accreditation': line.accreditation.id,
                'tahapan_audit': line.tahapan_audit,
                'nilai_ia': line.nilai,
            }

            self.env['tsi.crm_accreditation'].create(crm_accreditation_vals)

            total_nilai += line.nilai

        history_kontrak = self.env['tsi.history_kontrak'].search([('id', 'in', self.env.context.get('active_ids'))], limit=1)

        if history_kontrak:
            history_kontrak.write({
                'state': 'suspend',
                'nilai_kontrak': total_nilai,
            })

        partner_name = self.partner_id.name or "Customer"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses!',
                'message': f'{partner_name} berhasil ke CRM Suspend!',
                'sticky': False,
                'type': 'warning',
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

class WizardSuspendCRMLine(models.TransientModel):
    _name = 'tsi.wizard_suspend_line'
    _description = 'Wizard Suspend Line'

    suspend_id          = fields.Many2one('tsi.wizard_suspend', string='Wizard', required=True, ondelete='cascade')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    nomor_kontrak   = fields.Char('Nomor Kontrak')
    tanggal_kontrak = fields.Date('Tanggal Kontrak')
    tahapan_audit       = fields.Char('Tahapan Audit', tracking=True)
    nilai               = fields.Integer('Nilai Kontrak', tracking=True)

class WizardLossCRM(models.TransientModel):
    _name = 'tsi.wizard_loss'
    _description = 'Wizard Loss'

    def _get_default_partner(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).partner_id

    def _get_default_standard(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

    def _get_default_tahapan(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).tahapan_audit_ids

    def _get_default_sales(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).sales

    def _get_default_associate(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).associate

    def _get_default_category(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).category

    def _get_default_segment(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).segment

    def _get_default_tahun_aktif(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).status_tahun_aktif

    def _get_default_pic(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).pic

    def _get_default_closingby(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).closing_by

    def _get_default_alamat(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).alamat

    def _get_default_akreditasi(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).akreditasi

    def _get_default_level_audit(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).level_audit

    def _get_default_level_audit_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).level_audit_ispo

    def _get_default_referal(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).referal

    line_ids = fields.One2many('tsi.wizard_loss_line', 'loss_id', string='Lines CRM Loss')

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False,   default=_get_default_standard)
    tahapan_audit_ids   = fields.Many2many('tsi.iso.tahapan', string='Tahapan', tracking=True, readonly=False, default=_get_default_tahapan)
    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True,   default=_get_default_partner)
    sales               = fields.Many2one('res.users', string='Sales Person', tracking=True, store=True, readonly=True, default=_get_default_sales)
    associate           = fields.Many2one('res.partner', string="Associate", tracking=True , store=True, readonly=True, default=_get_default_associate)
    category            = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',   'Silver'),
                            ('gold', 'Gold')
                        ], string='Category', default=_get_default_category, readonly=True)
    segment             = fields.Many2many('res.partner.category', string='Segment', tracking=True, readonly=True, default=_get_default_segment)
    status_tahun_aktif  = fields.Char(string='Status Tahun Aktif', tracking=True, readonly=True, default=_get_default_tahun_aktif)
    pic                 = fields.Many2one('res.partner', string="PIC", tracking=True, readonly=True, default=_get_default_pic)
    closing_by          = fields.Selection([
                            ('konsultan',  'Konsultan'),
                            ('direct',   'Direct'),
                        ], string='Closing By', readonly=True, default=_get_default_closingby)
    alamat              = fields.Selection([
                            ('dalam_kota',  'Dalam Kota'),
                            ('luar_kota',   'Luar Kota'),
                        ], string='Alamat', readonly=True, default=_get_default_alamat)
    akreditasi          = fields.Many2one('tsi.iso.accreditation', string='Akreditasi', readonly=True, default=_get_default_akreditasi)
    level_audit         = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2')
                        ], string='Level Audit ISO', readonly=True, default=_get_default_level_audit)
    level_audit_ispo    = fields.Selection([
                            ('ia_reten',  'IA RETEN'),
                            ('rc',   'RC'),
                            ('sv1', 'SV1'),
                            ('sv2', 'SV2'),
                            ('sv3', 'SV3'),
                            ('sv4', 'SV4')
                        ], string='Level Audit ISPO', readonly=True, default=_get_default_level_audit_ispo)
    referal             = fields.Char(string='Referal', tracking=True, readonly=True, default=_get_default_referal)
    alasan              = fields.Many2one('crm.alasan', string="Alasan")

    def send(self):

        total_nilai = 0.0
        for line in self.line_ids:
            total_nilai += line.nilai

        # Ambil hanya record unik berdasarkan (nomor_kontrak, tanggal_kontrak)
        unique_lines = {(line.nomor_kontrak, line.tanggal_kontrak) for line in self.line_ids}

        # Ambil salah satu data (karena sudah unik)
        selected_line = next(iter(unique_lines), (False, False))

        # Ambil hanya satu nomor_kontrak dan tanggal_kontrak dari data unik
        selected_nomor_kontrak, selected_tanggal_kontrak = selected_line

        crm_loss_vals = {
            'partner_id': self.partner_id.id,
            'sales': self.sales.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            # 'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            # 'accreditation': self.akreditasi.id,
            # 'associate': self.associate.id,
            # 'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            # 'pic': self.pic.id,
            # 'closing_by': self.closing_by,
            # 'alamat': self.alamat,
            # 'level_audit': self.level_audit,
            # 'level_audit_ispo': self.level_audit_ispo,
            # 'referal': self.referal,
            'alasan': self.alasan.id,
            'nilai_kontrak': total_nilai,
            'contract_number': selected_nomor_kontrak,
            'contract_date': selected_tanggal_kontrak,
        }

        crm_loss = self.env['tsi.crm.loss'].create(crm_loss_vals)

        total_nilai = 0.0
        for line in self.line_ids:
            crm_accreditation_vals = {
                'loss_id': crm_loss.id,
                'iso_standard_ids': [(6, 0, line.iso_standard_ids.ids)],
                'accreditation': line.accreditation.id,
                'tahapan_audit': line.tahapan_audit,
                'nilai_ia': line.nilai,
            }

            self.env['tsi.crm_accreditation'].create(crm_accreditation_vals)

            total_nilai += line.nilai

        history_kontrak = self.env['tsi.history_kontrak'].search([('id', 'in', self.env.context.get('active_ids'))], limit=1)

        if history_kontrak:
            history_kontrak.write({
                'state': 'lost',
                'nilai_kontrak': total_nilai,
            })

        partner_name = self.partner_id.name or "Customer"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses!',
                'message': f'{partner_name} berhasil ke CRM Loss!',
                'sticky': False,
                'type': 'danger',
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

class WizardLossCRMLine(models.TransientModel):
    _name = 'tsi.wizard_loss_line'
    _description = 'Wizard Loss Line'

    loss_id             = fields.Many2one('tsi.wizard_loss', string='Wizard', required=True, ondelete='cascade')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    nomor_kontrak   = fields.Char('Nomor Kontrak')
    tanggal_kontrak = fields.Date('Tanggal Kontrak')
    tahapan_audit       = fields.Char('Tahapan Audit', tracking=True)
    nilai               = fields.Integer('Nilai Kontrak', tracking=True)
