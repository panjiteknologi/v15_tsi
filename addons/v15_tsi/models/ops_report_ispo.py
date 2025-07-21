from odoo import models, fields, api, SUPERUSER_ID, _

class AuditReportISPO(models.Model):
    _name           = 'ops.report.ispo'
    _description    = 'Audit Report ISPO'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Document No', tracking=True)
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference", tracking=True)
    plan_reference   = fields.Many2one('ops.plan.ispo', string="Plan Reference", tracking=True)
    notification_id = fields.Many2one('audit.notification.ispo', string="Notification", tracking=True)    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)
    audit_request_id    = fields.Many2one('tsi.audit.request', string="Audit Request",  readonly=True)    

# related, ea_code ???
    customer            = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    contact_person      = fields.Char(string="Contact Person", related='ispo_reference.contact_person', tracking=True)
    head_office         = fields.Char(string="Head Office", related='ispo_reference.head_office', tracking=True)
    site_office         = fields.Char(string="Site Office", related='ispo_reference.site_office', tracking=True)
    off_location        = fields.Char(string="Off Location", related='ispo_reference.off_location', tracking=True)
    part_time           = fields.Char(string="Part Time", related='ispo_reference.part_time', tracking=True)
    subcon              = fields.Char(string="Sub Contractor", related='ispo_reference.subcon', tracking=True)
    unskilled           = fields.Char(string="Unskilled", related='ispo_reference.unskilled', tracking=True)
    seasonal            = fields.Char(string="Seasonal", related='ispo_reference.seasonal', tracking=True)
    total_emp           = fields.Integer(string="Total Employee", related='customer.total_emp', tracking=True)
    # scope               = fields.Text('Scope', related='ispo_reference.scope', tracking=True, readonly=False)
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIK'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True, related='ispo_reference.scope')
    boundaries          = fields.Text('Boundaries', related='ispo_reference.boundaries', tracking=True)
    telepon             = fields.Char(string="No Telepon", related='ispo_reference.telepon', tracking=True)

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
                        ], string="Audit Type", readonly=True, related="plan_reference.audit_stage", tracking=True)
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

    audit_objectives    = fields.Many2many('ops.objectives.ispo',string='Audit Objectives', tracking=True)
    
# executive summary

    report_summary  = fields.One2many('ops.report_summary.ispo', 'report_id', string="Plan", index=True, tracking=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new', tracking=True)

    finding_type_ids   = fields.Many2many('ispo.finding.type', string='Finding Type', readonly=False, tracking=True)
    
    no_finding_lines = fields.One2many('ops.report.no_finding.line.ispo', 'ops_report_id', string='No Finding Lines')
    minor_lines = fields.One2many('ops.report.minor.line.ispo', 'ops_report_id', string='Minor Lines')
    observasi_lines = fields.One2many('ops.report.observasi.line.ispo', 'ops_report_id', string='Observasi Lines')
    catatan_legalitas_lines = fields.One2many('ops.report.catatan_legalitas.line.ispo', 'ops_report_id', string='Catatan Legalitas Lines')
    ofi_lines = fields.One2many('ops.report.ofi.line.ispo', 'ops_report_id', string='Oportunity for Improvment Lines')
    major_lines = fields.One2many('ops.report.major.line.ispo', 'ops_report_id', string='Major Lines')
    dokumen_sosialisasi = fields.Binary('Organization Chart', related='sales_order_id.dokumen_sosialisasi')
    file_name1      = fields.Char('Filename', related='sales_order_id.file_name1', tracking=True)
    file_name2      = fields.Char('Filename', tracking=True)

    show_finding_type      = fields.Boolean(string='Additional Info', default=False, tracking=True)
    show_no_finding        = fields.Boolean(string='Show No Finding', default=False)
    show_minor             = fields.Boolean(string='Show Non Confirmity', default=False)
    show_observasi         = fields.Boolean(string='Show Observasi', default=False)
    show_catatan           = fields.Boolean(string='Show Catatan Legalitas', default=False)
    show_ofi               = fields.Boolean(string='Show Oportunity for Improvment', default=False)

    @api.onchange('finding_type_ids')
    def _onchange_finding(self):
        for obj in self:
            if obj.finding_type_ids :
                obj.show_no_finding = False
                obj.show_minor      = False
                obj.show_observasi  = False
                obj.show_catatan    = False
                obj.show_ofi        = False                
                for finding in obj.finding_type_ids :
                    if finding.name == 'No Finding' :
                        if obj.show_finding_type != True :
                            obj.show_finding_type = False
                        obj.show_no_finding = True
                    if finding.name == 'Non Confirmity' :
                        if obj.show_finding_type != True :
                            obj.show_finding_type = False
                        obj.show_minor = True
                    if finding.name == 'Observasi' :
                        if obj.show_finding_type != True :
                            obj.show_finding_type = False
                        obj.show_observasi = True
                    if finding.name == 'Catatan Legalitas' :
                        if obj.show_finding_type != True :
                            obj.show_finding_type = False
                        obj.show_catatan = True
                    if finding.name == 'Oportunity for improvment' :
                        if obj.show_finding_type != True :
                            obj.show_finding_type = False
                        obj.show_ofi = True

    def set_to_confirm(self):
        self.write({'state': 'confirm'})
        self.update_ops_review()            
        return True

    def update_ops_review(self):
        if self.sales_order_id :    
            for standard in self.ispo_reference.iso_standard_ids :
                # Jika tidak ada ops.review.ispo, buat yang baru
                review = self.env['ops.review.ispo'].create({
                # 'report_id': report.id,
                    'criteria' : self.criteria,
                    'upload_dokumen': self.upload_dokumen,
                    'ispo_reference'     : self.ispo_reference.id,
                    'sales_order_id'    : self.sales_order_id.id,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1'    : self.file_name1,
                    'file_name2'    : self.file_name2,
                    'iso_standard_ids'  : standard,
                    'notification_id'   : self.notification_id.id,
                    'report_id'         : self.id   
                })

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True


    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.report.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditReportISPO, self).create(vals)
        return result

