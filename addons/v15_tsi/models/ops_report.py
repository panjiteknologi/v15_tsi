from odoo import models, fields, api, SUPERUSER_ID, _
import logging

# Mendefinisikan logger
_logger = logging.getLogger(__name__)

class AuditReport(models.Model):
    _name           = 'ops.report'
    _description    = 'Audit Report'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Document No', tracking=True)
    iso_reference   = fields.Many2one('tsi.iso', string="Reference", tracking=True)
    plan_reference   = fields.Many2one('ops.plan', string="Plan Reference", tracking=True)
    reference_request_ids = fields.Many2many('tsi.audit.request', string='Audit Request', tracking=True)
    notification_id = fields.Many2one('audit.notification', string="Notification", tracking=True)    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=False)
    audit_request_id    = fields.Many2one('tsi.audit.request', string="Audit Request",  readonly=True)
    program_id          = fields.Many2one('ops.program', string='Program', tracking=True)    

# related, ea_code ???
    customer            = fields.Many2one('res.partner', string="Customer", related='sales_order_id.partner_id', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    contact_person      = fields.Char(string="Contact Person", related='customer.contact_person', tracking=True)
    head_office         = fields.Char(string="Head Office", related='iso_reference.head_office', tracking=True)
    site_office         = fields.Char(string="Site Office", related='iso_reference.site_office', tracking=True)
    off_location        = fields.Char(string="Off Location", related='iso_reference.off_location', tracking=True)
    part_time           = fields.Char(string="Part Time", related='iso_reference.part_time', tracking=True)
    subcon              = fields.Char(string="Sub Contractor", related='iso_reference.subcon', tracking=True)
    unskilled           = fields.Char(string="Unskilled", related='iso_reference.unskilled', tracking=True)
    seasonal            = fields.Char(string="Seasonal", related='iso_reference.seasonal', tracking=True)
    total_emp           = fields.Integer(string="Total Employee", related='customer.total_emp', tracking=True)
    scope               = fields.Char('Scope', related='customer.scope', tracking=True)
    boundaries          = fields.Char('Boundaries', related='customer.boundaries', tracking=True)
    telepon             = fields.Char(string="No Telepon", related='customer.phone', tracking=True)

    ea_code             = fields.Char(string="EA Code", tracking=True)
    type_cient          = fields.Char(string="Seasonal", tracking=True)
    apprev_date         = fields.Date(string="Review Date", tracking=True)    
    contract_date       = fields.Date(string="Contract Date", tracking=True)    


    criteria        = fields.Char(string='Criteria', tracking=True)
    objectives      = fields.Text(string='Objectives', tracking=True)
    upload_dokumen  = fields.Binary('Documen Audit')
    audit_stage           = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('Survillance-1',    'Surveilance 1'),
                            ('Survillance-2',    'Surveilance 2'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], string="Audit Stage", readonly=True, related="plan_reference.audit_stage", tracking=True)
# audit general
    contract_number     = fields.Char('Contract Number', tracking=True)
    audit_start         = fields.Char('Audit Start', tracking=True)
    audit_end           = fields.Char('Audit End', tracking=True)
    certification_type  = fields.Char('Certification Type', tracking=True)
    standards           = fields.Char('Standards', tracking=True)
    audit_criteria      = fields.Char('Audit Criteria', tracking=True)
    audit_method        = fields.Char('Audit Method', tracking=True)

    auditor_lead        = fields.Many2one('hr.employee', string="Nama Auditor", tracking=True)
    auditor_1           = fields.Many2one('hr.employee', string='Auditor 1', tracking=True)
    auditor_2           = fields.Many2one('hr.employee', string='Auditor 2', tracking=True)
    auditor_3           = fields.Many2one('hr.employee', string='Auditor 3', tracking=True)

    kan_1               = fields.Char('Auditor KAN 1', tracking=True)
    kan_2               = fields.Char('Auditor KAN 2', tracking=True)

    audit_objectives    = fields.Many2many('ops.objectives',string='Audit Objectives', tracking=True)
    
