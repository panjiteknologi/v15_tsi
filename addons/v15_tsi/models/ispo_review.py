from base64 import standard_b64decode
from odoo import models, fields, api
from datetime import datetime, timedelta


class ISPOReview(models.Model):
    _name           = "tsi.ispo.review"
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _description    = "ISPO Review"
    _order          = 'id DESC'

    def _get_default_iso(self):
        return self.env['sale.order'].search([('id','in',self.env.context.get('active_ids'))],limit=5).iso_standard_ids

    reference       = fields.Many2one('tsi.ispo', string="Reference")
    doctype         = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',   'ISPO'),
                        ], string='Doc Type', index=True, related='reference.doctype', store=True)

    customer        = fields.Many2one('res.partner', string="Customer", related='reference.customer', store=True)

    name            = fields.Char(string="Document No",  readonly=True)
    office_address      = fields.Char(string="Office Address", related="reference.office_address")
    invoicing_address   = fields.Char(string="Invoicing Address", related="reference.invoicing_address")
    received_date   = fields.Date(string="Issued Date", related="reference.issue_date")    
    review_date     = fields.Datetime(string="Verified Date", default=datetime.now())    
    finish_date     = fields.Datetime(string="Approve Date", readonly=True)    
    
    review_by       = fields.Many2one('res.users', string="Created By", related="reference.user_id")
    sales_person       = fields.Many2one('res.users', string="Sales Person", related="reference.sales_person")
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)
    accreditation         = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation")

    # company_name    = fields.Char(string="Company Name")
    # ea_code         = fields.Many2one(string="EA Code", related='reference.ea_code')
    contact_person  = fields.Char(string="Contact Person", related="reference.contact_person")
    jabatan         = fields.Char(string="Position", related="reference.jabatan")
    telepon         = fields.Char(string="Telephone", related="reference.telepon")
    fax             = fields.Char(string="Fax", related="reference.fax")
    email           = fields.Char(string="Email", related="reference.email")
    website         = fields.Char(string="Website", related="reference.website")
    # cellular        = fields.Char(string="Celular", related="reference.cellular")
    # alt_scope       = fields.Text('Alt Scope', website_form_blacklisted=False)
    # alt_scope_id    = fields.Many2one('tsi.alt_scope',      string='Alt Scope')
    catatan             = fields.Text('Notes')

    # scope           = fields.Text(string="Scope", related='reference.scope', store=True)
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIK'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', related='reference.scope', index=True)
    boundaries  = fields.Text(string="Boundaries", related="reference.boundaries")
    cause       = fields.Text('Mandatory SNI', related='reference.cause')

    # personnel
    partner_site    = fields.One2many('tsi.iso.site', 'reference_id', string="Personnel Situation", index=True, related='reference.partner_site')
    head_office     = fields.Char(string="Head Office", )
    site_office     = fields.Char(string="Site Office", )
    off_location    = fields.Char(string="Off Location", )
    part_time       = fields.Char(string="Part Time", )
    subcon          = fields.Char(string="Sub Contractor", )
    unskilled       = fields.Char(string="Unskilled", )
    seasonal        = fields.Char(string="Seasonal", )
    total_emp       = fields.Char(string="Total Employee", )
    shift_number    = fields.Char(string="Shift", )
    number_site     = fields.Char(string="Number Site", )
    outsource_proc  = fields.Text('Outsourcing Process', )
    outsourced_activity = fields.Text(string="Outsourced Activity", )

    # maturity
    start_implement     = fields.Char(string="Start Implement", )

    mat_consultancy     = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Use of Consultants", )
    mat_certified       = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified System", )
    other_system         = fields.Char(string='Other System')
    # mat_certified_cb    = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Certified CB", )
    # mat_tools           = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Continual Improvement", )
    # mat_national        = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="National Certified", )
    # mat_more            = fields.Selection([('YES', 'YES'),('NO', 'NO')], string="Setup More Standard", )

    txt_mat_consultancy = fields.Char(string="Tx Consultancy", )
    txt_mat_certified   = fields.Char(string="Tx Certified", )
    # txt_mat_certified_cb    = fields.Char(string="Tx Certified CB", )
    # txt_mat_tools       = fields.Char(string="Tx Continual Improvement", )
    # txt_mat_national    = fields.Char(string="Tx National Certified", )
    # txt_mat_more        = fields.Char(string="Tx Setup More Standard", )
    
    stage_audit     = fields.Selection([
                            ('Stage-1', 'Stage 1'),
                            ('Stage-2', 'Stage 2'),
                            ('Surveillance-1', 'Surveillance 1'),
                            ('Surveillance-2', 'Surveillance 2'),
                            ('Surveillance-3', 'Surveillance 3'),
                            ('Surveillance-4', 'Surveillance 4'),
                            ('Recertification-1', 'Recertification 1'),
                            ('Recertification-2', 'Recertification 2'),
                        ], string='Audit Stage', index=True, related="reference.audit_stage")
    tx_site_count   = fields.Integer('Number of Site', )
    tx_remarks      = fields.Char('Remarks', related="reference.tx_remarks")
    certification   = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, readonly=True, related="reference.certification" )
    
    audit_stage = fields.Selection([
                            ('initial',         'Initial Assesment'),
                            ('recertification', 'Recertification'),
                            ('transfer_surveilance',    'Transfer Assesment from Surveilance'),
                            ('transfer_recert',         'Transfer Assesment from Recertification'),
                        ], string='Audit Stage', index=True, related="reference.audit_stage")
    
    legalitas_type = fields.Selection([
        ('integrasi', 'Integrasi'),
        ('kebun', 'Kebun'),
        ('pabrik', 'Pabrik'),
        ('swadaya_plasma', 'Swadaya/Plasma'),
    ], string='Tipe Legalitas', related="reference.legalitas_type")
    kebun_line_ids = fields.One2many('tsi.ispo.kebun.line', 'reference_id', string='Personal Situation Kebun', related="reference.kebun_line_ids")
    pabrik_line_ids = fields.One2many('tsi.ispo.pabrik.line', 'reference_id', string='Personal Situation Pabrik', related="reference.pabrik_line_ids")
    swadaya_line_ids = fields.One2many('tsi.ispo.swadaya.plasma.line', 'reference_id', string='Personal Situation Swadaya/Plasma', related="reference.swadaya_line_ids")

    # Field-field tambahan untuk Integrasi
    hgu = fields.Char(string='No. Sertifikat HGU', related="reference.hgu")
    sk_hgu = fields.Char(string='No. SK HGU', related="reference.sk_hgu")
    hgb = fields.Char(string='No. Sertifikat HGB', related="reference.hgb")
    sk_hgb = fields.Char(string='No. SK HGB', related="reference.sk_hgb")
    iup = fields.Char(string='IUP / IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP', related="reference.iup")
    pup = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun', related="reference.pup")
    izin_lingkungan_integrasi = fields.Char(string='Izin Lingkungan (Integrasi)', related="reference.izin_lingkungan_integrasi")
    luas_lahan = fields.Float(string='Luas Lahan', related="reference.luas_lahan")
    kapasitas_pabrik = fields.Float(string='Kapasitas Pabrik', related="reference.kapasitas_pabrik")
    izin_lokasi = fields.Char(string='Izin Lokasi', related="reference.izin_lokasi")
    apl = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat', related="reference.apl")
    risalah_panitia = fields.Char(string='Risalah Panitia A/B', related="reference.risalah_panitia")
    lahan_gambut = fields.Char(string='Lahan Gambut / Mineral', related="reference.lahan_gambut")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    jlh_kebun = fields.Char('Jumlah Kebun' , related="reference.jlh_kebun")
    jlh_pabrik = fields.Char('Jumlah Pabrik', related="reference.jlh_pabrik")
    # peta = fields.Selection([
    #     ('Peta Lokasi', 'Peta Lokasi'),
    #     ('Peta Topografi', 'Peta Topografi'),
    #     ('Peta Kebun', 'Peta Kebun'),
    #     ('Peta Area Statement', 'Peta Area Statement'),
    #     ('Peta Kawasan Lindung', 'Peta Kawasan Lindung'),
    #     ('Peta Sebaran Sungai', 'Peta Sebaran Sungai'),
    #     ('Peta Kemiringan Lahan', 'Peta Kemiringan Lahan'),
    # ], string='Peta - Peta', related="reference.peta")

    # Field-field tambahan untuk Kebun
    hgu_kebun = fields.Char(string='No. Sertifikat HGU', related="reference.hgu_kebun")
    sk_hgu_kebun= fields.Char(related="reference.sk_hgu_kebun")
    iupb = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP', related="reference.iupb")
    izin_lingkungan_kebun = fields.Char(string='Izin Lingkungan', related="reference.izin_lingkungan_kebun")
    informasi_plasma_kebun = fields.Char(string='Informasi Plasma', related="reference.informasi_plasma_kebun")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    pup_kebun = fields.Selection([
        ('kelas_i', 'Kelas I'),
        ('kelas_ii', 'Kelas II'),
        ('kelas_iii', 'Kelas III'),
    ], string='PUP / Kelas Kebun', related="reference.pup_kebun")
    risalah_panitia_kebun = fields.Char(string='Risalah Panitia B',related="reference.risalah_panitia_kebun")
    jumlah_kebun = fields.Char('Jumlah Kebun' , related="reference.jumlah_kebun")
    apl_kebun = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat', related="reference.apl_kebun")

    # Field-field tambahan untuk Pabrik
    hgb_pabrik = fields.Char(string='No. Sertifikat HGB' , related="reference.hgb_pabrik")
    sk_hgb_pabrik = fields.Char(string='No. SK HGB' , related="reference.sk_hgb_pabrik")
    kapasitas_pabrik_pabrik = fields.Float(string='Kapasitas Pabrik', related="reference.kapasitas_pabrik_pabrik")
    iup_pabrik = fields.Char(string='IUPB / Izin prinsip/BKPM/OSS/ITUK/ITUBP/SPUP', related="reference.iup_pabrik")
    sumber_bahan_baku = fields.Char(string='20% Sumber Bahan Baku', related="reference.sumber_bahan_baku")
    izin_lingkungan_pabrik = fields.Char(string='Izin Lingkungan', related="reference.izin_lingkungan_pabrik")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    risalah_panitia_pabrik = fields.Char(string='Risalah Panitia A',related="reference.risalah_panitia_pabrik")
    jumlah_pabrik = fields.Char('Jumlah Pabrik' , related="reference.jumlah_pabrik")
    apl_pabrik = fields.Char(string='APL / Pelepasan Kawasan Hutan/Tukar Menukar Kawasan/Tanah Adat/Ulayat', related="reference.apl_pabrik")

    # Field-field tambahan untuk Swadaya/Plasma
    shm = fields.Char(string='SHM/Kepemilikan Lahan Yang diakui Pemerintah', related="reference.shm")
    stdb = fields.Char(string='STDB', related="reference.stdb")
    sppl = fields.Char(string='SPPL', related="reference.sppl")
    akta_pendirian = fields.Char(string='Akta Pendirian dan SK Kemenhumkam', related="reference.akta_pendirian")
    peta_ids = fields.Many2many('tipe.peta.ispo', string='Peta-Peta', related="reference.peta_ids")
    salesinfo_site_ispo    = fields.One2many('tsi.iso.additional_salesinfo', 'reference_id10', string="Additional Info", index=True, related="reference.salesinfo_site_ispo")
    jlh_kebun_plasma = fields.Char('Jumlah Kebun' , related="reference.jlh_kebun_plasma")
    jlh_anggota = fields.Char('Jumlah Anggota' , related="reference.jlh_anggota")
    
    audit_type      = fields.Selection([
                            ('single',      'SINGLE AUDIT'),
                            ('join',        'JOIN AUDIT'),
                            ('combine',     'COMBINE AUDIT'),
                            ('integrated',  'INTEGRATED AUDIT'),
                        ], string='Audit Type', index=True)
    allowed_sampling    = fields.Char(string="Number of Sampling")

    proposed_aspect = fields.Char(string="Proposed Standard")
    proposed_desc   = fields.Char(string="Description")
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=True, default=_get_default_iso, related="reference.iso_standard_ids")

    # EMPLOYEE INFORMATION
    total_emp           = fields.Integer(string="Total Employee")
    site_emp_total      = fields.Integer(string='Total Site Employee')
    offsite_emp_total   = fields.Integer(string='Total OffSite Employee')
    ho_emp_total        = fields.Integer(string='Total HO Employee')
    number_of_site      = fields.Integer(string='Number of Site')

    mandays_ori_lines   = fields.One2many('tsi.iso.mandays', 'review_id', string="Mandays Original", index=True)
    mandays_isms_lines  = fields.One2many('tsi.iso.mandays.isms', 'review_id', string="Mandays ISMS", index=True)
    mandays_inte_lines  = fields.One2many('tsi.iso.mandays.integrated', 'review_id', string="Mandays Integrated", index=True)
    mandays_audit_time  = fields.One2many('tsi.iso.mandays.audit_time', 'review_id', string="Audit Time", index=True)
    mandays_justify     = fields.One2many('tsi.iso.mandays.justification', 'review_id', string="Justification", index=True)
    mandays_justify_isms     = fields.One2many('tsi.iso.mandays.justification.isms', 'review_id', string="Justification - ISMS", index=True)
    mandays_pa          = fields.One2many('tsi.iso.mandays.pa', 'review_id', string="PA", index=True)

