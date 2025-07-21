from odoo import models, fields, api, _
from datetime import datetime, timedelta, date

class AuditNotification(models.Model):
    _name           = 'audit.notification'
    _description    = 'Audit Notification'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name                = fields.Char(string='Document No',  readonly=True, tracking=True)
    iso_reference       = fields.Many2one('tsi.iso', string="Reference",  readonly=True)
    customer            = fields.Many2one('res.partner', string="Customer", related='sales_order_id.partner_id', tracking=True)    
    # customer            = fields.Many2one('res.partner', string="Customer", related='iso_reference.customer', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=False)
    audit_request_id    = fields.Many2one('tsi.audit.request', string="Audit Request",  readonly=True)    

    plan_lines          = fields.One2many('ops.plan', 'notification_id', string="Plan", index=True,  readonly=True, tracking=True)
    program_lines       = fields.One2many('ops.program', 'notification_id', string="Program", index=True,  readonly=True, tracking=True)
    report_lines        = fields.One2many('ops.report', 'notification_id', string="Report", index=True,  readonly=True, tracking=True)
    review_lines        = fields.One2many('ops.review', 'notification_id', string="Review", index=True,  readonly=True, tracking=True)
    sertifikat_lines    = fields.One2many('ops.sertifikat', 'notification_id', string="Sertifikat", index=True,  readonly=False, tracking=True)
    delivery_sertifikat_line = fields.One2many('sertifikat.delivery', 'notification_id', string="Delivery Sertifikat", index=True,  readonly=True, tracking=True)

    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Tipe Pembayaran', readonly=False, tracking=True, related="sales_order_id.tipe_pembayaran")

    global_status = fields.Char(string="Status Project", readonly=True)
    tgl_perkiraan_selesai = fields.Date(
        string="Plan of Audit Date",
        compute='_compute_tgl_perkiraan_selesai',  # Computed berdasarkan sales_order_id
        store=True  # Simpan nilainya di database agar tidak hilang
    )

    @api.depends('sales_order_id')
    def _compute_tgl_perkiraan_selesai(self):
        for record in self:
            if record.sales_order_id:
                if record.sales_order_id.tgl_perkiraan_audit_selesai:
                    # Mengonversi string menjadi date
                    tgl_selesai = datetime.strptime(record.sales_order_id.tgl_perkiraan_audit_selesai, "%Y-%m-%d").date()
                    record.tgl_perkiraan_selesai = tgl_selesai
                elif record.sales_order_id.tgl_perkiraan_selesai:
                    # Jika tgl_perkiraan_selesai ada, pakai nilai tersebut
                    record.tgl_perkiraan_selesai = record.sales_order_id.tgl_perkiraan_selesai
            else:
                record.tgl_perkiraan_selesai = False
    
    audit_state = fields.Selection([
        ('program', 'Program'),
        ('Stage-1', 'Stage-1'),
        ('Stage-2', 'Stage-2'),
        ('Surveillance1', 'Surveillance1'),
        ('Surveillance2', 'Surveillance2'),
        ('Recertification', 'Recertification'),
        ('plan', 'Plan'),
        ('report', 'Report'),
        ('recommendation', 'Recommendation'),
        ('certificate', 'Certificate'),
        ('draft', 'Draft'),
        ('done', 'Done')],
        string='Audit Status', compute='_compute_audit_status', store=True)

    # global_status = fields.Char(string='Status', compute='_compute_alias', store=True, tracking=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('audit.notification')
        vals['name'] = sequence or _('New')
        result = super(AuditNotification, self).create(vals)
        return result

    # @api.depends('customer', 'audit_state', 'iso_reference.state')
    # def _compute_alias(self):
    #     for record in self:
    #         alias = ''
    #         customer = record.customer

    #         if not customer:
    #             record.global_status = alias
    #             continue

    #         # Cek di audit.notification (Prioritas Tertinggi)
    #         if not alias:  # Pengecekan untuk model audit.notification
    #             if record.audit_state:
    #                 if record.audit_state == 'draft':
    #                     alias = 'Persetujuan Notifikasi'
    #                 elif record.audit_state == 'plan':
    #                     alias = 'Pengiriman Audit Plan'
    #                 elif record.audit_state == 'program':
    #                     alias = 'Pelaksanaan Audit'
    #                 elif record.audit_state == 'report':
    #                     alias = 'Penyelesaian CAPA'
    #                 elif record.audit_state == 'recommendation':
    #                     alias = 'Pengiriman Draft Sertifikat'
    #                 elif record.audit_state == 'certificate':
    #                     alias = 'Persetujuan Draft Sertifikat'
    #                 elif record.audit_state == 'done':
    #                     alias = 'Kirim Sertifikat'

    #         # Cek di tsi.iso.review (Prioritas Menengah)
    #         if not alias:  # Pengecekan model review hanya jika alias masih kosong
    #             iso_review = self.env['tsi.iso.review'].search([('customer', '=', customer.id)], limit=1)
    #             if iso_review:
    #                 if iso_review.state == 'new':
    #                     alias = 'Review Penugasan'
    #                 elif iso_review.state == 'approved':
    #                     alias = 'Pengiriman Notifikasi'

    #         # Cek di tsi.iso (Prioritas Terendah)
    #         if not alias:  # Pengecekan model tsi.iso hanya jika alias masih kosong
    #             iso_record = self.env['tsi.iso'].search([('customer', '=', customer.id)], limit=1)
    #             if iso_record:
    #                 if iso_record.state in ['new', 'waiting', 'approved']:
    #                     alias = 'Application Form or Request'

    #         record.global_status = alias
    
    @api.depends('program_lines.state', 'plan_lines.state', 'report_lines.state', 'review_lines.state', 'sertifikat_lines.state')
    def _compute_audit_status(self):
        for record in self:
            if any(program.state == 'done' for program in record.program_lines):
                record.audit_state = 'Stage-1'
            if any(program.state == 'done_stage2' for program in record.program_lines):
                record.audit_state = 'Stage-2'
            if any(program.state == 'done_surveillance1' for program in record.program_lines):
                record.audit_state = 'Surveillance1'
            if any(program.state == 'done_surveillance2' for program in record.program_lines):
                record.audit_state = 'Surveillance2'
            if any(program.state == 'done_recertification' for program in record.program_lines):
                record.audit_state = 'Recertification'
            if any(plan.state == 'done' for plan in record.plan_lines):
                record.audit_state = 'plan'
            if any(report.state == 'done' for report in record.report_lines):
                record.audit_state = 'report'
            if any(recommendation.state in ['waiting_finance', 'done'] for recommendation in record.review_lines):
                record.audit_state = 'recommendation'
            # elif any(recommendation.state == 'done' for recommendation in record.review_lines):
            #     record.audit_state = 'Recommendation'
            if any(certificate.state == 'done' for certificate in record.sertifikat_lines):
                record.audit_state = 'certificate'
            if any(program.state == 'new' for program in record.program_lines):
                record.audit_state = 'draft'

    def write(self, vals):
        res = super(AuditNotification, self).write(vals)
        # Set audit status when any related audit status is updated
        if any(key in vals for key in ['program_lines', 'plan_lines', 'report_lines', 'review_lines', 'sertifikat_lines']):
            self._compute_audit_status()
        return res