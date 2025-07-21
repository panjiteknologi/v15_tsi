from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime

class AuditReviewISPO(models.Model):
    _name           = 'ops.review.ispo'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Audit Review ISPO'
    _order          = 'id DESC'

    name            = fields.Char(string='Document No', tracking=True)
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference", tracking=True) 
    nama_customer   = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer', tracking=True)   
    # criteria        = fields.Char(string='Criteria', tracking=True)
    objectives      = fields.Text(string='Objectives', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    notification_id = fields.Many2one('audit.notification.ispo', string="Notification", tracking=True)    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    
    report_id       = fields.Many2one('ops.report.ispo', string='Report', tracking=True)
    upload_dokumen  = fields.Binary('Documen Audit')
    review_summary  = fields.One2many('ops.review_summary.ispo', 'review_id', string="Detail", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('approve', 'Approve'),
                            ('reject', 'Reject'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new', tracking=True)
    dokumen_sosialisasi = fields.Binary('Organization Chart')
    file_name1      = fields.Char('Filename', track_visibility='always')
    file_name2      = fields.Char('Filename', track_visibility='always')

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.review.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditReviewISPO, self).create(vals)
        return result


    def set_to_confirm(self):
        self.write({'state': 'approve'})            
        return True
    
    def set_to_reject(self):
        self.write({'state': 'reject'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})
        # sertifikat_obj = self.env['ops.sertifikat']
        # for review in self:
        #     for summary in review.review_summary:
        #         if summary.date:
        #             sertifikat_obj.create({'review_summary_id': summary.id,
        #                                    'ispo_reference' : self.ispo_reference.id,
        #                                    'sales_order_id' : self.sales_order_id.id,
        #                                    'notification_id' : self.notification_id.id,
        #                                    'iso_standard_ids' : [(6, 0, self.iso_standard_ids.ids)]})            
        return True  

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True
    
    def audit_recomendation(self):
        # Code to generate Stage 1 report
        return self.env.ref('v15_tsi.audit_recomendation').report_action(self)

class AuditReviewDetailISPO(models.Model):
    _name           = 'ops.review_summary.ispo'
    _description    = 'Audit Review Summary ISPO'

    review_id       = fields.Many2one('ops.review.ispo', string="Review", ondelete='cascade', index=True, tracking=True)
    remarks         = fields.Char(string='Remarks', tracking=True)
    status          = fields.Selection([
                                        ('reject', 'Reject'),
                                        ('Ok', 'Ok'),
                                    ], string="Status", tracking=True)
    attachment      = fields.Binary('Upload Doc', tracking=True)
    file_name2      = fields.Char('Filename', tracking=True)
    date            = fields.Date(string="Date Notification", default=datetime.today(), tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditReviewDetailISPO, self).create(vals)
        partner = record.review_id
        partner.message_post(body=f"Created Remarks: {record.remarks}, Status: {record.status}, Upload Doc: {record.file_name2}, Date Notification:{record.date}")
        return record

    def write(self, vals):
        res = super(AuditReviewDetailISPO, self).write(vals)
        for record in self:
            partner = record.review_id
            partner.message_post(body=f"Updated Remarks: {record.remarks}, Status: {record.status}, Upload Doc: {record.file_name2}, Date Notification:{record.date}")
        return res

    def unlink(self):
        for record in self:
            partner = record.review_id
            partner.message_post(body=f"Deleted Remarks: {record.remarks}, Status: {record.status}, Upload Doc: {record.file_name2}, Date Notification:{record.date}")
        return super(AuditReviewDetailISPO, self).unlink()
