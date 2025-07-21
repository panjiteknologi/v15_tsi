from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AuditRequestISPO(models.Model):
    _name           = 'tsi.audit.request.ispo'
    _description    = 'Audit Request ISPO'
    _inherit        = ['mail.thread', 'mail.activity.mixin']
    _order          = 'id DESC'

    name            = fields.Char(string="Document No",  readonly=True, tracking=True)
    audit_stage     = fields.Selection([
                            ('surveilance1',     'Surveillance 1'),
                            ('surveilance2',     'Surveillance 2'),
                            ('recertification', 'Recertification 1'),
                        ], string='Audit Stage', tracking=True, store=True)

    cycle               = fields.Selection([
                            ('cycle1',     'Cycle 1'),
                            ('cycle2',     'Cycle 2'),
                            ('cycle3',     'Cycle 3'),
                        ], string='Cycle', tracking=True)

    audit_stage2        = fields.Selection([
                            ('surveilance3',     'Surveillance 3'),
                            ('surveilance4',     'Surveillance 4'),
                            ('recertification2', 'Recertification 2'),
                        ], string='Audit Stage', tracking=True)

    audit_stage3        = fields.Selection([
                            ('surveilance5',     'Surveillance 5'),
                            ('surveilance6',     'Surveillance 6'),
                            ('recertification3', 'Recertification 3'),
                        ], string='Audit Stage', tracking=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', readonly=False)
    reference           = fields.Many2one('tsi.history_kontrak', string="Reference")
    partner_id          = fields.Many2one('res.partner', 'Company Name', readonly=True, tracking=True)
    office_address      = fields.Char(string='Office Address', related="reference.office_address", readonly=False, tracking=True)
    site_address        = fields.Char(string='Site Project Address', tracking=True)
    invoicing_address   = fields.Char(string="Invoicing Address", related="reference.invoicing_address", readonly=False, tracking=True)
    sales               = fields.Many2one('res.users', string='Sales Person',store=True, related="reference.sales", readonly=False, tracking=True)
    user_id             = fields.Many2one('res.users', string='Created By', index=True, tracking=2, default=lambda self: self.env.user)
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    telp                = fields.Char(string='Telp', related="reference.telp", readonly=False, tracking=True)
    email               = fields.Char(string='Email', related="reference.email", readonly=False, tracking=True)
    website             = fields.Char(string='Website', related="reference.website", readonly=False, tracking=True)
    cellular            = fields.Char(string='Cellular', tracking=True)
    scope               = fields.Char(string='Scope', related="reference.scope", readonly=False, tracking=True)
    boundaries          = fields.Char(string='Boundaries', related="reference.boundaries", readonly=False, tracking=True)
    number_site         = fields.Char(string='Number of Site', related="reference.number_site", readonly=False, tracking=True)
    total_emp           = fields.Char(string='Total Employee', tracking=True)
    total_emp_site      = fields.Char(string='Total Employee Site Project', tracking=True)
    mandays             = fields.Char(string='Mandays', tracking=True)
    tipe_pembayaran     = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',     'Lunas Di Awal'),
                            ('lunasakhir', 'Lunas Di Akhir'),
                        ], string='Tipe Pembayaran', tracking=True)
    is_amendment = fields.Boolean(string="Is Amendment Contract?")
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract",)
    category            = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',   'Silver'),
                            ('gold', 'Gold')
                        ], string='Category', related="reference.category", readonly=False, store=True)
    upload_npwp        = fields.Binary('Upload NPWP')
    file_name1       = fields.Char('Filename NPWP', tracking=True, store=True)
    issue_date = fields.Date(string="Issue Date", default=fields.Date.today, store=True)
    approve_date = fields.Datetime(string="Approve Date", store=True, tracking=True)

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")

    state_sales = fields.Selection([
        ('draft', 'Quotation'),
        ('cliennt_approval', 'Client Approval'),
        ('waiting_verify_operation', 'Waiting Verify Operation'),
        ('sent', 'Confirm to Closing'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Lost'),
    ], string='Status Sales', store=True, tracking=True, related="sale_order_id.state")

    lines_audit_request = fields.One2many('audit_request_ispo.line', 'reference_id', string="Lines Audit Request", index=True, tracking=True)

    # Site Line
    site_ids_ispo    = fields.One2many('crm.site.line', 'crm_site_id_ispo', string="Site Audit Request", index=True, related='reference.site_ids_ispo', readonly=False, tracking=True)
    
    # Mandays Line
    mandays_ids_ispo = fields.One2many('crm.mandays.line', 'crm_mandays_id_ispo', string="Mandays Audit Request", index=True, related='reference.mandays_ids_ispo', readonly=False, tracking=True)

    ispo_reference       = fields.Many2one('tsi.ispo', string="Application Form", readonly=True)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    review_reference_ispo    = fields.Many2many('tsi.ispo.review', string="Review Reference", readonly=True)
    ispo_notification    = fields.Many2one('audit.notification.ispo', string="Notification Reference", readonly=True, tracking=True)
    # crm_reference       = fields.Many2one('tsi.history_kontrak', string="CRM Reference", readonly=True)

    state           =fields.Selection([
                            ('request',         'Request'),
                            ('reject',          'Reject'),
                            ('approve',         'Approve'),
                            # ('approve_so',      'Approve SO'),
                            # ('approve_quot',    'Approve Quotation'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='request')

    state_crm =fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('lanjut', 'Lanjut'),
            ('lost','Loss'),
            ('suspend', 'Suspend'),
            ], string='Status', related="reference.state", store=True)

    referal = fields.Char(string='Referal', related="reference.referal", store=True)

    upload_contract = fields.Binary('Upload Kontrak')
    file_name       = fields.Char('Filename', tracking=True)
    closing_by = fields.Selection([
                ('konsultan',  'Konsultan'),
                ('direct',   'Direct'),
                ], string='Closing By', related="reference.closing_by", readonly=False, tracking=True, store=True)
    transport_by        = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Transport By', related="reference.transport_by", readonly=False, store=True)
    hotel_by            = fields.Selection([
                            ('tsi',  'TSI'),
                            ('klien',   'Klien'),
                        ], string='Akomodasi Hotel By', related="reference.hotel_by", readonly=False, store=True)
    tipe_klien_transport = fields.Selection([
                            ('reimbursement',  'Reimbursement'),
                            ('order_klien',   'Oder By Klien'),
                        ], string='Tipe', related="reference.tipe_klien_transport", readonly=False, store=True)
    tipe_klien_hotel    = fields.Selection([
                            ('reimbursement',  'Reimbursement'),
                            ('order_klien',   'Oder By Klien'),
                        ], string='Tipe', related="reference.tipe_klien_hotel", readonly=False, store=True)
    pic_crm             = fields.Selection([
                            ('dhea',  'Dhea'),
                            ('fauziah',   'Fauziah'),
                            ('mercy',   'Mercy'),
                        ], string='PIC CRM', related="reference.pic_crm", readonly=False, store=True)

    pic_direct          = fields.Char(string='PIC Direct', related="reference.pic_direct", readonly=False, tracking=True)
    email_direct        = fields.Char(string='Email Direct', related="reference.email_direct", readonly=False, tracking=True)
    phone_direct        = fields.Char(string='No Telp Direct', related="reference.phone_direct", readonly=False, tracking=True)

    pic_konsultan1       = fields.Many2one('res.partner', string='PIC Konsultan', related="reference.pic_konsultan1", readonly=False, tracking=True, store=True)
    pic_konsultan       = fields.Char(string='PIC Konsultan', related="reference.pic_konsultan", readonly=False, tracking=True)
    email_konsultan     = fields.Char(string='Email Konsultan', related="reference.email_konsultan", readonly=False, tracking=True)
    phone_konsultan     = fields.Char(string='No Telp Konsultan', related="reference.phone_konsultan", readonly=False, tracking=True)

    note                = fields.Text(string='Note', tracking=True)

    # ISPO
    show_ispo          = fields.Boolean(string='Additional Info', default=False)
    ea_code_ispo       = fields.Many2many('tsi.ea_code', 'rel_audit_request_ea_ispo', string="IAF Code", related="reference.ea_code_ispo", readonly=False, tracking=True)
    accreditation_ispo = fields.Many2one('tsi.iso.accreditation', string="Accreditation", related="reference.accreditation_ispo", readonly=False, tracking=True)

    # tgl_perkiraan_selesai = fields.Date(string="Plan of audit date", related="reference.tgl_perkiraan_selesai", readonly=False, store=True)
    tgl_perkiraan_audit_selesai = fields.Selection(string="Plan of audit date", related="reference.tgl_perkiraan_audit_selesai", readonly=False, store=True)

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('tsi.audit.request.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditRequestISPO, self).create(vals)
        return result

    def set_reject(self):
        self.write({'state': 'reject'})

        self.reference.state = 'reject'
        # self.send_reject_message()
        # self.send_reject_email()          
        return True

    # def send_reject_message(self):
    #     self.ensure_one()

    #     if not self.user_id or not self.user_id.partner_id:
    #         _logger.error("❌ ERROR: No valid partner for user_id: %s", self.user_id.id)
    #         return False

    #     partner_id = self.user_id.partner_id.id

    #     channel = self.env['mail.channel'].sudo().search([
    #         ('channel_partner_ids', 'in', [partner_id]),
    #         ('channel_partner_ids', 'in', [self.env.user.partner_id.id]),
    #         ('channel_type', '=', 'chat')
    #     ], limit=1)

    #     if not channel:
    #         channel = self.env['mail.channel'].sudo().create({
    #             'name': f"Chat with {self.user_id.name}",
    #             'channel_type': 'chat',
    #             'public': 'private',
    #             'channel_partner_ids': [(6, 0, [partner_id, self.env.user.partner_id.id])]
    #         })

    #     standard_list = ", ".join(self.iso_standard_ids.mapped("name")) if self.iso_standard_ids else "No Standards"

    #     message_body = f"""
    #         <p><strong>Audit Request Rejected</strong></p>
    #         <p>Your audit request has been <strong>rejected</strong>.</p>
    #         <p><strong>Request ID:</strong> {self.name}</p>
    #         <p><strong>Company Name:</strong> {self.partner_id.name}</p>
    #         <p><strong>Standard:</strong> {standard_list}</p>
    #         <p><strong>Status:</strong> {self.state}</p>
    #         <p>Thank you.</p>
    #     """

    #     channel.message_post(
    #         body=message_body,
    #         subject="Audit Request Rejected",
    #         message_type="comment",
    #         subtype_xmlid="mail.mt_comment",
    #         author_id=self.env.user.partner_id.id,
    #     )

    #     _logger.info("✅ Direct message sent to partner ID: %s via chat", partner_id)
    #     return True

    # def send_reject_email(self):
    #     self.ensure_one()
    #     template = self.env.ref('v15_tsi.email_template_reject_audit_request')

    #     recipient_email = self.user_id.partner_id.email

    #     if not recipient_email:
    #         _logger.error("❌ ERROR: No valid email found for user_id: %s", self.user_id.id)
    #         return False

    #     _logger.info("✅ Sending rejection email to: %s", recipient_email)

    #     if template:
    #         template.sudo().send_mail(self.id, force_send=True, email_values={'email_to': recipient_email})

    def set_revice(self):
        self.write({'state': 'revice'})
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('v15_tsi.tsi_audit_request_action')
        action.update({
            'context': {'default_customer': self.partner_id.id},
            'view_mode': 'form',
            'view_id': self.env.ref('v15_tsi.tsi_audit_request_ispo_view_tree').id,
            'target': [(self.env.ref('v15_tsi.tsi_audit_request_ispo_view_tree').id, 'tree')],
        })
        return action

    def set_request(self):
        self.write({'state': 'request'})            
        return True

    def set_approve(self):
        self.write({
            'state': 'approve',
            'approve_date': fields.Datetime.now(),
        })                   
        return True

    def create_quotation(self):
        return {
            'name': "Create Quotation",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tsi.wizard_audit_request.ispo',
            'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_request_ispo_view').id,
            'target': 'new'
        }

    def generate_ops(self):
        
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'ispo_reference': self.ispo_reference.id,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            'tipe_pembayaran': self.tipe_pembayaran,
            'nomor_kontrak': self.no_kontrak,  # Mengisi nomor_kontrak
            'nomor_quotation': self.no_kontrak,  # Mengisi nomor_quotation
            'contract_type': self.contract_type,
            # 'template_quotation': self.template_quotation,
            # 'dokumen_sosialisasi': self.dokumen_sosialisasi,
            # 'file_name': self.file_name,
            # 'file_name1': self.file_name1,
        })

        for line in self.lines_audit_request:
            product = line.product_id  
            
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,  
                'product_id': product.id if product else False, 
                'audit_tahapan': line.audit_tahapan,
                'tahun': line.tahun,
                'price_unit': line.price,
            })

        # for line in self.lines_audit_request:
        #     self.env['tsi.order.options'].create({
        #         'ordered_id': sale_order.id,
        #         # 'product_id': line.product_id.id,
        #         'audit_tahapans': line.audit_tahapan,
        #         'tahun_audit': line.tahun,
        #         'price_units': line.price,
        #         # 'product_uom_qty': 1.0,  
        #         # 'tax_id': [(6, 0, line.product_id.taxes_id.ids)] 
        #     })

        # sale_order.action_confirm()

        sale_order.write({'state': 'sent'}) 

        return True

    @api.onchange('iso_standard_ids')
    def _onchange_standards(self):
        for obj in self:
            if obj.iso_standard_ids :
                obj.show_ispo = False               
                for standard in obj.iso_standard_ids :
                    if standard.name == 'ISPO' :
                        if obj.show_ispo != True :
                            obj.show_ispo = False
                        obj.show_ispo = True

    # def generate_ops(self):
    #     if self.tipe_pembayaran:
    #         if self.iso_standard_ids:
    #             notification = self.env['audit.notification'].create({
    #                 'ispo_reference': self.ispo_reference.id,
    #                 'audit_request_id': self.id,
    #                 'tipe_pembayaran': self.tipe_pembayaran,
    #                 'iso_standard_ids': self.iso_standard_ids,
    #                 'customer': self.partner_id.id
    #             })
    #             self.iso_notification = notification.id

    #             for standard in self.iso_standard_ids:
    #                 if self.tipe_pembayaran in ['lunasawal', 'lunasakhir']:
                        
    #                     program = self.env['ops.program'].create({
    #                         'ispo_reference': self.ispo_reference.id,
    #                         'audit_request_id': self.id,
    #                         'iso_standard_ids': [(6, 0, [standard.id])],
    #                         'type_client': self.tipe_pembayaran,
    #                         'notification_id': notification.id,
    #                         'customer': self.partner_id.id
    #                     })

    #                     report = self.env['ops.report'].create({
    #                         'ispo_reference': self.ispo_reference.id,
    #                         'audit_request_id': self.id,
    #                         'iso_standard_ids': [(6, 0, [standard.id])],
    #                         'notification_id': notification.id,
    #                         'customer': self.partner_id.id
    #                     })

    #                 else:
    #                     program = self.env['ops.program'].create({
    #                         'ispo_reference': self.ispo_reference.id,
    #                         'audit_request_id': self.id,
    #                         'iso_standard_ids': [(6, 0, [standard.id])],
    #                         'type_client': self.tipe_pembayaran,
    #                         'notification_id': notification.id,
    #                         'customer': self.partner_id.id
    #                     })

    #             sale_order = self.env['sale.order'].create({
    #                 'partner_id': self.partner_id.id,
    #                 'ispo_reference': self.ispo_reference.id,
    #                 'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
    #                 'tipe_pembayaran': self.tipe_pembayaran,
    #                 'template_quotation' : self.template_quotation,
    #                 'dokumen_sosialisasi' : self.dokumen_sosialisasi,
    #                 'file_name' : self.file_name,
    #                 'file_name1' : self.file_name1,
    #             })

    #             for line in self.lines_audit_request:
    #                 self.env['sale.order.line'].create({
    #                     'order_id': sale_order.id,
    #                     'product_id': line.product_id.id,
    #                     'audit_tahapan': line.audit_tahapan,
    #                     'tahun' : line.tahun,  
    #                     'price_unit': line.price,
    #                     # 'product_uom_qty': 1.0,  
    #                     # 'tax_id': [(6, 0, line.product_id.taxes_id.ids)]  
    #                 })

    #             sale_order.action_confirm()

    #         else:
    #             raise UserError('Tidak ada standar ISO yang terkait.')
    #     else:
    #         raise UserError('Mohon tentukan tipe pembayaran.')

    #     return True


    # def create_sales(self):
    #     self.write({'state': 'approve_quot'})            

    #     return {
    #         'name': "Create Quotation",
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'tsi.wizard_audit_quotation',
    #         'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_quotation_view').id,
    #         'target': 'new'
    #     }

    # def create_quot(self):
    #     self.write({'state': 'approve_so'})            
    #     return {
    #         'name': "Create Quotation",
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'tsi.wizard_audit_quotation',
    #         'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_quotation_view').id,
    #         'target': 'new'
    #     }