class OpsReportNoFindingLineISPO(models.Model):
    _name = 'ops.report.no_finding.line.ispo'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)

    @api.model
    def create(self, vals):
        record = super(OpsReportNoFindingLineISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportNoFindingLineISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return super(OpsReportNoFindingLineISPO, self).unlink()

class OpsReportMinorLineISPO(models.Model):
    _name = 'ops.report.minor.line.ispo'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    close_findings = fields.Binary(string='Close Findings', tracking=True)
    file_name4 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)

    @api.model
    def create(self, vals):
        record = super(OpsReportMinorLineISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportMinorLineISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Temuan:{record.temuan}")
        return super(OpsReportMinorLineISPO, self).unlink()

class OpsReportObservasiISPO(models.Model):
    _name = 'ops.report.observasi.line.ispo'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)

    @api.model
    def create(self, vals):
        record = super(OpsReportObservasiISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportObservasiISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return super(OpsReportObservasiISPO, self).unlink()

class OpsReportCatatanLegalitasISPO(models.Model):
    _name = 'ops.report.catatan_legalitas.line.ispo'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)

    @api.model
    def create(self, vals):
        record = super(OpsReportCatatanLegalitasISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportCatatanLegalitasISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return super(OpsReportCatatanLegalitasISPO, self).unlink()

class OpsReportOfiISPO(models.Model):
    _name = 'ops.report.ofi.line.ispo'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report', tracking=True)
    audit_plan = fields.Binary(string='Audit Plan', tracking=True)
    file_name1 = fields.Char('File Name', tracking=True)
    attendance_sheet = fields.Binary(string='Attendance Sheet', tracking=True)
    file_name2 = fields.Char('File Name', tracking=True)
    audit_report = fields.Binary(string='Audit Report', tracking=True)
    file_name3 = fields.Char('File Name', tracking=True)
    temuan  = fields.Integer(string="Temuan", tracking=True)

    @api.model
    def create(self, vals):
        record = super(OpsReportOfiISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportOfiISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Temuan:{record.temuan}")
        return super(OpsReportOfiISPO, self).unlink()

class OpsReportMajorLineISPO(models.Model):
    _name = 'ops.report.major.line.ispo'

    ops_report_id = fields.Many2one('ops.report.ispo', string='Ops Report', tracking=True)
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

    @api.model
    def create(self, vals):
        record = super(OpsReportMajorLineISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Verification Audit: {record.file_name5}, Verification Attendance: {record.file_name6}, Verifikasi Audit: {record.file_name7}, Temuan:{record.temuan}")
        return record

    def write(self, vals):
        res = super(OpsReportMajorLineISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Verification Audit: {record.file_name5}, Verification Attendance: {record.file_name6}, Verifikasi Audit: {record.file_name7}, Temuan:{record.temuan}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Audit Plan: {record.file_name1}, Attendance Sheet: {record.file_name2}, Audit Report: {record.file_name3}, Close Findings: {record.file_name4}, Verification Audit: {record.file_name5}, Verification Attendance: {record.file_name6}, Verifikasi Audit: {record.file_name7}, Temuan:{record.temuan}")
        return super(OpsReportMajorLineISPO, self).unlink()

class AuditReportDetailISPO(models.Model):
    _name           = 'ops.report_summary.ispo'
    _description    = 'Audit Report Summary ISPO'

    report_id       = fields.Many2one('ops.report.ispo', string="Report", ondelete='cascade', index=True, tracking=True)
    summary         = fields.Char(string='Summary', tracking=True)
    status          = fields.Char(string='Status', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditReportDetailISPO, self).create(vals)
        partner = record.ops_report_id
        partner.message_post(body=f"Created Summary: {record.summary}, Status: {record.status}")
        return record

    def write(self, vals):
        res = super(AuditReportDetailISPO, self).write(vals)
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Updated Summary: {record.summary}, Status: {record.status}")
        return res

    def unlink(self):
        for record in self:
            partner = record.ops_report_id
            partner.message_post(body=f"Deleted Summary: {record.summary}, Status: {record.status}")
        return super(AuditReportDetailISPO, self).unlink()