# executive summary

    report_summary  = fields.One2many('ops.report_summary', 'report_id', string="Plan", index=True, tracking=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new', tracking=True)
    finding_type = fields.Selection([
        ('no_finding', 'No Finding'),
        ('minor', 'Minor'),
        ('major', 'Major')
    ], string='Finding Type', tracking=True)
    
    no_finding_lines = fields.One2many('ops.report.no_finding.line', 'ops_report_id', string='No Finding Lines')
    minor_lines = fields.One2many('ops.report.minor.line', 'ops_report_id', string='Minor Lines')
    major_lines = fields.One2many('ops.report.major.line', 'ops_report_id', string='Major Lines')
    dokumen_sosialisasi = fields.Binary('Organization Chart', related='sales_order_id.dokumen_sosialisasi')
    file_name1      = fields.Char('Filename', related='sales_order_id.file_name1', tracking=True)
    file_name2      = fields.Char('Filename', tracking=True)
    survillance_type = fields.Selection([
        ('Survillance-1', 'Survillance 1'),
        ('Survillance-2', 'Survillance 2'),
    ], string="Survillance Type", default='Survillance-1')

    recertification_type = fields.Selection([
        ('recertification', 'Recertification'),
    ], string="Recertification Type", default='recertification')

    def set_to_confirm(self):
        _logger.info(f"🚀 set_to_confirm dipanggil untuk report: {self.id}")
        self.write({'state': 'confirm'})
        self.update_ops_review()
        return True

    def update_ops_review(self):
        _logger.info(f"🚀 Mulai update_ops_review untuk report {self.name or self.id}")
        
        if (self.iso_reference or self.reference_request_ids) and self.iso_standard_ids:
            _logger.info(f"ISO Reference: {getattr(self.iso_reference, 'id', 'N/A')}, "
                        f"Reference Requests: {self.reference_request_ids.ids if self.reference_request_ids else []}, "
                        f"ISO Standards: {self.iso_standard_ids.ids}")

            audit_stage = (self.audit_stage or '').lower()
            if audit_stage == 'stage-02':
                self.create_ops_review_for_stage_02()
            elif audit_stage == 'survillance-1':
                self.create_ops_review_for_survillance('Survillance-1')
            elif audit_stage == 'survillance-2':
                self.create_ops_review_for_survillance('Survillance-2')
            elif audit_stage == 'recertification':
                self.create_ops_review_for_recertification()
            else:
                _logger.info(f"❌ Audit Stage tidak dikenali atau bukan salah satu dari yang ditentukan: {self.audit_stage}")
    
    def create_ops_review_for_stage_02(self):
        # Logic untuk 'Stage-02'
        for standard in self.iso_standard_ids:
            vals = {
                'criteria': self.criteria,
                'upload_dokumen': self.upload_dokumen,
                'iso_reference': self.iso_reference.id,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'file_name2': self.file_name2,
                'iso_standard_ids': [(6, 0, [standard.id])],
                'notification_id': self.notification_id.id,
                'report_id': self.id
            }
            # Tambahkan sales_order_id jika ada
            if self.sales_order_id:
                vals['sales_order_id'] = self.sales_order_id.id

            review = self.env['ops.review'].create(vals)
            _logger.info(f"✅ Ops Review created for Stage-02: {review.id}")

    def create_ops_review_for_survillance(self, survillance_type):
        _logger.info(f"✅ Mulai create_ops_review_for_survillance {survillance_type}")
        
        for standard in self.iso_standard_ids:
            vals = {
                'criteria': self.criteria,
                'upload_dokumen': self.upload_dokumen,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'file_name2': self.file_name2,
                'iso_standard_ids': [(6, 0, [standard.id])],
                'notification_id': self.notification_id.id,
                'report_id': self.id,
                'survillance_type': survillance_type
            }

            # Tambahkan iso_reference jika ada
            if self.iso_reference:
                vals['iso_reference'] = self.iso_reference.id
                _logger.info("📌 iso_reference ditambahkan")

            # Tambahkan reference_request_ids jika ada
            if self.reference_request_ids:
                vals['reference_request_ids'] = [(6, 0, self.reference_request_ids.ids)]
                _logger.info("📌 reference_request_ids ditambahkan")

            # Tambahkan sales_order_id jika ada
            if self.sales_order_id:
                vals['sales_order_id'] = self.sales_order_id.id

            # Jika salah satu ada → baru create
            if self.iso_reference or self.reference_request_ids:
                review = self.env['ops.review'].create(vals)
                _logger.info(f"✅ Ops Review created for {survillance_type}: {review.id}")
            else:
                _logger.info("⚠ Ops Review tidak dibuat karena iso_reference & reference_request_ids kosong dua-duanya")


    def create_ops_review_for_recertification(self):
        _logger.info("✅ Mulai create_ops_review_for_recertification")

        for standard in self.iso_standard_ids:
            vals = {
                'criteria': self.criteria,
                'upload_dokumen': self.upload_dokumen,
                'dokumen_sosialisasi': self.dokumen_sosialisasi,
                'file_name1': self.file_name1,
                'file_name2': self.file_name2,
                'iso_standard_ids': [(6, 0, [standard.id])],
                'notification_id': self.notification_id.id,
                'report_id': self.id,
                'recertification_type': 'recertification'
            }

            # Tambahkan iso_reference kalau ada
            if self.iso_reference:
                vals['iso_reference'] = self.iso_reference.id
                _logger.info("📌 iso_reference ditambahkan")

            # Tambahkan reference_request_ids kalau ada
            if self.reference_request_ids:
                vals['reference_request_ids'] = [(6, 0, self.reference_request_ids.ids)]
                _logger.info("📌 reference_request_ids ditambahkan")

            # Tambahkan sales_order_id kalau ada
            if self.sales_order_id:
                vals['sales_order_id'] = self.sales_order_id.id

            # Hanya buat ops.review kalau ada minimal salah satu
            if self.iso_reference or self.reference_request_ids:
                review = self.env['ops.review'].create(vals)
                _logger.info(f"✅ Ops Review created for Recertification: {review.id}")
            else:
                _logger.info("⚠ Ops Review tidak dibuat karena iso_reference & reference_request_ids kosong dua-duanya")

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    # def sync_attachment_audit(self):
    #     for report in self:
    #         partner = report.customer
    #         if not partner:
    #             continue

    #         # Gabungkan semua lines dari ops.report
    #         all_lines = list(report.no_finding_lines) + list(report.minor_lines) + list(report.major_lines)

    #         for line in all_lines:
    #             # Cek apakah attachment audit untuk partner sudah ada dengan file yang sama
    #             exist = self.env['tsi.attachment.audit'].search([
    #                 ('partner_id', '=', partner.id),
    #                 ('file_name1', '=', line.file_name1),
    #                 ('file_name2', '=', line.file_name2),
    #                 ('file_name3', '=', line.file_name3),
    #             ], limit=1)

    #             if not exist:
    #                 # Buat record jika belum ada
    #                 attachment_audit = self.env['tsi.attachment.audit'].create({
    #                     'partner_id': partner.id,
    #                     'audit_plan': line.audit_plan,
    #                     'file_name1': line.file_name1,
    #                     'attendance_sheet': line.attendance_sheet,
    #                     'file_name2': line.file_name2,
    #                     'audit_report': line.audit_report,
    #                     'file_name3': line.file_name3,
    #                 })
    #             else:
    #                 attachment_audit = exist

    #         # === Tambahkan attachment dari ops.review (jika ada) ===
    #         reviews = self.env['ops.review'].search([
    #             ('nama_customer', '=', partner.id)
    #         ])

    #         for review in reviews:
    #             for review_line in review.review_summary:
    #                 # Cek apakah attachment belum dimasukkan ke attachment audit
    #                 if review_line.attachment and not attachment_audit.audit_recomendation:
    #                     attachment_audit.write({
    #                         'audit_recomendation': review_line.attachment,
    #                         'file_name4': review_line.file_name2,
    #                     })

    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': 'Success',
    #             'message': 'Attachment Audit berhasil disinkronkan!',
    #             'type': 'success',
    #         }
    #     }

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.report')
        vals['name'] = sequence or _('New')
        result = super(AuditReport, self).create(vals)
        return result
    
    @api.onchange('finding_type')
    def _onchange_finding_type(self):
        if self.finding_type == 'no_finding':
            self.no_finding_lines = [(5, 0, 0)]
            self.minor_lines = [(5, 0, 0)]
            self.major_lines = [(5, 0, 0)]
        elif self.finding_type == 'minor':
            self.no_finding_lines = [(5, 0, 0)]
            self.minor_lines = [(0, 0, {})]  # Initialize minor lines as needed
            self.major_lines = [(5, 0, 0)]
        elif self.finding_type == 'major':
            self.no_finding_lines = [(5, 0, 0)]
            self.minor_lines = [(0, 0, {})]  # Initialize minor lines as needed
            self.major_lines = [(0, 0, {})]  # Initialize major lines as needed

class OpsReportNoFindingLine(models.Model):
    _name = 'ops.report.no_finding.line'

    ops_report_id = fields.Many2one('ops.report', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)
    review_27001 = fields.Binary(string='Review 27001')
    file_name4 = fields.Char('File Name')

    @api.model
    def create(self, vals):
        record = super(OpsReportNoFindingLine, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportNoFindingLine, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return super(OpsReportNoFindingLine, self).unlink()

class OpsReportMinorLine(models.Model):
    _name = 'ops.report.minor.line'

    ops_report_id = fields.Many2one('ops.report', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    close_findings = fields.Binary(string='Close Findings', tracking=True)
    file_name4 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)
    review_27001 = fields.Binary(string='Review 27001')
    file_name5 = fields.Char('File Name')

    @api.model
    def create(self, vals):
        record = super(OpsReportMinorLine, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportMinorLine, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Temuan:{record.temuan}")
        return super(OpsReportMinorLine, self).unlink()

class OpsReportMajorLine(models.Model):
    _name = 'ops.report.major.line'

    ops_report_id = fields.Many2one('ops.report', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    close_findings = fields.Binary(string='Close Findings', tracking=True)
    file_name4 = fields.Char('File Name', tracking=True)
    verification_audit = fields.Binary(string='Verification Audit', tracking=True)
    file_name5 = fields.Char('File Name', tracking=True)
    verification_attendance = fields.Binary(string='Verification Attendance', tracking=True)
    file_name6 = fields.Char('File Name', tracking=True)
    verifikasi_audit = fields.Binary(string='Verifikasi Audit', tracking=True)
    file_name7 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)
    review_27001 = fields.Binary(string='Review 27001')
    file_name8 = fields.Char('File Name')

    @api.model
    def create(self, vals):
        record = super(OpsReportMajorLine, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Verification Audit: {record.file_name5}, Verification Attendance: {record.file_name6}, Verifikasi Audit: {record.file_name7}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportMajorLine, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Verification Audit: {record.file_name5}, Verification Attendance: {record.file_name6}, Verifikasi Audit: {record.file_name7}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Verification Audit: {record.file_name5}, Verification Attendance: {record.file_name6}, Verifikasi Audit: {record.file_name7}, Temuan:{record.temuan}")
        return super(OpsReportMajorLine, self).unlink()

class AuditReportDetail(models.Model):
    _name           = 'ops.report_summary'
    _description    = 'Audit Report Summary'

    report_id       = fields.Many2one('ops.report', string="Report", ondelete='cascade', index=True, tracking=True)
    summary         = fields.Char(string='Summary', tracking=True)
    status          = fields.Char(string='Status', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditReportDetail, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Summary: {record.summary}, Status: {record.status}")
        return record

    def write(self, vals):
        res = super(AuditReportDetail, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Summary: {record.summary}, Status: {record.status}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Summary: {record.summary}, Status: {record.status}")
        return super(AuditReportDetail, self).unlink()