class AuditRequestISPOLines(models.Model):
    _name         = 'audit_request_ispo.line'
    _description  = 'Audit Request ISPO Line'
    _inherit      = ['mail.thread', 'mail.activity.mixin']

    reference_id  = fields.Many2one('tsi.audit.request.ispo', string="Reference")
    product_id    = fields.Many2one('product.product', string='Product')
    audit_tahapan = fields.Selection([
        ('Surveillance 1', 'Surveillance 1'),
        ('Surveillance 2', 'Surveillance 2'),
        ('Surveillance 3', 'Surveillance 3'),
        ('Surveillance 4', 'Surveillance 4'),
        ('Surveillance 5', 'Surveillance 5'),
        ('Surveillance 6', 'Surveillance 6'),
        ('Recertification', 'Recertification 1'),
        ('Recertification 2', 'Recertification 2'),
        ('Recertification 3', 'Recertification 3'),
    ], string='Audit Stage', index=True, tracking=True)
    price         = fields.Float(string='Price')
    up_value      = fields.Float(string='Up Value', store=True)
    loss_value    = fields.Float(string='Loss Value', store=True)
    tahun         = fields.Char("Tahun", tracking=True)
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)

    @api.depends('price', 'fee')
    def _compute_percentage(self):
        for record in self:
            if record.price > 0:
                record.percentage = (record.fee / record.price) * 100
            else:
                record.percentage = 0