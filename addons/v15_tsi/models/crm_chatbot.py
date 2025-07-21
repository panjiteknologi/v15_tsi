from odoo import models, fields, api
from datetime import datetime, timedelta


class AuditRequestChatbot(models.Model):
    _name = 'tsi.audit_request_chatbot'
    _description = 'Create Audit Reqiest Chatbot'
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    def _get_default_partner(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).partner_id

    def _get_default_iso(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids')),],limit=1).iso_reference

    def _get_default_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).ispo_reference

    def _get_default_sales(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).sales_reference

    def _get_default_review(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).review_reference

    def _get_default_review_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).review_reference_ispo

    def _get_default_iso(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).iso_standard_ids

    def _get_default_show_iso(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).show_iso_fields

    def _get_default_show_ispo(self):
        return self.env['tsi.history_kontrak'].search([('id','in',self.env.context.get('active_ids'))],limit=1).show_ispo_fields

    audit_stage = fields.Selection([
                            ('surveilance1',     'Surveilance 1'),
                            ('surveilance2',     'Surveilance 2'),
                            ('recertification', 'Recertification'),
                        ], string='Audit Stage', required=True)

    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')

    partner_id          = fields.Many2one('res.partner', 'Company Name')
    invoicing_address   = fields.Char(string="Invoicing Address", )
    office_address      = fields.Char(string='Office Address')
    no_kontrak          = fields.Char(string='Nomor Kontrak')
    telp                = fields.Char(string='Telp')
    email               = fields.Char(string='Email')
    website             = fields.Char(string='Website')
    cellular            = fields.Char(string='Cellular')
    scope               = fields.Char(string='Scope')
    boundaries          = fields.Char(string='Boundaries')
    number_site         = fields.Char(string='Number of Site')
    total_emp           = fields.Char(string='Total Employee')
    mandays             = fields.Char(string='Mandays')
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation")
    is_amendment = fields.Boolean(string="Is Amendment Contract?")
    contract_type = fields.Selection([
        ('new', 'New Contract'),
        ('amendment', 'Amandement Contract'),
    ], string="Contract Type", help="Select the type of contract")

    line_ids = fields.One2many('requestaudit_chatbot.line', 'line_id', string='Audit Lines')
    
    # add new field from doc audit request crm
    contact_person=fields.Char(string='Contact Person')
    project = fields.Char(string='Proyek')
    total_emp_project = fields.Float(string="")
    exp_date =  fields.Date(string='Expired Date')
    change_information = fields.Char(string='Change Information')
    other_notes = fields.Char(string='Other Notes')
    

    iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True, default=_get_default_iso)
    sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True, default=_get_default_sales)
    review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True, default=_get_default_review)
    # crm_reference       = fields.Many2one('tsi.history_kontrak', string="CRM Reference", readonly=True, default=_get_default_crm)
    ispo_reference       = fields.Many2one('tsi.ispo', string="Application Form", readonly=True, default=_get_default_ispo)
    review_reference_ispo    = fields.Many2many('tsi.ispo.review', string="Review Reference", readonly=True, default=_get_default_review_ispo)

    show_iso_fields = fields.Boolean(readonly=True, default=_get_default_show_iso, store=False)
    show_ispo_fields = fields.Boolean(readonly=True, default=_get_default_show_ispo, store=False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # Isi otomatis beberapa field dari partner ke sale.order
            self.office_address = self.partner_id.office_address
            self.invoicing_address = self.partner_id.invoice_address
            self.email = self.partner_id.email
            self.telp = self.partner_id.phone
            self.website = self.partner_id.website
            self.cellular = self.partner_id.mobile
            self.scope = self.partner_id.scope
            self.boundaries = self.partner_id.boundaries
            self.number_site = self.partner_id.number_site
            self.total_emp = self.partner_id.total_emp

    def send(self):
        if self.partner_id:
            original_data = self.env['tsi.audit_request_chatbot'].search([('id', 'in', self.env.context.get('active_ids'))], limit=1)

            changes_log = []

            if self.office_address != original_data.partner_id.office_address:
                changes_log.append(f"Office Address from {original_data.partner_id.office_address} to {self.office_address}")
            if self.invoicing_address != original_data.partner_id.invoice_address:
                changes_log.append(f"Invoicing Address from {original_data.partner_id.invoice_address} to {self.invoicing_address}")
            if self.email != original_data.partner_id.email:
                changes_log.append(f"Email from {original_data.partner_id.email} to {self.email}")
            if self.telp != original_data.partner_id.phone:
                changes_log.append(f"Phone from {original_data.partner_id.phone} to {self.telp}")
            if self.website != original_data.partner_id.website:
                changes_log.append(f"Website from {original_data.partner_id.website} to {self.website}")
            if self.cellular != original_data.partner_id.mobile:
                changes_log.append(f"Cellular from {original_data.partner_id.mobile} to {self.cellular}")
            if self.scope != original_data.partner_id.scope:
                changes_log.append(f"Scope from {original_data.partner_id.scope} to {self.scope}")
            if self.boundaries != original_data.partner_id.boundaries:
                changes_log.append(f"Boundaries from {original_data.partner_id.boundaries} to {self.boundaries}")
            if self.number_site != original_data.partner_id.number_site:
                changes_log.append(f"Number of Sites from {original_data.partner_id.number_site} to {self.number_site}")
            if self.total_emp != original_data.partner_id.total_emp:
                changes_log.append(f"Total Employees from {original_data.partner_id.total_emp} to {self.total_emp}")

            for iso_standard in self.iso_standard_ids:

                iso_form = self.env['tsi.audit.request'].create({
                    'audit_stage': self.audit_stage,
                    'iso_standard_ids': [(6, 0, [iso_standard.id])],
                    'partner_id': self.partner_id.id,
                    'office_address': self.office_address,
                    'invoicing_address': self.invoicing_address,
                    'telp': self.telp,
                    'email': self.email,
                    'website': self.website,
                    'cellular': self.cellular,
                    'scope': self.scope,
                    'boundaries': self.boundaries,
                    'number_site': self.number_site,
                    'no_kontrak': self.no_kontrak,
                    'total_emp': self.total_emp,
                    'mandays': self.mandays,
                    'iso_reference': self.iso_reference.id,
                    'sales_reference': self.sales_reference.id,
                    'review_reference': self.review_reference,
                    'is_amendment': self.is_amendment,
                    'contract_type': self.contract_type,
                })

                if iso_standard.name == "ISPO":

                    ispo_form = self.env['tsi.audit.request.ispo'].create({
                        'audit_stage': self.audit_stage,
                        'iso_standard_ids': [(6, 0, [iso_standard.id])],
                        'partner_id': self.partner_id.id,
                        'office_address': self.office_address,
                        'invoicing_address': self.invoicing_address,
                        'telp': self.telp,
                        'email': self.email,
                        'website': self.website,
                        'cellular': self.cellular,
                        'scope': self.scope,
                        'boundaries': self.boundaries,
                        'number_site': self.number_site,
                        'no_kontrak': self.no_kontrak,
                        'total_emp': self.total_emp,
                        'mandays': self.mandays,
                        'ispo_reference': self.ispo_reference.id,
                        'sales_reference': self.sales_reference.id,
                        'review_reference_ispo': self.review_reference_ispo,
                        'is_amendment': self.is_amendment,
                        'contract_type': self.contract_type,
                    })

                if changes_log:
                    message = '\n'.join(changes_log)
                    iso_form.message_post(body=f"Change :\n{message}")
                    if 'ispo_form' in locals():
                        ispo_form.message_post(body=f"Change :\n{message}")

                product = self.env['product.product'].search([('name', 'ilike', iso_standard.name)], limit=1)

                if not product:
                    
                    product = self.env['product.product'].create({
                        'name': iso_standard.name,
                        'type': 'service',
                        'list_price': 0.0,
                    })

                specific_lines = self.line_ids.filtered(lambda l: l.product_id == product)
                # field_mapping = {
                #     "ISO 9001:2015": ("price_baru_9001", "price_lama_9001", "up_value_9001", "loss_value_9001"),
                #     "ISO 14001:2015": ("price_baru_14001", "price_lama_14001", "up_value_14001", "loss_value_14001"),
                #     "ISO 22000:2018": ("price_baru_22000", "price_lama_22000", "up_value_22000", "loss_value_22000"),
                #     "ISO 22001:2018": ("price_baru_22001", "price_lama_22001", "up_value_22001", "loss_value_22001"),
                #     "ISO 22301:2019": ("price_baru_22301", "price_lama_22301", "up_value_22301", "loss_value_22301"),
                #     "ISO/IEC 27001:2022": ("price_baru_27001", "price_lama_27001", "up_value_27001", "loss_value_27001"),
                #     "ISO 27701:2019": ("price_baru_27701", "price_lama_27701", "up_value_27701", "loss_value_27701"),
                #     "ISO 45001:2018": ("price_baru_45001", "price_lama_45001", "up_value_45001", "loss_value_45001"),
                #     "ISO 37001:2016": ("price_baru_37001", "price_lama_37001", "up_value_37001", "loss_value_37001"),
                #     "ISO 37301:2021": ("price_baru_37301", "price_lama_37301", "up_value_37301", "loss_value_37301"),
                #     "ISO 31000:2018": ("price_baru_31000", "price_lama_31000", "up_value_31000", "loss_value_31000"),
                #     "ISO 13485:2016": ("price_baru_13485", "price_lama_13485", "up_value_13485", "loss_value_13485"),
                #     "ISO 9994:2018": ("price_baru_9994", "price_lama_9994", "up_value_9994", "loss_value_9994"),
                #     "ISPO": ("price_baru_ispo", "price_lama_ispo", "up_value_ispo", "loss_value_ispo"),
                #     "HACCP": ("price_baru_haccp", "price_lama_haccp", "up_value_haccp", "loss_value_haccp"),
                #     "GMP": ("price_baru_gmp", "price_lama_gmp", "up_value_gmp", "loss_value_gmp"),
                #     "SMK3": ("price_baru_smk3", "price_lama_smk3", "up_value_smk3", "loss_value_smk3"),
                # }

                for line in specific_lines:
                    # Create record in audit_request.line for the line item
                    self.env['audit_request.line'].create({
                        'reference_id': iso_form.id,
                        'product_id': product.id,
                        'audit_tahapan': line.audit_tahapan,
                        'price': line.price_baru,
                        'tahun': line.tahun,
                        'fee': line.fee,
                        'percentage': line.percentage
                    })

                    if product.name == "ISPO":
                        # Create record in audit_request_ispo.line for ISPO-specific products
                        self.env['audit_request_ispo.line'].create({
                            'reference_id': ispo_form.id,
                            'product_id': product.id,
                            'audit_tahapan': line.audit_tahapan,
                            'price': line.price_baru,
                            'tahun': line.tahun,
                            'fee': line.fee,
                            'percentage': line.percentage
                        })

                    # field_names = field_mapping.get(line.product_id.name, None)
                    # existing_history = self.env['tsi.audit_request_chatbot'].search([
                    #     ('partner_id', '=', line.line_id.partner_id.id)
                    # ], limit=1)

                    # if field_names:
                    #     price_baru_field, price_lama_field, up_value_field, loss_value_field = field_names
                    #     values = {
                    #         price_baru_field: line.price_baru,
                    #         price_lama_field: line.price_lama,
                    #         up_value_field: line.up_value,
                    #         loss_value_field: line.loss_value,
                    #     }
                    # else:
                    #     values = {
                    #         'price_baru': line.price_baru,
                    #         'price_lama': line.price_lama,
                    #         'up_value': line.up_value,
                    #         'loss_value': line.loss_value,
                    #     }

                    # if existing_history:
                    #     existing_history.write(values)
                    # else:
                    #     self.env['tsi.audit_request_chatbot'].create({
                    #         'partner_id': line.line_id.partner_id.id
                    #         # **values
                    #     })


class RequestAuditChatbotLine(models.Model):
    _name = 'requestaudit_chatbot.line'
    _description = 'Request Audit Chatbot Line'

    line_id = fields.Many2one('tsi.audit_request_chatbot', string='Line', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    audit_tahapan = fields.Selection([
        ('Surveillance 1', 'Surveillance 1'),
        ('Surveillance 2', 'Surveillance 2'),
        ('Recertefication', 'Recertefication'),
        ('Recertification', 'Recertefication'),
    ], string='Audit Stage', index=True, tracking=True)
    price_lama = fields.Float(string='Oldest Price')
    price_baru = fields.Float(string='Latest Price')
    up_value = fields.Float(string='Up Value', compute='_compute_value_difference', store=True)
    loss_value = fields.Float(string='Loss Value', compute='_compute_value_difference', store=True)
    tahun = fields.Char(string='Tahun')
    fee = fields.Float(string='Fee')
    percentage = fields.Float(string='Percentage', compute='_compute_percentage', store=True)

    @api.depends('price_baru', 'fee')
    def _compute_percentage(self):
        for record in self:
            if record.price_baru > record.fee:
                record.percentage = record.fee / (record.price_baru - record.fee)
            else:
                record.percentage = 0

    @api.depends('price_baru', 'price_lama')
    def _compute_value_difference(self):
        for record in self:
            if record.price_baru and record.price_lama:
                if record.price_baru > record.price_lama:
                    record.up_value = record.price_baru - record.price_lama
                    record.loss_value = 0.0
                elif record.price_baru < record.price_lama:
                    record.loss_value = record.price_lama - record.price_baru
                    record.up_value = 0.0
                else:
                    record.up_value = 0.0
                    record.loss_value = 0.0
            else:
                record.up_value = 0.0
                record.loss_value = 0.0
