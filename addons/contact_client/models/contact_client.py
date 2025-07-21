from odoo import api, fields, models, _

class ResPartnerClient(models.Model):
    _inherit = "res.partner"

    contact_client_ids = fields.One2many('res.partner.contact.client', 'partner_id', string="Custom Contacts")

    show_internal_notess = fields.Boolean(compute='_compute_show_internal_notess', store=True)
    
    @api.depends('is_company', 'contact_client')
    def _compute_show_internal_notess(self):
        for record in self:
            record.show_internal_notess = record.is_company and record.contact_client

    def open_contact_client_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Custom Contact Wizard',
            'res_model': 'contact.client.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }

class ResPartnerContactClient(models.Model):
    _name = 'res.partner.contact.client'
    _description = 'Custom Contact'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name_client = fields.Many2one('res.partner', string="PIC", domain="[('is_company', '=', False)]", tracking=True)
    phone_client = fields.Char(string="Phone", tracking=True)
    email_client = fields.Char(string="Email", tracking=True)
    address_client = fields.Char(string="Address", tracking=True)
    jabatan = fields.Char(string="Jabatan", tracking=True)
    partner_id = fields.Many2one('res.partner', string="Partner", tracking=True)

    @api.model
    def create(self, vals):
        record = super(ResPartnerContactClient, self).create(vals)
        self._update_history_kontrak_pic(record)
        return record

    def write(self, vals):
        res = super(ResPartnerContactClient, self).write(vals)
        for record in self:
            self._update_history_kontrak_pic(record)
        return res

    def _update_history_kontrak_pic(self, record):
        
        if record.partner_id:
            history_kontrak = self.env['tsi.history_kontrak'].search([('partner_id', '=', record.partner_id.id)], limit=1)

            if history_kontrak:
                pic_record = self.env['history_kontrak.pic'].sudo().search([
                    ('name_pic', '=', record.name_client.id),
                    ('hiskon_id', '=', history_kontrak.id)
                ], limit=1)

                updated_values = {
                    'phone_pic': record.phone_client,
                    'email_pic': record.email_client,
                    'address_pic': record.address_client,
                    'jabatan': record.jabatan,
                }

                if pic_record:
                    if any(pic_record[field] != value for field, value in updated_values.items()):
                        pic_record.sudo().write(updated_values)
                else:
                    
                    self.env['history_kontrak.pic'].sudo().create({
                        'hiskon_id': history_kontrak.id,
                        'name_pic': record.name_client.id,
                        **updated_values,
                        'partner_id': record.partner_id.id,
                    })

            record.partner_id.message_post(body=f"Created/Updated PIC: {record.name_client.name}, Phone: {record.phone_client}, Email: {record.email_client}, Address: {record.address_client}, Jabatan: {record.jabatan}")

    def unlink(self):
        for record in self:
            partner = record.partner_id
            partner.message_post(body=f"Deleted PIC: {record.name_client.name}, Phone: {record.phone_client}, Email: {record.email_client}, Address: {record.address_client}, Jabatan: {record.jabatan}")
        return super(ResPartnerContactClient, self).unlink()

class ContactClientWizard(models.TransientModel):
    _name = 'contact.client.wizard'
    _description = 'Custom Contact Wizard'

    associate_id = fields.Many2one('res.partner', string="PIC", domain="[('is_company', '=', False)]")
    phone_client = fields.Char(string="Phone")
    email_client = fields.Char(string="Email")
    address_client = fields.Char(string="Address")
    jabatan = fields.Char(string="Jabatan")

    @api.onchange('associate_id')
    def _onchange_name_client(self):
        if self.associate_id:
            self.address_client = self.associate_id.office_address
            self.phone_client = self.associate_id.phone
            self.email_client = self.associate_id.email
            self.jabatan = self.associate_id.function
        else:
            self.address_client = False
            self.phone_client = False
            self.email_client = False
            self.jabatan = False

    def action_save(self):
        partner_id = self.env.context.get('default_partner_id')
        if partner_id:
            # Ambil partner yang sedang aktif
            partner = self.env['res.partner'].browse(partner_id)
            phone = partner.phone
            email = partner.email
            office_address = partner.office_address
            function = partner.function
            
            # Update data res.partner dengan data dari wizard
            if self.associate_id:
                self.associate_id.write({
                    'phone': self.phone_client,
                    'email': self.email_client,
                    'office_address': self.address_client,
                    'function': self.jabatan,
                })
            
            # Buat entri baru di res.partner.custom.contacts
            self.env['res.partner.contact.client'].create({
                'name_client': self.associate_id.id,
                'phone_client': self.phone_client,
                'email_client': self.email_client,
                'address_client': self.address_client,
                'jabatan': self.jabatan,
                'partner_id': partner.id,
            })
            
            # Buat entri baru di res.partner.custom.contact
            partner = self.env['res.partner'].browse(partner_id)
            self.env['res.partner.contact.client'].create({
                'name_client': partner.id,
                'phone_client': phone,
                'email_client': email,
                'address_client': office_address,
                'jabatan': function,
                'partner_id': self.associate_id.id,
            })