from datetime import datetime, timedelta
from base64 import standard_b64decode
from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from num2words import num2words
import logging
import roman
from odoo.exceptions import UserError, RedirectWarning, ValidationError, except_orm, Warning

class AuditSertifikatISPO(models.Model):
    _name           = 'ops.sertifikat.ispo'
    _description    = 'Audit Sertifikat ISPO'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Document No', tracking=True)
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference", tracking=True)    
    head_office = fields.Char(string='Head Office', tracking=True)
    site_office = fields.Char(string='Site Office', tracking=True)
    luas_kebun = fields.Float(string='Luas Kebun', tracking=True, digits=(12, 0))
    desa_kebun = fields.Char(string='Desa (Kebun)', tracking=True)
    desa_pabrik = fields.Char(string='Desa (Pabrik)', tracking=True)
    kapasitas = fields.Float(string='Kapasitas', tracking=True, digits=(12, 0))
    lintang_kebun = fields.Char(string='Lintang Kebun', tracking=True)
    bujur_kebun = fields.Char(string='Bujur Kebun', tracking=True)
    lintang_pabrik = fields.Char(string='Lintang Pabrik', tracking=True)
    bujur_pabrik = fields.Char(string='Bujur Pabrik', tracking=True)
    luasan_area = fields.Float(string='Luasan Area (Ha)', tracking=True, digits=(12, 0))
    area_tanam = fields.Float(string='Luas Area Tanam', tracking=True, digits=(12, 0))
    tanaman_menghasilkan = fields.Float(string='Tanaman Menghasilkan', tracking=True, digits=(12, 0))
    tanaman_belum = fields.Float(string='Tanaman Belum Menghasilkan', tracking=True, digits=(12, 0))
    produksi = fields.Float(string='Produksi', tracking=True, digits=(12, 0))
    produktivitas = fields.Float(string='Produktivitas', tracking=True, digits=(12, 0))
    kapasitas_pabrik = fields.Float(string='Kapasitas Pabrik', tracking=True, digits=(12, 0))
    sumber = fields.Selection([
        ('Inti', 'Inti'),
        ('Plasma', 'Plasma'),
        ('Swadaya', 'Swadaya')
    ], string='Sumber Bahan Baku', tracking=True)
    tahun = fields.Char(string='Tahun', tracking=True)
    cpo = fields.Float(string='CPO', tracking=True, digits=(12, 0))
    palm_kernel = fields.Float(string='Palm Kernel', tracking=True, digits=(12, 0))
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    
    notification_id = fields.Many2one('audit.notification.ispo', string="Notification", tracking=True)    
    tanggal_terbit  = fields.Date("Terbit Sertifikat", tracking=True)
    upload_sertifikat   = fields.Binary('Upload Sertifikat')
    file_name2      = fields.Char('Filename', tracking=True)
    nomor_sertifikat    = fields.Char('Nomor Sertifikat', tracking=True)
    sertifikat_summary  = fields.One2many('ops.sertifikat_summary.ispo', 'sertifikat_id', string="Plan", index=True)
    sertifikat_kan  = fields.One2many('ops.sertifikat_kan.ispo', 'sertifikat_id', string="KAN", index=True)
    sertifikat_non  = fields.One2many('ops.sertifikat_non.ispo', 'sertifikat_id', string="Non KAN", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new', tracking=True)
    rantai_pasok = fields.Selection([
        ('Segregasi', 'Segregasi'),
        ('Mass Balance', 'Mass Balance')
    ], string='Model Rantai Pasok', tracking=True)
    nama_customer       = fields.Many2one('res.partner', string="Organization", related='ispo_reference.customer', readonly=False, tracking=True)
    address             = fields.Char(string="Address", related='ispo_reference.office_address', tracking=True)
    # scope               = fields.Text('Scope', related='ispo_reference.scope', tracking=True, readonly=False)
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIK'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True, related='ispo_reference.scope', readonly=False)
    akre_tes = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    review_summary_id = fields.Many2one('ops.review_summary', string='Review Summary', tracking=True)
    initial_date = fields.Date(string='Tanggal Penerbitan Sertifikat', tracking=True)
    # issue_date = fields.Date(string='Certification Issue Date', store=True, tracking=True)
    validity_date = fields.Date(string='Tanggal Berakhir Sertifikat', store=True, tracking=True)
    # expiry_date = fields.Date(string='Certification Expiry Date', store=True, tracking=True)

    luas_kebun_str = fields.Char(string='Luas Kebun (Formatted)', compute='_compute_float_str', store=False)
    kapasitas_str = fields.Char(string='Kapasitas (Formatted)', compute='_compute_float_str', store=False)
    luasan_area_str = fields.Char(string='Luasan Area (Ha) (Formatted)', compute='_compute_float_str', store=False)
    area_tanam_str = fields.Char(string='Luas Area Tanam (Formatted)', compute='_compute_float_str', store=False)
    tanaman_menghasilkan_str = fields.Char(string='Tanaman Menghasilkan (Formatted)', compute='_compute_float_str', store=False)
    tanaman_belum_str = fields.Char(string='Tanaman Belum Menghasilkan (Formatted)', compute='_compute_float_str', store=False)
    produksi_str = fields.Char(string='Produksi (Formatted)', compute='_compute_float_str', store=False)
    produktivitas_str = fields.Char(string='Produktivitas (Formatted)', compute='_compute_float_str', store=False)
    kapasitas_pabrik_str = fields.Char(string='Kapasitas Pabrik (Formatted)', compute='_compute_float_str', store=False)
    cpo_str = fields.Char(string='CPO (Formatted)', compute='_compute_float_str', store=False)
    palm_kernel_str = fields.Char(string='Palm Kernel (Formatted)', compute='_compute_float_str', store=False)

    @api.depends('luas_kebun', 'kapasitas', 'luasan_area', 'area_tanam', 
                 'tanaman_menghasilkan', 'tanaman_belum', 'produksi', 
                 'kapasitas_pabrik', 'cpo', 'palm_kernel')
    def _compute_float_str(self):
        for record in self:
            record.luas_kebun_str = '{:,.0f}'.format(record.luas_kebun).replace(',', '.')
            record.kapasitas_str = '{:,.0f}'.format(record.kapasitas).replace(',', '.')
            record.luasan_area_str = '{:,.0f}'.format(record.luasan_area).replace(',', '.')
            record.area_tanam_str = '{:,.0f}'.format(record.area_tanam).replace(',', '.')
            record.tanaman_menghasilkan_str = '{:,.0f}'.format(record.tanaman_menghasilkan).replace(',', '.')
            record.tanaman_belum_str = '{:,.0f}'.format(record.tanaman_belum).replace(',', '.')
            record.produksi_str = '{:,.0f}'.format(record.produksi).replace(',', '.')
            record.produktivitas_str = '{:,.0f}'.format(record.produktivitas).replace(',', '.')
            record.kapasitas_pabrik_str = '{:,.0f}'.format(record.kapasitas_pabrik).replace(',', '.')
            record.cpo_str = '{:,.0f}'.format(record.cpo).replace(',', '.')
            record.palm_kernel_str = '{:,.0f}'.format(record.palm_kernel).replace(',', '.')

    @api.onchange('initial_date')
    def _onchange_initial_date(self):
        for record in self:
            if record.initial_date:
                initial_datetime = datetime.combine(record.initial_date, datetime.min.time())
                # Tambah 5 tahun lalu mundur 1 hari
                validity_datetime = initial_datetime + relativedelta(years=5, days=-1)
                record.validity_date = validity_datetime.date()
    # initial_date = fields.Date(string='Initial Certification Date', related='review_summary_id.date', readonly=True)
    # issue_date = fields.Date(string='Certification Issued Date', compute='_compute_issue_date', store=True)
    # validity_date = fields.Date(string='Certification Validity Date', compute='_compute_validity_date', store=True)
    # expiry_date = fields.Date(string='Certification Expiry Date', compute='_compute_expiry_date', store=True)

    # @api.depends('initial_date')
    # def _compute_issue_date(self):
    #     for record in self:
    #         if record.initial_date:
    #             initial_date = fields.Datetime.from_string(record.initial_date)
    #             record.issue_date = (initial_date).date()
    #         else:
    #             record.issue_date = False

    # @api.depends('issue_date')
    # def _compute_validity_date(self):
    #     for record in self:
    #         if record.issue_date:
    #             issue_date = fields.Datetime.from_string(record.issue_date)
    #             record.validity_date = (issue_date + timedelta(days=(3*365-1))).date()
    #         else:
    #             record.validity_date = False

    # @api.depends('issue_date')
    # def _compute_expiry_date(self):
    #     for record in self:
    #         if record.issue_date:
    #             issue_date = fields.Datetime.from_string(record.issue_date)
    #             record.expiry_date = (issue_date + timedelta(days=(365-1))).date()
    #         else:
    #             record.expiry_date = False



    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.sertifikat.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditSertifikatISPO, self).create(vals)
        return result

    def set_to_confirm(self):
        self.write({'state': 'confirm'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})
        
        # Update res.partner with certification_lines
        partner = self.nama_customer
        if partner:
            cert_line_vals = {
                'sertifikat_ispo_reference': self.id,
                'no_sertifikat': self.nomor_sertifikat,
                'initial_date': self.initial_date,
                # 'issue_date': self.issue_date,
                'validity_date': self.validity_date,
                # 'expiry_date': self.expiry_date
            }
            partner.write({
                'certification_lines': [(0, 0, cert_line_vals)]
            })

            certification_year = self.initial_date.year if self.initial_date else ''
            tahun_masuk_vals = {
                'partner_id': partner.id,
                'sertifikat_ispo_reference': self.id,
                'iso_standard_ids': [(6, 0, self.ispo_reference.iso_standard_ids.ids)],
                # 'issue_date': self.issue_date,
                'certification_year': certification_year,
            }
            # Create new entry in 'tsi.tahun_masuk'
            self.env['tsi.tahun_masuk'].create(tahun_masuk_vals)

        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    
    @api.onchange('akre_tes')
    def _onchange_akre_tes(self):
        if self.akre_tes.name == 'KAN':
            self.sertifikat_non = [(5, 0, 0)]  
        elif self.akre_tes.name == 'NON KAN':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'Akreditasi 1':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'APMG':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'BARU':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'UAF':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'GLOBUS':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'IAF':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'SCC':
            self.sertifikat_kan = [(5, 0, 0)]

