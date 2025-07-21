from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class AuditSertifikat(models.Model):
    _name           = 'ops.sertifikat'
    _description    = 'Audit Sertifikat'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Document No', tracking=True)
    iso_reference   = fields.Many2one('tsi.iso', string="Reference", tracking=True)    
    criteria        = fields.Char(string='Criteria', tracking=True)
    objectives      = fields.Text(string='Objectives', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    
    notification_id = fields.Many2one('audit.notification', string="Notification", tracking=True)    
    tanggal_terbit  = fields.Date("Terbit Sertifikat", tracking=True)
    upload_sertifikat   = fields.Binary('Upload Sertifikat')
    file_name2      = fields.Char('Filename', tracking=True)
    nomor_sertifikat    = fields.Char('Nomor Sertifikat', tracking=True)
    sertifikat_summary  = fields.One2many('ops.sertifikat_summary', 'sertifikat_id', string="Plan", index=True)
    sertifikat_kan  = fields.One2many('ops.sertifikat_kan', 'sertifikat_id', string="KAN", index=True)
    sertifikat_non  = fields.One2many('ops.sertifikat_non', 'sertifikat_id', string="Non KAN", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new', tracking=True)
    nama_customer       = fields.Many2one('res.partner', string="Organization", related='sales_order_id.partner_id', tracking=True, store=True)
    address             = fields.Char(string="Address", related='nama_customer.office_address', tracking=True, store=True)
    scope               = fields.Text('Scope', related='iso_reference.scope', tracking=True, store=True, default=False)
    # accreditation       = fields.Selection([
    #                         ('KAN',     'KAN'),
    #                         ('Non KAN', 'Non KAN'),
    #                     ], string='Accreditaion')
    # akre                = fields.Selection([
    #                         ('KAN',     'KAN'),
    #                         ('Non', 'Non KAN'),
    #                     ], string='Accreditaion', tracking=True)
    akre_tes = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    review_summary_id = fields.Many2one('ops.review_summary', string='Review Summary', tracking=True)
    initial_date = fields.Date(string='Initial Certification Date', tracking=True)
    issue_date = fields.Date(string='Certification Issue Date', store=True, tracking=True)
    validity_date = fields.Date(string='Certification Validity Date', store=True, tracking=True)
    expiry_date = fields.Date(string='Certification Expiry Date', store=True, tracking=True)
    confirm_date = fields.Datetime(string="Confirm Date", store=True, tracking=True)
    done_date = fields.Datetime(string="Done Date", store=True, tracking=True)

    @api.onchange('initial_date')
    def _onchange_initial_date(self):
        for record in self:
            if record.initial_date:
                # Set issue_date sama dengan initial_date
                record.issue_date = record.initial_date

                # Ubah initial_date ke datetime
                initial_datetime = datetime.combine(record.initial_date, datetime.min.time())

                # Hitung validity_date: +3 tahun - 1 hari
                validity_datetime = initial_datetime + relativedelta(years=3, days=-1)
                record.validity_date = validity_datetime.date()

                # Hitung expiry_date: +1 tahun - 1 hari
                expiry_datetime = initial_datetime + relativedelta(years=1, days=-1)
                record.expiry_date = expiry_datetime.date()
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
        sequence = self.env['ir.sequence'].next_by_code('ops.sertifikat')
        vals['name'] = sequence or _('New')
        if not vals.get('iso_reference'):
            vals['nama_customer'] = self.env.user.partner_id.id  # ✅ Fix di sini
        result = super(AuditSertifikat, self).create(vals)
        return result

    def set_to_confirm(self):
        self.write({
            'state': 'confirm',
            'confirm_date': fields.Datetime.now(),
        }) 
        return True

    def set_to_done(self):
        self.write({
            'state': 'done',
            'done_date': fields.Datetime.now(),
        })

        for rec in self:
            if rec.sales_order_id:
                rec.sales_order_id.generate_crm()
        
        # Update res.partner with certification_lines
        partner = self.nama_customer
        if partner:
            cert_line_vals = {
                'sertifikat_reference': self.id,
                'no_sertifikat': self.nomor_sertifikat,
                'initial_date': self.initial_date,
                'issue_date': self.issue_date,
                'validity_date': self.validity_date,
                'expiry_date': self.expiry_date
            }
            partner.write({
                'certification_lines': [(0, 0, cert_line_vals)]
            })

            # Also update tahun_masuk
            # Ensure issue_date is a datetime.date object
            certification_year = self.issue_date.year if self.issue_date else ''
            tahun_masuk_vals = {
                'partner_id': partner.id,
                'sertifikat_reference': self.id,
                'iso_standard_ids': [(6, 0, self.iso_reference.iso_standard_ids.ids)],
                'issue_date': self.issue_date,
                'certification_year': certification_year,
            }
            # Create new entry in 'tsi.tahun_masuk'
            self.env['tsi.tahun_masuk'].create(tahun_masuk_vals)

        self.message_post(body="Generate CRM Oleh %s" % self.env.user.name)

        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    # def set_to_generate_crm(self):
    #     for rec in self:
    #         if rec.sales_order_id:
    #             rec.sales_order_id.generate_crm()

    #     self.message_post(body="Generate CRM Oleh %s" % self.env.user.name)
    
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
        elif self.akre_tes.name == 'UAF':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'GLOBUS':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'IAF':
            self.sertifikat_kan = [(5, 0, 0)]
        elif self.akre_tes.name == 'SCC':
            self.sertifikat_kan = [(5, 0, 0)]

class AuditSertifikatDetail(models.Model):
    _name           = 'ops.sertifikat_summary'
    _description    = 'Audit Sertifikat Summary'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True, tracking=True)
    summary         = fields.Char(string='Summary', tracking=True)
    status          = fields.Char(string='Status', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditSertifikatDetail, self).create(vals)
        partner = record.sertifikat_id
        partner.message_post(body=f"Created Summary: {record.summary}, Status: {record.status}")
        return record

    def write(self, vals):
        res = super(AuditSertifikatDetail, self).write(vals)
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Updated Summary: {record.summary}, Status: {record.status}")
        return res

    def unlink(self):
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Deleted Summary: {record.summary}, Status: {record.status}")
        return super(AuditSertifikatDetail, self).unlink()

class SertifikatKAN(models.Model):
    _name           = 'ops.sertifikat_kan'
    _description    = 'Audit Sertifikat KAN'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True, tracking=True)
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
        record = super(SertifikatKAN, self).create(vals)
        partner = record.sertifikat_id
        partner.message_post(body=f"Created Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return record

    def write(self, vals):
        res = super(SertifikatKAN, self).write(vals)
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Updated Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return res

    def unlink(self):
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Deleted Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return super(SertifikatKAN, self).unlink()

class SertifikatNonKAN(models.Model):
    _name           = 'ops.sertifikat_non'
    _description    = 'Audit Sertifikat Non KAN'

    sertifikat_id       = fields.Many2one('ops.sertifikat', string="Sertifikat", ondelete='cascade', index=True, tracking=True)
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
        record = super(SertifikatNonKAN, self).create(vals)
        partner = record.sertifikat_id
        partner.message_post(body=f"Created Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return record

    def write(self, vals):
        res = super(SertifikatNonKAN, self).write(vals)
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Updated Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return res

    def unlink(self):
        for record in self:
            partner = record.sertifikat_id
            partner.message_post(body=f"Deleted Accreditaion: {record.status_sertifikat}, Date: {record.date}, Remarks: {record.remarks}")
        return super(SertifikatNonKAN, self).unlink()