# ISPO RELATED FIELD
    ispo_evaluasi       = fields.One2many('tsi.ispo.evaluasi', 'review_id', string="Evaluasi", index=True)
    ispo_nilai_skor     = fields.One2many('tsi.ispo.nilai_skor', 'review_id', string="Nilai Skor", index=True)
    ispo_justification  = fields.One2many('tsi.ispo.justification', 'review_id', string="Justification", index=True)
    ispo_mandays        = fields.One2many('tsi.ispo.mandays', 'review_id', string="Mandays", index=True)
    ispo_total_mandays  = fields.One2many('tsi.ispo.total_mandays', 'review_id', string="Total Mandays", index=True)

    sampling_pabrik     = fields.Boolean(string='Sampling Pabrik')
    sampling_kebun      = fields.Boolean(string='Sampling Kebun')


    state           = fields.Selection([
                            ('new',         'New'),
                            # ('review',      'Review'),
                            ('approved',    'Approved'),
                            ('revice',    'Revised'),
                            ('reject',      'Reject'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='new')
    
    audit_similarities = fields.Selection([
                            ('similar',         'Similar Activities processes'),
                            ('diferences',      'Diferences between Activities'),
                        ], string='Multisite Similarities', index=True, )

    lingkup = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, )
    kepemilikan = fields.Selection([
                            ('bumn',   'BUMN'),
                            ('individu', 'INDIVIDU'),
                            ('bumd',  'BUMD'),
                            ('kud',  'KUD'),
                            ('pma',  'PMA'),
                        ], string='Kepemilikan', index=True, readonly=True, related="reference.kepemilikan")
    
    sertifikasi_baru = fields.Boolean(string='Sertifikasi Awal/Baru', related="reference.sertifikasi_baru")
    re_sertifikasi = fields.Boolean(string='Re-Sertifikasi', related="reference.re_sertifikasi")
    perluasan = fields.Boolean(string='Perluasan Ruang Lingkup', related="reference.perluasan")
    pengurangan = fields.Boolean(string='Pengurangan Ruang Lingkup', related="reference.pengurangan")
    transfer = fields.Boolean(string='Transfer CB/LS', related="reference.transfer") 

    
    # ISPO RELATED fields
    permohonan     = fields.Selection([
                            ('baru',   'Sertifikasi Awal / Baru'),
                            ('ulang', 'Re-Sertifikasi'),
                            ('perluasan',  'Perluasan Ruang Lingkup'),
                            ('transfer',  'Transfer CB / LS'),
                        ], string='Ruang Lingkup', index=True, )
    lingkup = fields.Selection([
                            ('kebun',   'KEBUN'),
                            ('pabrik', 'Pabrik'),
                            ('integrasi',  'Integrasi'),
                        ], string='Ruang Lingkup', index=True, )
    tipe_tanah = fields.Selection([
                            ('tidak_gambut',   'Tidak Bergambut'),
                            ('gambut', 'Gambut'),
                        ], string='Tipe Tanah', index=True, )
    sebaran_tanah = fields.Selection([
                            ('tidak',       'Tidak berbatasan langsung dengan lahan negara/ masyarakat'),
                            ('berbatasan',  'Berbatasan dengan lahan negara/  Kawasan lindung namun terdapat Batasan alam yang jelas'),
                            ('lindung',     'Sebagian atau seluruhnya berada pada Kawasan Linding'),
                        ], string='Sebaran Geografis', index=True, )
    tipe_kegiatan = fields.Selection([
                            ('tidak',       'Tidak ada peremajaan'),
                            ('ada',  'Ada peremajaan'),
                        ], string='Tipe Kegiatan', index=True, )
    topografi = fields.Selection([
                            ('datar',       'Datar'),
                            ('bukit',  'Berbukit'),
                        ], string='Topografi Tanah', index=True, )

    is_kebun_pabrik     = fields.Boolean(string='Kebun / Pabrik')
                        
    legal_lokasi        = fields.Char(string='Ijin Lokasi', )
    legal_iup           = fields.Char(string='Ijin IUP', )
    legal_spup          = fields.Char(string='Ijin SPUP', )
    legal_itubp         = fields.Char(string='Ijin ITBUP', )
    legal_prinsip       = fields.Char(string='Ijin Prinsip', )
    legal_menteri       = fields.Char(string='Ijin Menteri', )
    legal_bkpm          = fields.Char(string='Ijin BKPM', )

    perolehan_a         = fields.Char(string='APL', )
    perolehan_b         = fields.Char(string='HPK', )
    perolehan_c         = fields.Char(string='Tanah Adat', )
    perolehan_d         = fields.Char(string='Tanah Lain', )

    legal_hgu           = fields.Char(string='HGU / HGB', )
    legal_amdal         = fields.Char(string='Izin Lingkungan - AMDAL', )

    is_plasma_swadaya   = fields.Boolean(string='Plasma / Swadaya', )

    kebun_sertifikat    = fields.Char(string='Sertifikat Tanah', )
    kebun_penetapan     = fields.Char(string='Penetapan', )
    kebun_std           = fields.Char(string='Surat Tanda Daftar', )
    kebun_pembentukan   = fields.Char(string='Pembentukan', )
    kebun_konversi      = fields.Char(string='Konversi', )
    kebun_kesepakatan   = fields.Char(string='Kesepakatan', )

    sertifikat_ispo     = fields.Text(string='Sertifikat ISPO', )

    tani_nama           = fields.Char(string='Nama Kelompok Tani', )
    tani_adrt           = fields.Char(string='Akta Pendirian', )
    tani_pembentukan    = fields.Char(string='Pembentukan Kelompok Tani', )
    tani_rko            = fields.Char(string='Rencana Kegiatan', )
    tani_kegiatan       = fields.Char(string='Laporan Kegiatan', )
    tani_jumlah         = fields.Char(string='Jumlah Petani', )
    tani_area           = fields.Char(string='Total Area', )
    tani_tertanam       = fields.Char(string='Area Tertanam', )
    tani_tbs            = fields.Char(string='Produksi TBS', )

    peta_lokasi         = fields.Char(string='Peta Lokasi', )

    add_nama_perusahaan = fields.Char(string='Informasi Konsultan', related="reference.add_nama_perusahaan" )
    add_sertifikasi     = fields.Char(string='Sertifikasi Lain', )
    add_pic             = fields.Char(string='Personal Perusahaan Yang sudah pelatihan Auditor ISPO', )
    add_kendali         = fields.Boolean(string='Tim Kendali Internal', )
    add_kendali_jml     = fields.Integer(string='Tim Kendali Internal Jumlah', )
    add_auditor         = fields.Boolean(string='Auditor ISPO Internal', related="reference.add_auditor" )
    add_auditor_jml     = fields.Integer(string='Auditor Internal Jumlah', )

    ispo_kebun          = fields.One2many('tsi.ispo.kebun', 'reference', string="Kebun", index=True)
    ispo_pabrik         = fields.One2many('tsi.ispo.pabrik', 'reference', string="Pabrik", index=True)
    ispo_pemasok        = fields.One2many('tsi.ispo.pemasok', 'reference', string="Pemasok", index=True)
    ispo_sertifikat     = fields.One2many('tsi.ispo.sertifikat', 'reference', string="Sertifikat", index=True, related="reference.ispo_sertifikat")
    
      
    lines_initial       = fields.One2many('tsi.iso.initial', 'reference_id', string="Lines Initial", index=True, related="reference.lines_initial")
    lines_surveillance  = fields.One2many('tsi.iso.surveillance', 'reference_id', string="Lines SUrveillance", index=True, related="reference.lines_surveillance")
    show_ispo           = fields.Boolean(string='Show ISPO', default=False, related="reference.show_ispo")

    #field auditor
    audit_pt = fields.Boolean(string='Audit Per PT 2 Orang' , related="reference.audit_pt")
    nama_audit_pt = fields.Char(string='Nama Auditor', related="reference.nama_audit_pt")
    audit_group = fields.Boolean(string='Audit Per Group 5 Orang' , related="reference.audit_group")
    ics = fields.Boolean(string='ICS untuk Plasma/Swadaya', related="reference.ics")
    nama_ics = fields.Char(string='Nama Auditor PT', related="reference.nama_ics") 
    tgl_perkiraan_mulai = fields.Date(string="Estimated Audit Start Date")
    tgl_perkiraan_selesai = fields.Date(string="Estimated Audit Date End",store=True) 

    def action_create_kontrak(self):
        # Cari record sale.order berdasarkan partner_id
        sale_order = self.env['sale.order'].search([('partner_id', '=', self.customer.id)], limit=1)  # Perbaikan di sini
        
        if not sale_order:
            raise UserError("Tidak ditemukan sale order untuk partner ini.")
        
        # Cari dokumen dari tsi.iso.review yang terkait dengan customer
        reviews = self.env['tsi.ispo.review'].search([('customer', '=', self.customer.id)])
        
        if not reviews:
            raise UserError("Tidak ditemukan dokumen ISO Review untuk partner ini.")
        
        # Update state menjadi 'sent'
        sale_order.write({
            'state': 'sent',
            'application_review_ispo_ids': [(6, 0, reviews.ids)],  # Menambahkan dokumen ke field Many2many
        })

        # Opsional: Tampilkan pesan sukses
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses',
                'message': f"State untuk Sale Order '{sale_order.name}' berhasil diubah menjadi 'Sent' dan dokumen review ditambahkan.",
                'type': 'success',
                'sticky': False,
            },
        }
    

    @api.onchange('show_integreted_yes', 'show_integreted_no')
    def onchange_show_integrated(self):
        if self.integrated_audit == 'YES' and not self.show_integreted_yes:
            self.integrated_audit = False
        elif self.integrated_audit == 'NO' and not self.show_integreted_no:
            self.integrated_audit = False

    @api.onchange('integrated_audit')
    def onchange_integrated_audit(self):
        if self.integrated_audit == 'YES':
            self.show_integreted_yes = True
            self.show_integreted_no = False
        elif self.integrated_audit == 'NO':
            self.show_integreted_yes = False
            self.show_integreted_no = True 

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :
                obj.show_14001 = False
                obj.show_45001 = False
                obj.show_27001 = False
                obj.show_haccp = False
                obj.show_22000 = False  
                obj.show_ispo = False               
                obj.show_salesinfo = False
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISO 14001' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_14001 = True
                    if standard.name == 'ISO 45001' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_45001 = True
                    if standard.name == 'ISO 27001' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_27001 = True
                    if standard.name == 'ISO 22000' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_22000 = True
                    if standard.name == 'HACCP' :
                        if obj.show_salesinfo != True :
                            obj.show_salesinfo = False
                        obj.show_haccp = True
                    if standard.name == 'ISPO' :
                        if obj.show_ispo != True :
                            obj.show_ispo = False
                        obj.show_ispo = True
                    elif standard.name == 'ISO 9001' :
                        obj.show_salesinfo = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.ispo.review')
        vals['name'] = sequence or _('New')
        result = super(ISPOReview, self).create(vals)
        return result

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_quotation_ispo',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_quotation_ispo_view').id,
            'target': 'new'
        }

    # def set_to_running(self):
    #     self.write({'state': 'approved'})            
    #     return return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'iso_review',
    #         'view_id': self.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
    #         'target': [(self.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
    #     }
    
    def set_to_running(self):
        for record in self:
            record.state = 'approved'
            record.finish_date = fields.Datetime.now()
            self.ensure_one()
            action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_review_action')
            action.update({
                'context': {'default_customer': self.customer.id},
                'view_mode': 'form',
                'view_id': self.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
                'target': [(self.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
            })
        return action

    def set_to_reject(self):
        self.write({'state': 'reject'})

        self.reference.state = 'reject'
        for review in self:
            # Update message_follower_ids and message_ids to tsi.iso
            self.env['tsi.iso'].sudo().write({
                'message_follower_ids': [(4, review.id)],  # Add followers from this review
                'message_ids': [(4, msg.id) for msg in review.message_ids],  # Add messages from this review
            })            
        return True

    def set_to_revice(self):
        self.write({'state': 'revice'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_iso_review_action')
        action.update({
            'context': {'default_customer': self.customer.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_iso_review_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_iso_review_view_tree').id, 'tree')],
        })
        return action

    def create_open_quotation(self):
        self.env['sale.order'].create({
            'iso_reference' : self.reference.id,
            'partner_id' : self.customer.id,
        })
        self.reference.compute_state()


    def set_to_closed(self):
        self.create_open_quotation()
        self.write({'state': 'approved'})
        self.write({'finish_date': fields.Datetime.now()})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True