class AuditSertifikatDetailISPO(models.Model):
    _name           = 'ops.sertifikat_summary.ispo'
    _description    = 'Audit Sertifikat Summary ISPO'

    sertifikat_id       = fields.Many2one('ops.sertifikat.ispo', string="Sertifikat", ondelete='cascade', index=True, tracking=True)
    summary         = fields.Char(string='Summary', tracking=True)
    status          = fields.Char(string='Status', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditSertifikatDetailISPO, self).create(vals)
        partner = record.sertifikat_id
        partner.message_post(body=f"Created Summary: {record.summary}, Status: {record.status}")
        return record

    def write(self, vals):
        res = super(AuditSertifikatDetailISPO, self).write(vals)
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Updated Summary: {record.summary}, Status: {record.status}")
        return res

    def unlink(self):
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Deleted Summary: {record.summary}, Status: {record.status}")
        return super(AuditSertifikatDetailISPO, self).unlink()

class SertifikatKANISPO(models.Model):
    _name           = 'ops.sertifikat_kan.ispo'
    _description    = 'Audit Sertifikat KAN ISPO'

    sertifikat_id       = fields.Many2one('ops.sertifikat.ispo', string="Sertifikat", ondelete='cascade', index=True, tracking=True)
    status_sertifikat   = fields.Selection([
                            ('sned_client', 'Draft send To Client'),
                            ('approv_client', 'Draft Approved by Client'),
                            ('register_kan', 'Draft Registered to KAN'),
                            ('approv_kan', 'Draft Approved by KAN'),
                            ('seritifikat_client', 'Certificate send to Client'),
                            ('received_client', 'Certificate received by Client'),
                        ], string='Accreditaion', tracking=True)
    date                = fields.Date(string='Date', tracking=True)
    remarks             = fields.Char(string='Remarks', tracking=True)

    @api.model
    def create(self, vals):
        record = super(SertifikatKANISPO, self).create(vals)
        partner = record.sertifikat_id
        partner.message_post(body=f"Created Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return record

    def write(self, vals):
        res = super(SertifikatKANISPO, self).write(vals)
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Updated Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return res

    def unlink(self):
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Deleted Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return super(SertifikatKANISPO, self).unlink()

class SertifikatNonKANISPO(models.Model):
    _name           = 'ops.sertifikat_non.ispo'
    _description    = 'Audit Sertifikat Non KAN ISPO'

    sertifikat_id       = fields.Many2one('ops.sertifikat.ispo', string="Sertifikat", ondelete='cascade', index=True, tracking=True)
    status_sertifikat   = fields.Selection([
                            ('sned_client', 'Draft send To Client'),
                            ('approv_client', 'Draft Approved by Client'),
                            ('seritifikat_client', 'Certificate send to Client'),
                            ('received_client', 'Certificate received by Client'),
                        ], string='Accreditaion', tracking=True)
    date                = fields.Date(string='Date', tracking=True)
    remarks             = fields.Char(string='Remarks', tracking=True)

    @api.model
    def create(self, vals):
        record = super(SertifikatNonKANISPO, self).create(vals)
        partner = record.sertifikat_id
        partner.message_post(body=f"Created Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return record

    def write(self, vals):
        res = super(SertifikatNonKANISPO, self).write(vals)
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Updated Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return res

    def unlink(self):
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Deleted Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return super(SertifikatNonKANISPO, self).unlink()
