from odoo import models, fields, api
from datetime import datetime, timedelta
import logging
from docx import Document
from io import BytesIO
import base64
import logging
from odoo.exceptions import UserError
import io  
from odoo.tools.translate import _ 

import json
import requests
from odoo.http import request, Response


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit        = "res.partner"

    is_associate        = fields.Boolean('Is Associate')
    is_franchise        = fields.Boolean('Is Franchise')
    code                = fields.Char('Code', tracking=True)
    associate_lines     = fields.One2many('tsi.associate_partner', 'partner_id', "Associate")
    site_lines          = fields.One2many('tsi.site_partner', 'partner_id', "Sites")
    feedback_lines      = fields.One2many('tsi.partner_feedback', 'nama_perusahaan', "Feedback")
    
    scope           = fields.Char('Scope', tracking=True) 
    boundaries      = fields.Char('Boundaries', tracking=True) 
    number_site     = fields.Char('Number of Site', tracking=True) 
    total_emp       = fields.Integer('Total Employee', tracking=True) 
    # mandays         = fields.Char('Mandays') 
    tgl_sertifikat  = fields.Date(string='Tanggal Sertifikat', tracking=True)
    # harga           = fields.Integer(string='Harga')
    tahun_masuk     = fields.Char('Tahun Aktif', tracking=True)
    invoice_address = fields.Char('Invoice Address', tracking=True)
    office_address  = fields.Char('Office Address', tracking=True)
    contact_person  = fields.Char('Contact Person', tracking=True)
    pic_id          = fields.Many2one('res.partner', string="Existing Contact Person", domain="[('is_company', '=', False)]", tracking=True)
    nomor_customer  = fields.Char(string='Customer ID',  copy=False, tracking=True) 
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string="Standard", compute='_compute_iso_standard_ids', store=True)

    username  = fields.Char('Username', tracking=True)
    password  = fields.Char('Password', tracking=True)
    access_token  = fields.Char('Akses Token')
    # birthday        = fields.Date(string='Birthday', tracking=True)
    
    kategori        = fields.Selection([
                            ('bronze',  'Bronze'),
                            ('silver',  'Silver'),
                            ('gold',    'Gold'),
                        ], string='Kategori', index=True, tracking=True)

    attachment_audit_lines = fields.One2many('tsi.attachment.audit', 'partner_id', string="Attachment Audit", index=True)
    certification_lines = fields.One2many('tsi.partner.certificate', 'partner_id', string="Certification", index=True)
    tahun_masuk_lines = fields.One2many('tsi.tahun_masuk', 'partner_id', string="Tahun Masuk", index=True)
    state = fields.Selection([
    ('belum_valid', 'Belum Valid'),
    ('sudah_valid', 'Sudah Valid'),
    ], string='State', default='belum_valid', tracking=True)
    state_2 = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='Status Certificate Klien', default='New')
    # access_token = fields.Char('Access Token')
    show_internal_notes = fields.Boolean(compute='_compute_show_internal_notes', store=True)
    ea_code_ids = fields.Many2many('tsi.ea_code', string="EA Code")
    status_klien = fields.Selection([
        ('New', 'New'),
        ('active', 'Active'),
        ('suspend', 'Suspend'),
        ('withdraw', 'Withdrawn'),
        ('Re-Active', 'Re-Active'),
        ('Double', 'Double'),
    ], string='State', compute='_compute_status_klien', inverse='_inverse_status_klien', store=True)

    @api.depends('tahun_masuk_lines.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for partner in self:
            # Mengumpulkan semua iso_standard_ids dari tahun_masuk_lines
            all_iso_ids = set()
            for line in partner.tahun_masuk_lines:
                all_iso_ids.update(line.iso_standard_ids.ids)

            # Set iso_standard_ids pada partner
            partner.iso_standard_ids = [(6, 0, list(all_iso_ids))]

    @api.depends('state_2')
    def _compute_status_klien(self):
        """Ambil data otomatis dari state_2."""
        for record in self:
            if record.state_2:
                record.status_klien = record.state_2

    def _inverse_status_klien(self):
        """Sinkronisasi otomatis dari status_klien ke state_2."""
        for record in self:
            if record.status_klien:
                record.state_2 = record.status_klien
    
    @api.depends('is_company', 'contact_client')
    def _compute_show_internal_notes(self):
        for record in self:
            record.show_internal_notes = record.is_company and record.contact_client
            

    def action_valid_partner(self):
        self.write({'state': 'sudah_valid'})
        return True

    def get_iso_review(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Audit',
                'view_mode': 'tree,form',
                'res_model': 'audit.notification',
                'domain': [('customer', '=', self.id)],
                'context': "{'create': False}"
            }

    def get_feedback(self):
            self.ensure_one()
            return {
                'type': 'ir.actions.act_window',
                'name': 'Feedback',
                'view_mode': 'tree,form',
                'res_model': 'tsi.partner_feedback',
                'domain': [('nama_perusahaan', '=', self.id)],
                'context': {'default_nama_perusahaan': self.id }
            }

    def action_generate_attachment_audit_lines(self):
        self.ensure_one()
        if not self.attachment_audit_lines:
            default_lines = [
                (0, 0, {'attachment_name': 'audit_plan'}),
                (0, 0, {'attachment_name': 'attedance_sheet'}),
                (0, 0, {'attachment_name': 'audit_report'}),
                (0, 0, {'attachment_name': 'audit_recomendation'}),
            ]
            self.write({'attachment_audit_lines': default_lines})
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'title': 'Success',
            #         'message': 'Attachment Audit berhasil disinkronkan!',
            #         'type': 'success',
            #         'sticky': False,
            #     }
            # }

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if 'attachment_audit_lines' in fields and not res.get('attachment_audit_lines'):
            res['attachment_audit_lines'] = [
                (0, 0, {'attachment_name': 'audit_plan'}),
                (0, 0, {'attachment_name': 'attedance_sheet'}),
                (0, 0, {'attachment_name': 'audit_report'}),
                (0, 0, {'attachment_name': 'audit_recomendation'}),
            ]
        return res

    # @api.model
    # def create(self, vals):
    #     record = super(ResPartner, self).create(vals)
    #     record.update_pic_history_kontrak()
    #     return record

    # def write(self, vals):
    #     res = super(ResPartner, self).write(vals)
    #     self.update_pic_history_kontrak()
    #     return res

    # def update_pic_history_kontrak(self):
    #     for record in self:
    #         if record.pic_id:
    #             partner_name = record.name
    #             existing_history_kontrak = self.env['tsi.history_kontrak'].search([
    #                 ('partner_id', '=', partner_name),
    #             ], limit=1)
                
    #             if existing_history_kontrak:
    #                 existing_history_kontrak.write({
    #                     'pic': record.pic_id.id,
    #                 })
    #             else:
    #                 self.env['tsi.history_kontrak'].create({
    #                     'partner_id': partner_name,
    #                     'pic': record.pic_id.id,
    #                 })

    # def unlink(self):
    #     for record in self:
    #         if record.pic_id:
    #             partner_name = record.name
    #             history_kontrak = self.env['tsi.history_kontrak'].search([
    #                 ('partner_id', '=', partner_name),
    #                 ('pic', '=', record.pic_id.id)
    #             ])
    #             if history_kontrak:
    #                 history_kontrak.unlink()
    #     return super(ResPartner, self).unlink()

class AttachmentAudit(models.Model):
    _name           = 'tsi.attachment.audit'
    _description    = 'Attachment Audit'

    partner_id = fields.Many2one('res.partner', "Partner", tracking=True)
    # attachment_name = fields.Char(string='Attachment Name')
    attachment_name = fields.Selection([
        ('audit_plan', 'Audit Plan'),
        ('attedance_sheet', 'Attedance Sheet'),
        ('audit_report', 'Audit Report'),
        ('audit_recomendation', 'Audit Recomendation'),
    ], string='Attachment Name', store=True, tracking=True)
    stage_1 = fields.Binary(string='Stage 1', tracking=True)
    file_name_stage1 = fields.Char('File Name Stage 1', tracking=True)
    stage_2 = fields.Binary(string='Stage 2', tracking=True)
    file_name_stage2 = fields.Char('File Name Stage 2', tracking=True)
    sv1 = fields.Binary(string='SV1', tracking=True)
    file_name_sv1 = fields.Char('File Name SV1', tracking=True)
    sv2 = fields.Binary(string='SV2', tracking=True)
    file_name_sv2 = fields.Char('File Name SV2', tracking=True)
    rc1 = fields.Binary(string='RC1', tracking=True)
    file_name_rc1 = fields.Char('File Name RC1', tracking=True)
    sv3 = fields.Binary(string='SV3', tracking=True)
    file_name_sv3 = fields.Char('File Name SV3', tracking=True)
    sv4 = fields.Binary(string='SV4', tracking=True)
    file_name_sv4 = fields.Char('File Name SV4', tracking=True)
    rc2 = fields.Binary(string='RC2', tracking=True)
    file_name_rc2 = fields.Char('File Name RC2', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AttachmentAudit, self).create(vals)
        partner = record.partner_id
        partner.message_post(body=f"Created Attachment Name: {record.attachment_name}, Stage 1: {record.file_name_stage1}, Stage 2: {record.file_name_stage2}, SV1: {record.file_name_sv1}, SV2:{record.file_name_sv2}, RC1: {record.file_name_rc1}, SV3: {record.file_name_sv3}, SV4: {record.file_name_sv4}, RC2:{record.file_name_rc2}")
        return record

    def write(self, vals):
        res = super(AttachmentAudit, self).write(vals)
        for record in self:
            partner = record.partner_id
            partner.message_post(body=f"Updated Attachment Name: {record.attachment_name}, Stage 1: {record.file_name_stage1}, Stage 2: {record.file_name_stage2}, SV1: {record.file_name_sv1}, SV2:{record.file_name_sv2}, RC1: {record.file_name_rc1}, SV3: {record.file_name_sv3}, SV4: {record.file_name_sv4}, RC2:{record.file_name_rc2}")
        return res

    def unlink(self):
        for record in self:
            partner = record.partner_id
            partner.message_post(body=f"Deleted Attachment Name: {record.attachment_name}, Stage 1: {record.file_name_stage1}, Stage 2: {record.file_name_stage2}, SV1: {record.file_name_sv1}, SV2:{record.file_name_sv2}, RC1: {record.file_name_rc1}, SV3: {record.file_name_sv3}, SV4: {record.file_name_sv4}, RC2:{record.file_name_rc2}")
        return super(AttachmentAudit, self).unlink()

class PartnerCertificate(models.Model):
    _name           = 'tsi.partner.certificate'
    _description    = 'certificate'

    partner_id          = fields.Many2one('res.partner', string="Reference", tracking=True)
    sertifikat_reference = fields.Many2one('ops.sertifikat', string="Document No", tracking=True)
    sertifikat_ispo_reference = fields.Many2one('ops.sertifikat.ispo', string="Document No", tracking=True)
    no_sertifikat        = fields.Char('Nomor Sertifikat', tracking=True)    
    standard            = fields.Many2one('tsi.iso.standard', string="Standard",tracking=True )
    initial_date = fields.Date(string='Initial Certification Date',store=True, tracking=True)
    issue_date = fields.Date(string='Certification Issue Date', store=True, tracking=True)
    validity_date = fields.Date(string='Certification Validity Date', store=True, tracking=True)
    expiry_date = fields.Date(string='Certification Expiry Date', store=True, tracking=True)
    tahapan_audit   = fields.Selection([
                            ('initial audit',         'Initial Audit'),
                            ('Surveillance 1', 'Surveillance 1'),
                            ('Surveillance 2', 'Surveillance 2'),
                            ('Surveillance 3', 'Surveillance 3'),
                            ('Surveillance 4', 'Surveillance 4'),
                            ('Surveillance 5', 'Surveillance 5'),
                            ('Surveillance 6', 'Surveillance 6'),
                            ('Recertification', 'Recertification 1'),
                            ('Recertification 2', 'Recertification 2'),
                            ('Recertification 3', 'Recertification 3'),
                        ], string='Tahapan Audit')
    scope           = fields.Char('Scope', related="partner_id.scope", readonly=False)
    boundaries           = fields.Char('Boundaries', related="partner_id.boundaries", readonly=False)
    # harga               = fields.Integer(string='Harga')
    # mandays             = fields.Char(string='Mandays')
    # scope               = fields.Char(string='Scope', related="partner_id.scope")
    # boundaries_id  = fields.Many2many('tsi.iso.boundaries', string="Boundaries", related="partner_id.boundaries_id")
    
    def send_whatsapp_message_custom(self):
        current_date = datetime.today().date()
        three_months_before = current_date + timedelta(days=90)
        two_months_before = current_date + timedelta(days=60)
        one_month_before = current_date + timedelta(days=30)
        expiring_certificates = request.env['tsi.partner.certificate'].search(['|', '|', ('expiry_date', '=', three_months_before),('expiry_date', '=', two_months_before),('expiry_date', '=', one_month_before)])
        numbers = [( cert.partner_id.name, cert.partner_id.pic_id.name, cert.partner_id.mobile,cert.standard.name, cert.tahapan_audit, cert.expiry_date) for cert in expiring_certificates if cert.partner_id.mobile]
        audit_stage_mapping = {
            'initial audit': 'Surveillance 1',
            'Surveillance 1': 'Surveillance 2',
            'Surveillance 2': 'Surveillance 3',
            'Surveillance 3': 'Surveillance 4',
            'Surveillance 4': 'Recertification',
            'Recertification': 'Recertification'
        }
        
        for client, pic, nomor, standard, tahapan_audit, expiry_date in numbers:
            if expiry_date == three_months_before:
                message_template = "expired_3_months"
            elif expiry_date == two_months_before:
                message_template = "expired_2_months"
            elif expiry_date == one_month_before:
                message_template = "expired_1_month"
            else:
                continue 
            expiry_date_str = expiry_date.strftime('%d %B %Y')
            next_tahapan_audit = audit_stage_mapping.get(tahapan_audit, tahapan_audit)
            # _logger.info(f'Client "{client}" nomor "{nomor}" Standard "{standard}" tahapan "{next_tahapan_audit}" dengan template  untuk sertifikat kadaluarsa pada {expiry_date_str}')

            payload = {
                "messaging_product": "whatsapp",
                "to": nomor,
                "type": "template",
                "template": {
                    "name": message_template,
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "header",
                            "parameters":[
                                {
                                    "type": "text",
                                    "text": next_tahapan_audit
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": pic
                                },
                                {
                                    "type": "text",
                                    "text": client
                                },
                                {
                                    "type": "text",
                                    "text": next_tahapan_audit
                                },
                                {
                                    "type": "text",
                                    "text": standard
                                },
                                {
                                    "type": "text",
                                    "text": next_tahapan_audit
                                },
                                {
                                    "type": "text",
                                    "text": expiry_date_str
                                },
                                {
                                    "type": "text",
                                    "text": pic
                                },
                                {
                                    "type": "text",
                                    "text": standard
                                },
                                {
                                    "type": "text",
                                    "text": next_tahapan_audit
                                }
                                
                            ]
                        }
                    ]
                    
                }
            }
        
        url = 'https://graph.facebook.com/v21.0/426469107220591/messages'
        access_token = 'EAAOT6dJD7ZBMBOzdC9eranvzlc4SbFM5RmZCIsKaKyWMKNFZBqmPHQNTZAMop4WcjPMOyuNl8tAlBsM9zi6S5LG7Jys58HXPvqXcMbndmP0mlcBHJz6o3lKKFGmI5CTbWo3o3ZBpN6cqEjbLYUmII2U0LZAshv48ZAiSNKKaXzlZAXY13oCkYBtEEk8JkHaZCbWPskgZDZD'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                _logger.info(f'Client "{client}" nomor "{nomor}" pic "{pic}" Standard "{standard}" tahapan "{next_tahapan_audit}" untuk sertifikat kadaluarsa pada {expiry_date_str}')
    
            else:
                response_data = response.json()
                error_code = response_data.get('error', {}).get('code')
                
                if error_code == 190:
                    _logger.error(f'Token kadaluarsa atau tidak valid untuk nomor {nomor}. Perlu refresh token.')
                else:
                    _logger.error(f'Error sending message to {nomor}: {response_data}')
        except Exception as e:
            _logger.error(f'An error occurred while sending message to {nomor}: {str(e)}')

    
    
    @api.model
    def _check_certificates(self):
        today = datetime.today().date()
        partners = self.env['res.partner'].search([])

        for partner in partners:
            state_set = False
            
            for cert in partner.certification_lines:

                if cert.expiry_date:

                    if cert.expiry_date + timedelta(days=1) < today <= cert.expiry_date + timedelta(weeks=26):
                        partner.state_2 = 'suspend'
                        state_set = True
                    
                    elif today > cert.expiry_date + timedelta(weeks=26):
                        partner.state_2 = 'withdraw'
                        state_set = True
                
                if cert.validity_date and today > cert.validity_date + timedelta(days=1):
                    partner.state_2 = 'withdraw'
                    state_set = True
            
            if not state_set:
                partner.state_2 = 'active'

    @api.model
    def create(self, vals):
        record = super(PartnerCertificate, self).create(vals)
        for record in self:
            partner = record.partner_id

            # Formatting dates
            initial_date_str = record.initial_date.strftime('%d %B %Y') if record.initial_date else ''
            issue_date_str = record.issue_date.strftime('%d %B %Y') if record.issue_date else ''
            validity_date_str = record.validity_date.strftime('%d %B %Y') if record.validity_date else ''
            expiry_date_str = record.expiry_date.strftime('%d %B %Y') if record.expiry_date else ''

            # Message post for each record
            partner.message_post(body=(
                f"Created Document No: {record.sertifikat_reference.name}, Nomor Sertifikat: {record.no_sertifikat}, "
                f"Initial Certification Date: {initial_date_str}, Certification Issue Date: {issue_date_str}, "
                f"Certification Validity Date: {validity_date_str}, Certification Expiry Date: {expiry_date_str}"
            ))
        return record

    def write(self, vals):
        res = super(PartnerCertificate, self).write(vals)
        for record in self:
            partner = record.partner_id

            # Formatting dates
            initial_date_str = record.initial_date.strftime('%d %B %Y') if record.initial_date else ''
            issue_date_str = record.issue_date.strftime('%d %B %Y') if record.issue_date else ''
            validity_date_str = record.validity_date.strftime('%d %B %Y') if record.validity_date else ''
            expiry_date_str = record.expiry_date.strftime('%d %B %Y') if record.expiry_date else ''

            # Message post for each record
            partner.message_post(body=(
                f"Updated Document No: {record.sertifikat_reference.name}, Nomor Sertifikat: {record.no_sertifikat}, "
                f"Initial Certification Date: {initial_date_str}, Certification Issue Date: {issue_date_str}, "
                f"Certification Validity Date: {validity_date_str}, Certification Expiry Date: {expiry_date_str}"
            ))
        return res

    def unlink(self):
        for record in self:
            partner = record.partner_id

            # Formatting dates
            initial_date_str = record.initial_date.strftime('%d %B %Y') if record.initial_date else ''
            issue_date_str = record.issue_date.strftime('%d %B %Y') if record.issue_date else ''
            validity_date_str = record.validity_date.strftime('%d %B %Y') if record.validity_date else ''
            expiry_date_str = record.expiry_date.strftime('%d %B %Y') if record.expiry_date else ''

            # Message post for each record
            partner.message_post(body=(
                f"Deleted Document No: {record.sertifikat_reference.name}, Nomor Sertifikat: {record.no_sertifikat}, "
                f"Initial Certification Date: {initial_date_str}, Certification Issue Date: {issue_date_str}, "
                f"Certification Validity Date: {validity_date_str}, Certification Expiry Date: {expiry_date_str}"
            ))
        return super(PartnerCertificate, self).unlink()

class PartnerTahunMasuk(models.Model):
    _name           = 'tsi.tahun_masuk'
    _description    = 'Tahun Masuk'

    partner_id = fields.Many2one('res.partner', "Partner", tracking=True)
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    sertifikat_reference = fields.Many2one('ops.sertifikat', string="Document No", tracking=True)
    sertifikat_ispo_reference = fields.Many2one('ops.sertifikat.ispo', string="Document No", tracking=True)
    issue_date = fields.Date(string='Certification Issue Date', store=True, tracking=True)
    certification_year = fields.Char(string="Certification Year", tracking=True)
    noted = fields.Char(string="Keterangan", tracking=True)

    @api.model
    def create(self, vals):
        record = super(PartnerTahunMasuk, self).create(vals)
        partner = record.partner_id

        # Menggabungkan nama dari iso_standard_ids
        iso_standards_names = ', '.join(record.iso_standard_ids.mapped('name'))

        partner.message_post(body=(
            f"Created Standards: {iso_standards_names}, "
            f"Document No: {record.sertifikat_reference.name}, "
            f"Certification Issue Date: {record.issue_date}, "
            f"Certification Year: {record.certification_year}"
            f"Keterangan: {record.noted}"
        ))
        return record

    def write(self, vals):
        res = super(PartnerTahunMasuk, self).write(vals)
        for record in self:
            partner = record.partner_id

            # Menggabungkan nama dari iso_standard_ids
            iso_standards_names = ', '.join(record.iso_standard_ids.mapped('name'))

            partner.message_post(body=(
                f"Updated Standards: {iso_standards_names}, "
                f"Document No: {record.sertifikat_reference.name}, "
                f"Certification Issue Date: {record.issue_date}, "
                f"Certification Year: {record.certification_year}"
                f"Keterangan: {record.noted}"
            ))
        return res

    def unlink(self):
        for record in self:
            partner = record.partner_id

            # Menggabungkan nama dari iso_standard_ids
            iso_standards_names = ', '.join(record.iso_standard_ids.mapped('name'))

            partner.message_post(body=(
                f"Deleted Standards: {iso_standards_names}, "
                f"Document No: {record.sertifikat_reference.name}, "
                f"Certification Issue Date: {record.issue_date}, "
                f"Certification Year: {record.certification_year}"
            ))
        return super(PartnerTahunMasuk, self).unlink()

    # @api.depends('issue_date')
    # def _compute_certification_year(self):
    #     for record in self:
    #         if record.issue_date:
    #             record.certification_year = str(record.issue_date.year)
    #         else:
    #             record.certification_year = ''

class AssociatePartner(models.Model):
    _name = 'tsi.associate_partner'
    _description = 'Associate Partner'
    _rec_name = 'associate_id'

    partner_id = fields.Many2one('res.partner', "Partner")
    associate_id = fields.Many2one('res.partner', "Associate")
    associate_code = fields.Char('Associate Code', related='associate_id.code')
    keterangan = fields.Char('Keterangan') 

class SitePartner(models.Model):
    _name           = 'tsi.site_partner'
    _description    = 'Site Partner'
    _rec_name       = 'jenis'

    partner_id      = fields.Many2one('res.partner', "Partner", tracking=True)
    jenis           = fields.Char('Type(HO, Factory etc)', tracking=True) 
    alamat          = fields.Char('Address', tracking=True) 
    telp            = fields.Char('Telp', tracking=True) 
    jumlah_karyawan = fields.Char(string='Total No. of All Employees', tracking=True)
    effective_emp   = fields.Char('Total No. of Effective Employees', tracking=True) 

    @api.model
    def create(self, vals):
        record = super(SitePartner, self).create(vals)
        partner = record.partner_id
        partner.message_post(body=f"Created Type(HO, Factory etc): {record.jenis}, Address: {record.alamat}, Telp: {record.telp}, Total No. of All Employees: {record.jumlah_karyawan}, Total No. of Effective Employees: {record.effective_emp}")
        return record

    def write(self, vals):
        res = super(SitePartner, self).write(vals)
        for record in self:
            partner = record.partner_id
            partner.message_post(body=f"Updated Type(HO, Factory etc): {record.jenis}, Address: {record.alamat}, Telp: {record.telp}, Total No. of All Employees: {record.jumlah_karyawan}, Total No. of Effective Employees: {record.effective_emp}")
        return res

    def unlink(self):
        for record in self:
            partner = record.partner_id
            partner.message_post(body=f"Deleted Type(HO, Factory etc): {record.jenis}, Address: {record.alamat}, Telp: {record.telp}, Total No. of All Employees: {record.jumlah_karyawan}, Total No. of Effective Employees: {record.effective_emp}")
        return super(SitePartner, self).unlink()

class PartnerFeedback(models.Model):
    _name           = 'tsi.partner_feedback'
    _description    = 'Partner Feedback'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nomor Tiket', required=True, readonly=True, default='New')
    nama_pic        = fields.Char(string="Nama PIC", tracking=True)
    nama_perusahaan = fields.Many2one('res.partner', "Nama Perusahaan", domain=[('is_company','=', True)], tracking=True)
    email           = fields.Char(string='Email', tracking=True)
    telepon         = fields.Char(string='Telepon', tracking=True)
    tgl_keluhan     = fields.Date(string='Tanggal Keluhan',default=datetime.now(), tracking=True)
    media_keluhan   = fields.Selection([
                        ('phone','Telepon'),
                        ('email','Email'),
                        ('website','Website'),
                        ],string='Media Keluhan', index=True, tracking=True)
    department      = fields.Selection([
                        ('sales','Sales'),
                        ('crm','CRM'),
                        ('operation','Operation'),
                        ('finance','Finance'),
                        ('it','IT'),
                        ('auditor','Auditor')
                        ],string='Department', index=True, tracking=True)
    jabatan         = fields.Char(string='Jabatan', tracking=True)
    alamat          = fields.Char(string='Alamat', tracking=True)
    standar         = fields.Many2many('tsi.iso.standard',string='Standard',domain=[('standard','=', 'iso')], tracking=True)
    tahap_audit     = fields.Selection([
                            ('initial_audit', 'Initial Audit'),
                            ('surveilance_1', 'Survillance 1'),
                            ('surveilance_2', 'Survillance 2'),
                            ('surveilance_3', 'Survillance 3'),
                            ('surveilance_4', 'Survillance 4'),
                            ('recertification', 'Recertification'),
                        ], string='Tahapan Audit', tracking=True)
    tgl_selesai     = fields.Date(string='Tanggal Selesai', tracking=True)
    diterima_oleh   = fields.Many2one('res.partner',string='Diterima Oleh',domain=[('is_company','=', False)], tracking=True)
    deskripsi       = fields.Char(string='Deskripsi', tracking=True)
    partner_id      = fields.Many2one('res.partner', "Partner")
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            sequence = self.env['ir.sequence'].next_by_code('seq.partner_feedback') or '/'
            current_month = fields.Date.today().month
            roman_month = self._int_to_roman(current_month)
            year = fields.Date.today().strftime('%Y')
            vals['name'] = f'{sequence}/TSI/{roman_month}/{year}'
    
        return super(PartnerFeedback, self).create(vals)

    @staticmethod
    def _int_to_roman(month):
        roman_numerals = {
            1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI",
            7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII"
        }
        return roman_numerals.get(month, "I")
    
    
    def action_send_mail(self):
        self.ensure_one()
        _logger.info("Email from object: %s", self.email)

        template_id = self.env.ref('v15_tsi.email_template_tsi_partner_feedback').id
        template = self.env['mail.template'].browse(template_id)

        report = self.env.ref('v15_tsi.report_feedbanck_customer')
        
        docx_content = report.export_doc_by_template(
            file_template_data=report.file_template_data, 
            file_name_export='Report Keluhan Pelanggan',  
            datas=self
        )

        attachment = self.env['ir.attachment'].create({
            'name': 'Report Keluhan Pelanggan.docx',
            'type': 'binary',
            'datas': base64.b64encode(docx_content),
            'res_model': 'tsi.partner_feedback',
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        })

        ctx = {
            'default_model': 'tsi.partner_feedback',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
            'default_attachment_ids': [(6, 0, [attachment.id])],
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


    # @api.model
    # def create(self, vals):
    #     record = super(PartnerFeedback, self).create(vals)
    #     partner = record.partner_id
    #     partner.message_post(body=f"Created Tanggal: {record.tanggal}, Issue: {record.name}, Description: {record.description}, Status: {record.state}")
    #     return record

    # def write(self, vals):
    #     res = super(PartnerFeedback, self).write(vals)
    #     for record in self:
    #         partner = record.partner_id
    #         partner.message_post(body=f"Updated Tanggal: {record.tanggal}, Issue: {record.name}, Description: {record.description}, Status: {record.state}")
    #     return res

    # def unlink(self):
    #     for record in self:
    #         partner = record.partner_id
    #         partner.message_post(body=f"Deleted Tanggal: {record.tanggal}, Issue: {record.name}, Description: {record.description}, Status: {record.state}")
    #     return super(PartnerFeedback, self).unlink()

class TSICRMAccreditation(models.Model):
    _name           = 'tsi.crm_accreditation'
    _description    = 'CRM Accreditation'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    reference_id    = fields.Many2one('tsi.crm', "reference", tracking=True)
    loss_id         = fields.Many2one('tsi.crm.loss', "Reference Loss")
    lanjut_id         = fields.Many2one('tsi.crm.lanjut', "Reference Lanjut")
    suspend_id         = fields.Many2one('tsi.crm.suspen', "Reference Suspend")
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    accreditation   = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    tahapan_audit   = fields.Char('Tahapan Audit', tracking=True) 
    nilai_ia        = fields.Integer('Nilai', tracking=True) 
    level           = fields.Char('Level', tracking=True) 
    nomor           = fields.Char('Nomor', tracking=True) 
    tanggal         = fields.Char('Tanggal', tracking=True)

    # @api.model
    # def create(self, vals):
    #     record = super(TSICRMAccreditation, self).create(vals)
    #     for rec in record:
    #         rec.message_post(body=f"Created Standards: {rec.iso_standard_ids.name}, Accreditation: {rec.accreditation.name}, Tahapan Audit: {rec.tahapan_audit}, Nilai:{rec.nilai_ia}")
    #     return super(TSICRMAccreditation, self).create(vals)

    # def write(self, vals):
    #     res = super(TSICRMAccreditation, self).write(vals)
    #     for rec in record:
    #         rec.message_post(body=f"Updated Standards: {rec.iso_standard_ids.name}, Accreditation: {rec.accreditation.name}, Tahapan Audit: {rec.tahapan_audit}, Nilai:{rec.nilai_ia}")
    #     return super(TSICRMAccreditation, self).write(vals)

    # def unlink(self):
    #     for rec in record:
    #         rec.message_post(body=f"Deleted Standards: {rec.iso_standard_ids.name}, Accreditation: {rec.accreditation.name}, Tahapan Audit: {rec.tahapan_audit}, Nilai:{rec.nilai_ia}")
    #     return super(TSICRMAccreditation, self).unlink() 

    # def create(self, vals):
    #     record = super(TSICRMAccreditation, self).create(vals)
    #     partner = record.reference_id
    #     partner.message_post(body=f"Created Standards: {record.iso_standard_ids.name}, Accreditation: {record.accreditation.name}, Tahapan Audit: {record.tahapan_audit}, Nilai:{record.nilai_ia}")
    #     return record
    

    # def write(self, vals):
    #     res = super(TSICRMAccreditation, self).write(vals)
    #     for record in self:
    #         partner = record.reference_id
    #         partner.message_post(body=f"Updated Standards: {record.iso_standard_ids.name}, Accreditation: {record.accreditation.name}, Tahapan Audit: {record.tahapan_audit}, Nilai:{record.nilai_ia}")
    #     return res
    

    # def unlink(self):
    #     for record in self:
    #         partner = record.reference_id
    #         partner.message_post(body=f"Deleted Standards: {record.iso_standard_ids.name}, Accreditation: {record.accreditation.name}, Tahapan Audit: {record.tahapan_audit}, Nilai:{record.nilai_ia}")
    #     return super(TSICRMAccreditation, self).unlink() 
    

class TSICRM(models.Model):
    _name           = 'tsi.crm'
    _description    = 'TSI CRM'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    partner_id      = fields.Many2one('res.partner', "Partner", tracking=True)
    contract_number = fields.Char('Contract Number', tracking=True)
    contract_date   = fields.Date(string='Tanggal Kontrak', tracking=True)
    tahapan_audit   = fields.Selection([
                            ('initial',         'Initial Audit'),
                            ('surveilance1',     'Surveilance 1'),
                            ('surveilance2',     'Surveilance 2'),
                            ('recertification', 'Recertification'),
                        ], string='Tahapan Audit', tracking=True)
    accreditation         = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    nilai_ia        = fields.Char('Nilai Kontrak', tracking=True)   
    level           = fields.Char('Level', tracking=True)
    segment_id      = fields.Many2many('res.partner.category', string='Segment', tracking=True)

    nilai_ia        = fields.Char('Initial Audit', tracking=True)
    nilai_sv1       = fields.Char('Surveilance 1', tracking=True)
    nilai_sv2       = fields.Char('Surveilance 2', tracking=True)
    nilai_recert    = fields.Char('Recertification', tracking=True)
    sales_name      = fields.Char('Sales Name', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)

    # iso_reference       = fields.Many2one('tsi.iso', string="Application Form", readonly=True)
    # sales_reference     = fields.Many2one('sale.order', string="Sales Reference", readonly=True)
    # review_reference    = fields.Many2many('tsi.iso.review', string="Review Reference", readonly=True)

    # doctype         = fields.Selection([
    #                         ('iso',  'ISO'),
    #                         ('ispo',   'ISPO'),
    #                     ], string='Doc Type', related='iso_reference.doctype', readonly=True, index=True)

    # state           =fields.Selection([
    #                         ('draft',         'Draft'),
    #                         ('lanjut',         'Lanjut'),
    #                         ('reject',         'Reject'),
    #                         ('approve',         'Approve'),
    #                         ('lost',      'Lost'),
    #                         ('suspend',  'Suspend'),
    #                     ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='draft')

    crm_accreditation       = fields.One2many('tsi.crm_accreditation', 'reference_id', string="Accreditation Lines", index=True, tracking=True)

    # def generate_sales_order(self):
    #     self.env['sale.order'].create({
    #         'partner_id'        : self.partner_id.id,
    #         'iso_reference'     : self.iso_reference.id,
    #         'doctype'           : self.doctype
    #     })
    #     return True

    # def set_to_lanjut(self):
    #     self.write({'state': 'lanjut'})            
    #     return True

    # def set_to_lost(self):
    #     self.write({'state': 'lost'})            
    #     return True

    # def set_to_suspend(self):
    #     self.write({'state': 'suspend'})            
    #     return True

    # def create_audit(self):
    #     return {
    #         'name': "Create Audit",
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'tsi.wizard_audit',
    #         'view_id': self.env.ref('v15_tsi.tsi_wizard_audit_view').id,
    #         'target': 'new'
    #     }


class TSICRMLanjut(models.Model):
    _name           = 'tsi.crm.lanjut'
    _description    = 'Customer Lanjut'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'


    partner_id      = fields.Many2one('res.partner', "Partner", readonly=True)
    contract_number = fields.Char('Nomor Kontrak', readonly=True)
    contract_date   = fields.Date(string='Tanggal Kontrak', readonly=True)
    sales           = fields.Many2one('res.users', string='Sales Person', readonly=True)
    level           = fields.Char(string='Level', readonly=True)
    segment         = fields.Many2many('res.partner.category', string='Segment', readonly=True)
    tahapan_audit   = fields.Selection([
                                ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Survillance 5', 'Survillance 5'),
                                ('Survillance 6', 'Survillance 6'),
                                ('Recertification', 'Recertification 1'),
                                ('Recertification 2', 'Recertification 2'),
                                ('Recertification 3', 'Recertification 3'),
                            ], string='Tahapan Audit')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', store=True, readonly=True)
    nilai_kontrak   = fields.Float(string='Nilai Kontrak', tracking=True)
    nilai_initial_audit = fields.Integer(string='IA', compute='_compute_nilai_initial_audit', store=True)
    nilai_s1 = fields.Integer(string='SV1', compute='_compute_nilai_s1', store=True)
    nilai_s2 = fields.Integer(string='SV2', compute='_compute_nilai_s2', store=True)
    nilai_s3 = fields.Integer(string='SV3', compute='_compute_nilai_s3', store=True)
    nilai_s4 = fields.Integer(string='SV4', compute='_compute_nilai_s4', store=True)
    nilai_s5 = fields.Integer(string='SV5', compute='_compute_nilai_s5', store=True)
    nilai_s6 = fields.Integer(string='SV6', compute='_compute_nilai_s6', store=True)
    nilai_recertification = fields.Integer(string='RC1', compute='_compute_nilai_recertification', store=True)
    nilai_recertification2 = fields.Integer(string='RC2', compute='_compute_nilai_recertification2', store=True)
    nilai_recertification3 = fields.Integer(string='RC3', compute='_compute_nilai_recertification3', store=True)
    crm_accreditations  = fields.One2many('tsi.crm_accreditation', 'lanjut_id', string="Accreditation Lines", index=True)

    # ISO 9001
    price_baru_9001      = fields.Float(string='Current Price ISO 9001')
    price_lama_9001      = fields.Float(string='Previous Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Current Price ISO 14001')
    price_lama_14001      = fields.Float(string='Previous Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Current Price ISO 22000')
    price_lama_22000      = fields.Float(string='Previous Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 22001
    price_baru_22001      = fields.Float(string='Current Price ISO 22001')
    price_lama_22001      = fields.Float(string='Previous Price ISO 22001')
    up_value_22001        = fields.Float(string='Up Value ISO 22001')
    loss_value_22001      = fields.Float(string='Loss Value ISO 22001')

    # ISO 22301
    price_baru_22301      = fields.Float(string='Current Price ISO 22301')
    price_lama_22301      = fields.Float(string='Previous Price ISO 22301')
    up_value_22301        = fields.Float(string='Up Value ISO 22301')
    loss_value_22301      = fields.Float(string='Loss Value ISO 22301')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Current Price ISO 27001')
    price_lama_27001      = fields.Float(string='Previous Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 27701
    price_baru_27701      = fields.Float(string='Current Price ISO 27701')
    price_lama_27701      = fields.Float(string='Previous Price ISO 27701')
    up_value_27701        = fields.Float(string='Up Value ISO 27701')
    loss_value_27701      = fields.Float(string='Loss Value ISO 27701')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Current Price ISO 45001')
    price_lama_45001      = fields.Float(string='Previous Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Current Price ISO 37001')
    price_lama_37001      = fields.Float(string='Previous Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 37301
    price_baru_37301      = fields.Float(string='Current Price ISO 37301')
    price_lama_37301      = fields.Float(string='Previous Price ISO 37301')
    up_value_37301        = fields.Float(string='Up Value ISO 37301')
    loss_value_37301      = fields.Float(string='Loss Value ISO 37301')

    # ISO 31000
    price_baru_31000      = fields.Float(string='Current Price ISO 31000')
    price_lama_31000      = fields.Float(string='Previous Price ISO 31000')
    up_value_31000        = fields.Float(string='Up Value ISO 31000')
    loss_value_31000      = fields.Float(string='Loss Value ISO 31000')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Current Price ISO 13485')
    price_lama_13485      = fields.Float(string='Previous Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Current Price ISO 9994')
    price_lama_9994      = fields.Float(string='Previous Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Current Price ISPO')
    price_lama_ispo      = fields.Float(string='Previous Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')

    # HACCP
    price_baru_haccp      = fields.Float(string='Current Price HACCP')
    price_lama_haccp      = fields.Float(string='Previous Price HACCP')
    up_value_haccp        = fields.Float(string='Up Value HACCP')
    loss_value_haccp      = fields.Float(string='Loss Value HACCP')

    # GMP
    price_baru_gmp      = fields.Float(string='Current Price GMP')
    price_lama_gmp      = fields.Float(string='Previous Price GMP')
    up_value_gmp        = fields.Float(string='Up Value GMP')
    loss_value_gmp      = fields.Float(string='Loss Value GMP')

    # SMK3
    price_baru_smk3      = fields.Float(string='Current Price SMK3')
    price_lama_smk3      = fields.Float(string='Previous Price SMK3')
    up_value_smk3        = fields.Float(string='Up Value SMK3')
    loss_value_smk3      = fields.Float(string='Loss Value SMK3')

    # @api.depends('crm_accreditations.iso_standard_ids')
    # def _compute_iso_standard_ids(self):
    #     for record in self:
    #         # Mengumpulkan semua ISO standard IDs dari baris crm_accreditations
    #         iso_standard_ids = record.crm_accreditations.mapped('iso_standard_ids')
    #         # Hanya ambil ID (integer) dari daftar ISO standards
    #         all_iso_standard_ids = set(iso_standard_ids.mapped('id'))
    #         record.iso_standard_ids = [(6, 0, list(all_iso_standard_ids))]

    # @api.depends('crm_accreditations.accreditation')
    # def _compute_accreditation(self):
    #     for record in self:

    #         all_accreditations = record.crm_accreditations.mapped('accreditation')
            
    #         if all_accreditations:
                
    #             record.accreditation = all_accreditations[0]
    #         else:
    #             record.accreditation = False
    
    @api.depends('crm_accreditations')
    def _compute_nilai_initial_audit(self):
        for record in self:
            record.nilai_initial_audit = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Initial Audit').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s1(self):
        for record in self:
            record.nilai_s1 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s2(self):
        for record in self:
            record.nilai_s2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s3(self):
        for record in self:
            record.nilai_s3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 3').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s4(self):
        for record in self:
            record.nilai_s4 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 4').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s5(self):
        for record in self:
            record.nilai_s5 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 5').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s6(self):
        for record in self:
            record.nilai_s6 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 6').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification(self):
        for record in self:
            record.nilai_recertification = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification2(self):
        for record in self:
            record.nilai_recertification2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification3(self):
        for record in self:
            record.nilai_recertification3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 3').mapped('nilai_ia')
            ) or False

class TSICRMLoss(models.Model):
    _name           = 'tsi.crm.loss'
    _description    = 'Customer Lanjut'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    alasan          = fields.Many2one('crm.alasan', string="Alasan", readonly=True)
    partner_id      = fields.Many2one('res.partner', "Partner", readonly=True)
    contract_number = fields.Char('Nomor Kontrak', readonly=True)
    contract_date   = fields.Date(string='Tanggal Kontrak', readonly=True)
    sales           = fields.Many2one('res.users', string='Sales Person', readonly=True)
    level           = fields.Char(string='Level', readonly=True)
    segment         = fields.Many2many('res.partner.category', string='Segment', readonly=True)
    nilai_kontrak   = fields.Float(string='Nilai Kontrak', tracking=True)
    tahapan_audit   = fields.Selection([
                                ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Survillance 5', 'Survillance 5'),
                                ('Survillance 6', 'Survillance 6'),
                                ('Recertification', 'Recertification 1'),
                                ('Recertification 2', 'Recertification 2'),
                                ('Recertification 3', 'Recertification 3'),
                            ], string='Tahapan Audit')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', store=True, readonly=True)
    nilai_initial_audit = fields.Integer(string='IA', compute='_compute_nilai_initial_audit', store=True)
    nilai_s1 = fields.Integer(string='SV1', compute='_compute_nilai_s1', store=True)
    nilai_s2 = fields.Integer(string='SV2', compute='_compute_nilai_s2', store=True)
    nilai_s3 = fields.Integer(string='SV3', compute='_compute_nilai_s3', store=True)
    nilai_s4 = fields.Integer(string='SV4', compute='_compute_nilai_s4', store=True)
    nilai_s5 = fields.Integer(string='SV5', compute='_compute_nilai_s5', store=True)
    nilai_s6 = fields.Integer(string='SV6', compute='_compute_nilai_s6', store=True)
    nilai_recertification = fields.Integer(string='RC1', compute='_compute_nilai_recertification', store=True)
    nilai_recertification2 = fields.Integer(string='RC2', compute='_compute_nilai_recertification2', store=True)
    nilai_recertification3 = fields.Integer(string='RC3', compute='_compute_nilai_recertification3', store=True)
    crm_accreditations  = fields.One2many('tsi.crm_accreditation', 'loss_id', string="Accreditation Lines", index=True)

    # ISO 9001
    price_baru_9001      = fields.Float(string='Current Price ISO 9001')
    price_lama_9001      = fields.Float(string='Previous Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Current Price ISO 14001')
    price_lama_14001      = fields.Float(string='Previous Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Current Price ISO 22000')
    price_lama_22000      = fields.Float(string='Previous Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 22001
    price_baru_22001      = fields.Float(string='Current Price ISO 22001')
    price_lama_22001      = fields.Float(string='Previous Price ISO 22001')
    up_value_22001        = fields.Float(string='Up Value ISO 22001')
    loss_value_22001      = fields.Float(string='Loss Value ISO 22001')

    # ISO 22301
    price_baru_22301      = fields.Float(string='Current Price ISO 22301')
    price_lama_22301      = fields.Float(string='Previous Price ISO 22301')
    up_value_22301        = fields.Float(string='Up Value ISO 22301')
    loss_value_22301      = fields.Float(string='Loss Value ISO 22301')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Current Price ISO 27001')
    price_lama_27001      = fields.Float(string='Previous Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 27701
    price_baru_27701      = fields.Float(string='Current Price ISO 27701')
    price_lama_27701      = fields.Float(string='Previous Price ISO 27701')
    up_value_27701        = fields.Float(string='Up Value ISO 27701')
    loss_value_27701      = fields.Float(string='Loss Value ISO 27701')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Current Price ISO 45001')
    price_lama_45001      = fields.Float(string='Previous Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Current Price ISO 37001')
    price_lama_37001      = fields.Float(string='Previous Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 37301
    price_baru_37301      = fields.Float(string='Current Price ISO 37301')
    price_lama_37301      = fields.Float(string='Previous Price ISO 37301')
    up_value_37301        = fields.Float(string='Up Value ISO 37301')
    loss_value_37301      = fields.Float(string='Loss Value ISO 37301')

    # ISO 31000
    price_baru_31000      = fields.Float(string='Current Price ISO 31000')
    price_lama_31000      = fields.Float(string='Previous Price ISO 31000')
    up_value_31000        = fields.Float(string='Up Value ISO 31000')
    loss_value_31000      = fields.Float(string='Loss Value ISO 31000')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Current Price ISO 13485')
    price_lama_13485      = fields.Float(string='Previous Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Current Price ISO 9994')
    price_lama_9994      = fields.Float(string='Previous Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Current Price ISPO')
    price_lama_ispo      = fields.Float(string='Previous Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')

    # HACCP
    price_baru_haccp      = fields.Float(string='Current Price HACCP')
    price_lama_haccp      = fields.Float(string='Previous Price HACCP')
    up_value_haccp        = fields.Float(string='Up Value HACCP')
    loss_value_haccp      = fields.Float(string='Loss Value HACCP')

    # GMP
    price_baru_gmp      = fields.Float(string='Current Price GMP')
    price_lama_gmp      = fields.Float(string='Previous Price GMP')
    up_value_gmp        = fields.Float(string='Up Value GMP')
    loss_value_gmp      = fields.Float(string='Loss Value GMP')

    # SMK3
    price_baru_smk3      = fields.Float(string='Current Price SMK3')
    price_lama_smk3      = fields.Float(string='Previous Price SMK3')
    up_value_smk3        = fields.Float(string='Up Value SMK3')
    loss_value_smk3      = fields.Float(string='Loss Value SMK3')

    @api.depends('crm_accreditations.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for record in self:
            # Mengumpulkan semua ISO standard IDs dari baris crm_accreditations
            iso_standard_ids = record.crm_accreditations.mapped('iso_standard_ids')
            # Hanya ambil ID (integer) dari daftar ISO standards
            all_iso_standard_ids = set(iso_standard_ids.mapped('id'))
            record.iso_standard_ids = [(6, 0, list(all_iso_standard_ids))]

    @api.depends('crm_accreditations.accreditation')
    def _compute_accreditation(self):
        for record in self:

            all_accreditations = record.crm_accreditations.mapped('accreditation')
            
            if all_accreditations:
                
                record.accreditation = all_accreditations[0]
            else:
                record.accreditation = False
    
    @api.depends('crm_accreditations')
    def _compute_nilai_initial_audit(self):
        for record in self:
            record.nilai_initial_audit = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Initial Audit').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s1(self):
        for record in self:
            record.nilai_s1 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s2(self):
        for record in self:
            record.nilai_s2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s3(self):
        for record in self:
            record.nilai_s3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 3').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s4(self):
        for record in self:
            record.nilai_s4 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 4').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s5(self):
        for record in self:
            record.nilai_s5 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 5').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s6(self):
        for record in self:
            record.nilai_s6 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 6').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification(self):
        for record in self:
            record.nilai_recertification = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification2(self):
        for record in self:
            record.nilai_recertification2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification3(self):
        for record in self:
            record.nilai_recertification3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 3').mapped('nilai_ia')
            ) or False

class TSICRMSuspen(models.Model):
    _name           = 'tsi.crm.suspen'
    _description    = 'Customer Suspen'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'partner_id'
    _order          = 'id DESC'

    alasan          = fields.Many2one('crm.alasan', string="Alasan", readonly=True)
    partner_id      = fields.Many2one('res.partner', "Partner", readonly=True)
    contract_number = fields.Char('Nomor Kontrak', readonly=True)
    contract_date   = fields.Date(string='Tanggal Kontrak', readonly=True)
    sales           = fields.Many2one('res.users', string='Sales Person', readonly=True)
    level           = fields.Char(string='Level', readonly=True)
    segment         = fields.Many2many('res.partner.category', string='Segment', readonly=True)
    tahapan_audit   = fields.Selection([
                                ('initial audit',         'Initial Audit'),
                                ('Survillance 1', 'Survillance 1'),
                                ('Survillance 2', 'Survillance 2'),
                                ('Survillance 3', 'Survillance 3'),
                                ('Survillance 4', 'Survillance 4'),
                                ('Survillance 5', 'Survillance 5'),
                                ('Survillance 6', 'Survillance 6'),
                                ('Recertification', 'Recertification 1'),
                                ('Recertification 2', 'Recertification 2'),
                                ('Recertification 3', 'Recertification 3'),
                            ], string='Tahapan Audit')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', store=True, readonly=True)
    nilai_kontrak   = fields.Float(string='Nilai Kontrak', tracking=True)
    nilai_initial_audit = fields.Integer(string='IA', compute='_compute_nilai_initial_audit', store=True)
    nilai_s1 = fields.Integer(string='SV1', compute='_compute_nilai_s1', store=True)
    nilai_s2 = fields.Integer(string='SV2', compute='_compute_nilai_s2', store=True)
    nilai_s3 = fields.Integer(string='SV3', compute='_compute_nilai_s3', store=True)
    nilai_s4 = fields.Integer(string='SV4', compute='_compute_nilai_s4', store=True)
    nilai_s5 = fields.Integer(string='SV5', compute='_compute_nilai_s5', store=True)
    nilai_s6 = fields.Integer(string='SV6', compute='_compute_nilai_s6', store=True)
    nilai_recertification = fields.Integer(string='RC1', compute='_compute_nilai_recertification', store=True)
    nilai_recertification2 = fields.Integer(string='RC2', compute='_compute_nilai_recertification2', store=True)
    nilai_recertification3 = fields.Integer(string='RC3', compute='_compute_nilai_recertification3', store=True)
    crm_accreditations  = fields.One2many('tsi.crm_accreditation', 'suspend_id', string="Accreditation Lines", index=True)

    state           =fields.Selection([
                            ('lanjut', 'Lanjut'),
                            ('suspend', 'Suspend'),
                            ('lost','Loss'),
                        ], string='Status', readonly=True, copy=False, index=True, tracking=True, default='suspend')

    # ISO 9001
    price_baru_9001      = fields.Float(string='Current Price ISO 9001')
    price_lama_9001      = fields.Float(string='Previous Price ISO 9001')
    up_value_9001        = fields.Float(string='Up Value ISO 9001')
    loss_value_9001      = fields.Float(string='Loss Value ISO 9001')

    # ISO 14001
    price_baru_14001      = fields.Float(string='Current Price ISO 14001')
    price_lama_14001      = fields.Float(string='Previous Price ISO 14001')
    up_value_14001        = fields.Float(string='Up Value ISO 14001')
    loss_value_14001      = fields.Float(string='Loss Value ISO 14001')

    # ISO 22000
    price_baru_22000      = fields.Float(string='Current Price ISO 22000')
    price_lama_22000      = fields.Float(string='Previous Price ISO 22000')
    up_value_22000        = fields.Float(string='Up Value ISO 22000')
    loss_value_22000      = fields.Float(string='Loss Value ISO 22000')

    # ISO 22001
    price_baru_22001      = fields.Float(string='Current Price ISO 22001')
    price_lama_22001      = fields.Float(string='Previous Price ISO 22001')
    up_value_22001        = fields.Float(string='Up Value ISO 22001')
    loss_value_22001      = fields.Float(string='Loss Value ISO 22001')

    # ISO 22301
    price_baru_22301      = fields.Float(string='Current Price ISO 22301')
    price_lama_22301      = fields.Float(string='Previous Price ISO 22301')
    up_value_22301        = fields.Float(string='Up Value ISO 22301')
    loss_value_22301      = fields.Float(string='Loss Value ISO 22301')

    # ISO 27001
    price_baru_27001      = fields.Float(string='Current Price ISO 27001')
    price_lama_27001      = fields.Float(string='Previous Price ISO 27001')
    up_value_27001        = fields.Float(string='Up Value ISO 27001')
    loss_value_27001      = fields.Float(string='Loss Value ISO 27001')

    # ISO 27701
    price_baru_27701      = fields.Float(string='Current Price ISO 27701')
    price_lama_27701      = fields.Float(string='Previous Price ISO 27701')
    up_value_27701        = fields.Float(string='Up Value ISO 27701')
    loss_value_27701      = fields.Float(string='Loss Value ISO 27701')

    # ISO 45001
    price_baru_45001      = fields.Float(string='Current Price ISO 45001')
    price_lama_45001      = fields.Float(string='Previous Price ISO 45001')
    up_value_45001        = fields.Float(string='Up Value ISO 45001')
    loss_value_45001      = fields.Float(string='Loss Value ISO 45001')

    # ISO 37001
    price_baru_37001      = fields.Float(string='Current Price ISO 37001')
    price_lama_37001      = fields.Float(string='Previous Price ISO 37001')
    up_value_37001        = fields.Float(string='Up Value ISO 37001')
    loss_value_37001      = fields.Float(string='Loss Value ISO 37001')

    # ISO 37301
    price_baru_37301      = fields.Float(string='Current Price ISO 37301')
    price_lama_37301      = fields.Float(string='Previous Price ISO 37301')
    up_value_37301        = fields.Float(string='Up Value ISO 37301')
    loss_value_37301      = fields.Float(string='Loss Value ISO 37301')

    # ISO 31000
    price_baru_31000      = fields.Float(string='Current Price ISO 31000')
    price_lama_31000      = fields.Float(string='Previous Price ISO 31000')
    up_value_31000        = fields.Float(string='Up Value ISO 31000')
    loss_value_31000      = fields.Float(string='Loss Value ISO 31000')

    # ISO 13485
    price_baru_13485      = fields.Float(string='Current Price ISO 13485')
    price_lama_13485      = fields.Float(string='Previous Price ISO 13485')
    up_value_13485        = fields.Float(string='Up Value ISO 13485')
    loss_value_13485      = fields.Float(string='Loss Value ISO 13485')

    # ISO 9994
    price_baru_9994      = fields.Float(string='Current Price ISO 9994')
    price_lama_9994      = fields.Float(string='Previous Price ISO 9994')
    up_value_9994        = fields.Float(string='Up Value ISO 9994')
    loss_value_9994      = fields.Float(string='Loss Value ISO 9994')

    # ISPO
    price_baru_ispo      = fields.Float(string='Current Price ISPO')
    price_lama_ispo      = fields.Float(string='Previous Price ISPO')
    up_value_ispo        = fields.Float(string='Up Value ISPO')
    loss_value_ispo      = fields.Float(string='Loss Value ISPO')

    # HACCP
    price_baru_haccp      = fields.Float(string='Current Price HACCP')
    price_lama_haccp      = fields.Float(string='Previous Price HACCP')
    up_value_haccp        = fields.Float(string='Up Value HACCP')
    loss_value_haccp      = fields.Float(string='Loss Value HACCP')

    # GMP
    price_baru_gmp      = fields.Float(string='Current Price GMP')
    price_lama_gmp      = fields.Float(string='Previous Price GMP')
    up_value_gmp        = fields.Float(string='Up Value GMP')
    loss_value_gmp      = fields.Float(string='Loss Value GMP')

    # SMK3
    price_baru_smk3      = fields.Float(string='Current Price SMK3')
    price_lama_smk3      = fields.Float(string='Previous Price SMK3')
    up_value_smk3        = fields.Float(string='Up Value SMK3')
    loss_value_smk3      = fields.Float(string='Loss Value SMK3')

    def create_lanjut(self):
        iso_standard_ids_set = set(self.iso_standard_ids.mapped('name'))
        
        new_lanjut_record = self.env['tsi.crm.lanjut'].create({
            'partner_id': self.partner_id.id,
            'sales': self.sales.id,
            'contract_number': self.contract_number,
            'contract_date': self.contract_date,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            # 'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            # 'associate': self.associate.id,
            # 'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            # 'pic': self.pic.id,
            # 'closing_by': self.closing_by,
            # 'alamat': self.alamat,
            # 'level_audit': self.level_audit,
            # 'level_audit_ispo': self.level_audit_ispo,
            # 'referal': self.referal,
            'nilai_kontrak': self.nilai_kontrak,
            # 'accreditation': self.accreditation.id,
            **({'price_baru_9001': self.price_baru_9001,
                'price_lama_9001': self.price_lama_9001,
                'up_value_9001': self.up_value_9001,
                'loss_value_9001': self.loss_value_9001}
            if 'ISO 9001:2015' in iso_standard_ids_set else {}),
            **({'price_baru_14001': self.price_baru_14001,
                'price_lama_14001': self.price_lama_14001,
                'up_value_14001': self.up_value_14001,
                'loss_value_14001': self.loss_value_14001}
            if 'ISO 14001:2015' in iso_standard_ids_set else {}),
            **({'price_baru_22000': self.price_baru_22000,
                'price_lama_22000': self.price_lama_22000,
                'up_value_22000': self.up_value_22000,
                'loss_value_22000': self.loss_value_22000}
            if 'ISO 22000:2018' in iso_standard_ids_set else {}),
            **({'price_baru_22001': self.price_baru_22001,
                'price_lama_22001': self.price_lama_22001,
                'up_value_22001': self.up_value_22001,
                'loss_value_22001': self.loss_value_22001}
            if 'ISO 22001:2018' in iso_standard_ids_set else {}),
            **({'price_baru_22301': self.price_baru_22301,
                'price_lama_22301': self.price_lama_22301,
                'up_value_22301': self.up_value_22301,
                'loss_value_22301': self.loss_value_22301}
            if 'ISO 22301:2019' in iso_standard_ids_set else {}),
            **({'price_baru_27001': self.price_baru_27001,
                'price_lama_27001': self.price_lama_27001,
                'up_value_27001': self.up_value_27001,
                'loss_value_27001': self.loss_value_27001}
            if 'ISO/IEC 27001:2022' in iso_standard_ids_set else {}),
            **({'price_baru_27701': self.price_baru_27701,
                'price_lama_27701': self.price_lama_27701,
                'up_value_27701': self.up_value_27701,
                'loss_value_27701': self.loss_value_27701}
            if 'ISO 27701:2019' in iso_standard_ids_set else {}),
            **({'price_baru_45001': self.price_baru_45001,
                'price_lama_45001': self.price_lama_45001,
                'up_value_45001': self.up_value_45001,
                'loss_value_45001': self.loss_value_45001}
            if 'ISO 45001:2018' in iso_standard_ids_set else {}),
            **({'price_baru_37001': self.price_baru_37001,
                'price_lama_37001': self.price_lama_37001,
                'up_value_37001': self.up_value_37001,
                'loss_value_37001': self.loss_value_37001}
            if 'ISO 37001:2016' in iso_standard_ids_set else {}),
            **({'price_baru_37301': self.price_baru_37301,
                'price_lama_37301': self.price_lama_37301,
                'up_value_37301': self.up_value_37301,
                'loss_value_37301': self.loss_value_37301}
            if 'ISO 37301:2021' in iso_standard_ids_set else {}),
            **({'price_baru_31000': self.price_baru_31000,
                'price_lama_31000': self.price_lama_31000,
                'up_value_31000': self.up_value_31000,
                'loss_value_31000': self.loss_value_31000}
            if 'ISO 31000:2018' in iso_standard_ids_set else {}),
            **({'price_baru_13485': self.price_baru_13485,
                'price_lama_13485': self.price_lama_13485,
                'up_value_13485': self.up_value_13485,
                'loss_value_13485': self.loss_value_13485}
            if 'ISO 13485:2016' in iso_standard_ids_set else {}),
            **({'price_baru_9994': self.price_baru_9994,
                'price_lama_9994': self.price_lama_9994,
                'up_value_9994': self.up_value_9994,
                'loss_value_9994': self.loss_value_9994}
            if 'ISO 9994:2018' in iso_standard_ids_set else {}),
            **({'price_baru_ispo': self.price_baru_ispo,
                'price_lama_ispo': self.price_lama_ispo,
                'up_value_ispo': self.up_value_ispo,
                'loss_value_ispo': self.loss_value_ispo}
            if 'ISPO' in iso_standard_ids_set else {}),
            **({'price_baru_haccp': self.price_baru_haccp,
                'price_lama_haccp': self.price_lama_haccp,
                'up_value_haccp': self.up_value_haccp,
                'loss_value_haccp': self.loss_value_haccp}
            if 'HACCP' in iso_standard_ids_set else {}),
            **({'price_baru_gmp': self.price_baru_gmp,
                'price_lama_gmp': self.price_lama_gmp,
                'up_value_gmp': self.up_value_gmp,
                'loss_value_gmp': self.loss_value_gmp}
            if 'GMP' in iso_standard_ids_set else {}),
            **({'price_baru_smk3': self.price_baru_smk3,
                'price_lama_smk3': self.price_lama_smk3,
                'up_value_smk3': self.up_value_smk3,
                'loss_value_smk3': self.loss_value_smk3}
            if 'SMK3' in iso_standard_ids_set else {}),
        })

        history_kontrak = self.env['tsi.history_kontrak'].search([
            ('partner_id', '=', self.partner_id.id)
        ])

        history_kontrak.write({'state': 'lanjut'})

        self.write({'state': 'lanjut'})

        suspen_accreditations = self.env['tsi.crm_accreditation'].search([('suspend_id', '=', self.id)])

        for standard in self.iso_standard_ids:
            suspen_accreditation = suspen_accreditations.filtered(lambda a: standard in a.iso_standard_ids)

            if suspen_accreditation:
                for suspen_acc in suspen_accreditation:

                    if suspen_acc.tahapan_audit == 'Initial Audit' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Initial Audit',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 1' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 1',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 2' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 2',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 3' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 3',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 4' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 4',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 5' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 5',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 6' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 6',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification 1' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification 1',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification 2' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification 2',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification 3' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'lanjut_id': new_lanjut_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification 3',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

        partner_name = self.partner_id.name or "Customer"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses!',
                'message': f'{partner_name} berhasil ke CRM Lanjut!',
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

    def create_loss(self):
        iso_standard_ids_set = set(self.iso_standard_ids.mapped('name'))
        
        new_loss_record = self.env['tsi.crm.loss'].create({
            'partner_id': self.partner_id.id,
            'sales': self.sales.id,
            'contract_number': self.contract_number,
            'contract_date': self.contract_date,
            'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
            # 'tahapan_audit_ids': [(6, 0, self.tahapan_audit_ids.ids)],
            # 'associate': self.associate.id,
            # 'category': self.category,
            'segment': [(6, 0, self.segment.ids)],
            # 'pic': self.pic.id,
            # 'closing_by': self.closing_by,
            # 'alamat': self.alamat,
            # 'level_audit': self.level_audit,
            # 'level_audit_ispo': self.level_audit_ispo,
            # 'referal': self.referal,
            'nilai_kontrak': self.nilai_kontrak,
            # 'accreditation': self.accreditation.id,
            **({'price_baru_9001': self.price_baru_9001,
                'price_lama_9001': self.price_lama_9001,
                'up_value_9001': self.up_value_9001,
                'loss_value_9001': self.loss_value_9001}
            if 'ISO 9001:2015' in iso_standard_ids_set else {}),
            **({'price_baru_14001': self.price_baru_14001,
                'price_lama_14001': self.price_lama_14001,
                'up_value_14001': self.up_value_14001,
                'loss_value_14001': self.loss_value_14001}
            if 'ISO 14001:2015' in iso_standard_ids_set else {}),
            **({'price_baru_22000': self.price_baru_22000,
                'price_lama_22000': self.price_lama_22000,
                'up_value_22000': self.up_value_22000,
                'loss_value_22000': self.loss_value_22000}
            if 'ISO 22000:2018' in iso_standard_ids_set else {}),
            **({'price_baru_22001': self.price_baru_22001,
                'price_lama_22001': self.price_lama_22001,
                'up_value_22001': self.up_value_22001,
                'loss_value_22001': self.loss_value_22001}
            if 'ISO 22001:2018' in iso_standard_ids_set else {}),
            **({'price_baru_22301': self.price_baru_22301,
                'price_lama_22301': self.price_lama_22301,
                'up_value_22301': self.up_value_22301,
                'loss_value_22301': self.loss_value_22301}
            if 'ISO 22301:2019' in iso_standard_ids_set else {}),
            **({'price_baru_27001': self.price_baru_27001,
                'price_lama_27001': self.price_lama_27001,
                'up_value_27001': self.up_value_27001,
                'loss_value_27001': self.loss_value_27001}
            if 'ISO/IEC 27001:2022' in iso_standard_ids_set else {}),
            **({'price_baru_27701': self.price_baru_27701,
                'price_lama_27701': self.price_lama_27701,
                'up_value_27701': self.up_value_27701,
                'loss_value_27701': self.loss_value_27701}
            if 'ISO 27701:2019' in iso_standard_ids_set else {}),
            **({'price_baru_45001': self.price_baru_45001,
                'price_lama_45001': self.price_lama_45001,
                'up_value_45001': self.up_value_45001,
                'loss_value_45001': self.loss_value_45001}
            if 'ISO 45001:2018' in iso_standard_ids_set else {}),
            **({'price_baru_37001': self.price_baru_37001,
                'price_lama_37001': self.price_lama_37001,
                'up_value_37001': self.up_value_37001,
                'loss_value_37001': self.loss_value_37001}
            if 'ISO 37001:2016' in iso_standard_ids_set else {}),
            **({'price_baru_37301': self.price_baru_37301,
                'price_lama_37301': self.price_lama_37301,
                'up_value_37301': self.up_value_37301,
                'loss_value_37301': self.loss_value_37301}
            if 'ISO 37301:2021' in iso_standard_ids_set else {}),
            **({'price_baru_31000': self.price_baru_31000,
                'price_lama_31000': self.price_lama_31000,
                'up_value_31000': self.up_value_31000,
                'loss_value_31000': self.loss_value_31000}
            if 'ISO 31000:2018' in iso_standard_ids_set else {}),
            **({'price_baru_13485': self.price_baru_13485,
                'price_lama_13485': self.price_lama_13485,
                'up_value_13485': self.up_value_13485,
                'loss_value_13485': self.loss_value_13485}
            if 'ISO 13485:2016' in iso_standard_ids_set else {}),
            **({'price_baru_9994': self.price_baru_9994,
                'price_lama_9994': self.price_lama_9994,
                'up_value_9994': self.up_value_9994,
                'loss_value_9994': self.loss_value_9994}
            if 'ISO 9994:2018' in iso_standard_ids_set else {}),
            **({'price_baru_ispo': self.price_baru_ispo,
                'price_lama_ispo': self.price_lama_ispo,
                'up_value_ispo': self.up_value_ispo,
                'loss_value_ispo': self.loss_value_ispo}
            if 'ISPO' in iso_standard_ids_set else {}),
            **({'price_baru_haccp': self.price_baru_haccp,
                'price_lama_haccp': self.price_lama_haccp,
                'up_value_haccp': self.up_value_haccp,
                'loss_value_haccp': self.loss_value_haccp}
            if 'HACCP' in iso_standard_ids_set else {}),
            **({'price_baru_gmp': self.price_baru_gmp,
                'price_lama_gmp': self.price_lama_gmp,
                'up_value_gmp': self.up_value_gmp,
                'loss_value_gmp': self.loss_value_gmp}
            if 'GMP' in iso_standard_ids_set else {}),
            **({'price_baru_smk3': self.price_baru_smk3,
                'price_lama_smk3': self.price_lama_smk3,
                'up_value_smk3': self.up_value_smk3,
                'loss_value_smk3': self.loss_value_smk3}
            if 'SMK3' in iso_standard_ids_set else {}),
        })

        history_kontrak = self.env['tsi.history_kontrak'].search([
            ('partner_id', '=', self.partner_id.id)
        ])

        history_kontrak.write({'state': 'lost'})

        self.write({'state': 'lost'})

        suspen_accreditations = self.env['tsi.crm_accreditation'].search([('suspend_id', '=', self.id)])

        for standard in self.iso_standard_ids:

            suspen_accreditation = suspen_accreditations.filtered(lambda a: standard in a.iso_standard_ids)

            if suspen_accreditation:
                for suspen_acc in suspen_accreditation:
                    
                    if suspen_acc.tahapan_audit == 'Initial Audit' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Initial Audit',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 1' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 1',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 2' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 2',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 3' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 3',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 4' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 4',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 5' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 5',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Surveillance 6' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Surveillance 6',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification 1' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification 1',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification 2' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification 2',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

                    elif suspen_acc.tahapan_audit == 'Recertification 3' and suspen_acc.nilai_ia:
                        self.env['tsi.crm_accreditation'].create({
                            'loss_id': new_loss_record.id,
                            'iso_standard_ids': [(6, 0, [standard.id])],
                            'accreditation': suspen_acc.accreditation.id,
                            'tahapan_audit': 'Recertification 3',
                            'nilai_ia': suspen_acc.nilai_ia,
                        })

        partner_name = self.partner_id.name or "Customer"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sukses!',
                'message': f'{partner_name} berhasil ke CRM Loss!',
                'sticky': False,
                'type': 'danger',
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

    @api.depends('crm_accreditations.iso_standard_ids')
    def _compute_iso_standard_ids(self):
        for record in self:
            # Mengumpulkan semua ISO standard IDs dari baris crm_accreditations
            iso_standard_ids = record.crm_accreditations.mapped('iso_standard_ids')
            # Hanya ambil ID (integer) dari daftar ISO standards
            all_iso_standard_ids = set(iso_standard_ids.mapped('id'))
            record.iso_standard_ids = [(6, 0, list(all_iso_standard_ids))]

    @api.depends('crm_accreditations.accreditation')
    def _compute_accreditation(self):
        for record in self:

            all_accreditations = record.crm_accreditations.mapped('accreditation')
            
            if all_accreditations:
                
                record.accreditation = all_accreditations[0]
            else:
                record.accreditation = False
    
    @api.depends('crm_accreditations')
    def _compute_nilai_initial_audit(self):
        for record in self:
            record.nilai_initial_audit = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Initial Audit').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s1(self):
        for record in self:
            record.nilai_s1 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s2(self):
        for record in self:
            record.nilai_s2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s3(self):
        for record in self:
            record.nilai_s3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 3').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s4(self):
        for record in self:
            record.nilai_s4 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 4').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s5(self):
        for record in self:
            record.nilai_s5 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 5').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_s6(self):
        for record in self:
            record.nilai_s6 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Surveillance 6').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification(self):
        for record in self:
            record.nilai_recertification = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 1').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification2(self):
        for record in self:
            record.nilai_recertification2 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 2').mapped('nilai_ia')
            ) or False

    @api.depends('crm_accreditations')
    def _compute_nilai_recertification3(self):
        for record in self:
            record.nilai_recertification3 = sum(
                record.crm_accreditations.filtered(lambda r: r.tahapan_audit == 'Recertification 3').mapped('nilai_ia')
            ) or False

class CustomerSurvey(models.Model):
    _name = 'crm.customer.survey'
    _description = 'Survei Kepuasan Pelanggan'
    _rec_name    = 'company'
    
    # partner_id              = fields.Many2one('res.partner', string='Perusahaan', domain="[('is_company', '=', True)]")
    company                 = fields.Char(string='Perusahaan')
    nama                    = fields.Char(string='Nama')
    jabatan                 = fields.Char(string='Jabatan')
    email                   = fields.Char(string='Email')
    no_telp                 = fields.Char(string='Nomor Telp')
    iso_standard_ids        = fields.Many2many('tsi.iso.standard', string='Standards')
    tanggal_audit           = fields.Date(string='Tanggal Pelaksanaan Audit')
    tanggal_input           = fields.Date(string='Tanggal Input Survey')
    tahap_audit = fields.Selection([
        ('ia', 'Initial Audit'),
        ('sv1', 'Surveillance 1'),
        ('sv2', 'Surveillance 2'),
        ('sv3', 'Surveillance 3'),
        ('sv4', 'Surveillance 4'),
        ('re', 'Resertifikasi')
    ], string='Tahap Audit')
    question_1 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Sales (proses kontrak) PT TSI Sertifikasi Internasional ?')
    saran_1                 = fields.Char(string='Mohon saran / masukan untuk peningkatan kinerja Sales TSI')
    question_2 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Admin (persiapan & penjadwalan audit) PT TSI Sertifikasi Internasional ?')
    saran_2                 = fields.Char(string='Mohon saran / masukan untuk peningkatan kinerja Admin TSI')

    # Auditor 1 - 4
    star_auditor1 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Auditor 1 PT TSI Sertifikasi Internasional?')
    nama_auditor1 = fields.Char(string='Nama Auditor 1')

    star_auditor2 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Auditor 2 PT TSI Sertifikasi Internasional?')
    nama_auditor2 = fields.Char(string='Nama Auditor 2')

    star_auditor3 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Auditor 3 PT TSI Sertifikasi Internasional?')
    nama_auditor3 = fields.Char(string='Nama Auditor 3')

    star_auditor4 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Auditor 4 PT TSI Sertifikasi Internasional?')
    nama_auditor4 = fields.Char(string='Nama Auditor 4')

    question_3 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Customer Relation/ Customer Care PT TSI Sertifikasi Internasional?')
    saran_3                 = fields.Char(string='Mohon saran / masukan untuk peningkatan kinerja Auditor TSI')
    question_4 = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Bagaimana penilaian terhadap Finance (proses invoicing) PT TSI Sertifikasi Internasional?')
    saran_4                 = fields.Char(string='Mohon saran / masukan untuk peningkatan kinerja Finance TSI')
    question_5 = fields.Selection([
        ('website', 'Website'),
        ('sales', 'Sales'),
        ('asosiasi', 'Asosiasi'),
        ('medsos', 'Media sosial'),
        ('relasi', 'Kerabat/Relasi'),
        ('lainnya', 'Lainnya')
    ], string='Dari mana Anda mendapatkan informasi mengenai PT TSI Sertifikasi Internasional ?')
    score = fields.Selection([
        ('01', '1'),
        ('02', '2'),
        ('03', '3'),
        ('04', '4'),
        ('05', '5'),
        ('06', '6'),
        ('07', '7'),
        ('08', '8'),
        ('09', '9'),
        ('10', '10')
    ], string='Seberapa besar kemungkinan Anda merekomendasikan Perusahaan kami kepada rekan kerja dan kolega?')
    # score = fields.Integer(string='Seberapa besar kemungkinan Anda merekomendasikan Perusahaan kami kepada rekan kerja dan kolega?', default=10)
    saran_5                 = fields.Char(string='Mohon saran /masukan terkait dengan peluang peningkatan pelayanan kami')
    # average_score = fields.Float(string="Nilai Rata-Rata", compute="_compute_average_score", store=True)
    tipe = fields.Selection([
        ('iso', 'ISO'),
        ('ispo', 'ISPO')
    ], string='Tipe', compute='_compute_tipe', store=True)

    @api.depends('iso_standard_ids')
    def _compute_tipe(self):
        for record in self:
            if record.iso_standard_ids.filtered(lambda s: s.name in ['ISPO', 'ISCC']):
                record.tipe = 'ispo'
            else:
                record.tipe = 'iso'

    # @api.depends('question_1', 'question_2', 'question_3', 'question_4')
    # def _compute_average_score(self):
    #     weight_mapping = {
    #         '01': 2,
    #         '02': 4,
    #         '03': 6,
    #         '04': 8,
    #         '05': 10
    #     }
    #     for record in self:
    #         scores = [
    #             weight_mapping.get(record.question_1, 0),
    #             weight_mapping.get(record.question_2, 0),
    #             weight_mapping.get(record.question_3, 0),
    #             weight_mapping.get(record.question_4, 0)
    #         ]
    #         answered_scores = [score for score in scores if score > 0]
    #         if answered_scores:
    #             record.average_score = sum(answered_scores) / 4.0
    #         else:
    #             record.average_score = 0

class CRMAchievementComparison(models.Model):
    _name = 'crm.achievement.comparison'
    _description = 'Perbandingan Pencapaian Setiap 3 Tahun Terakhir'
    _rec_name    = 'year'

    # name = fields.Char(string="Nama Pencapaian", required=True)
    year = fields.Char(string="Tahun")
    month = fields.Selection([
        ('01', 'Januari'),
        ('02', 'Februari'),
        ('03', 'Maret'),
        ('04', 'April'),
        ('05', 'Mei'),
        ('06', 'Juni'),
        ('07', 'Juli'),
        ('08', 'Agustus'),
        ('09', 'September'),
        ('10', 'Oktober'),
        ('11', 'November'),
        ('12', 'Desember')
    ], string="Bulan")
    
    achievement_value = fields.Float(string="Pencapaian", required=True)
    
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    total_achievement_value = fields.Monetary(
        string="Total Pencapaian", 
        compute='_compute_total_achievement_value', 
        store=True, 
        currency_field='currency_id'
    )

    @api.depends('achievement_value')
    def _compute_total_achievement_value(self):
        """ Menghitung total pencapaian """
        for record in self:
            total = sum(self.search([]).mapped('achievement_value'))
            record.total_achievement_value = total

class CRMTargetActual(models.Model):
    _name = 'crm.target.actual'
    _description = 'Target dan Actual'
    _rec_name    = 'year'

    pencapaian_crm = fields.Selection([
        ('iso', 'ISO'),
        ('ispo', 'ISPO'),
    ], string='Pencapaian')
    year = fields.Char(string="Tahun")
    month = fields.Selection([
        ('01', 'Januari'),
        ('02', 'Februari'),
        ('03', 'Maret'),
        ('04', 'April'),
        ('05', 'Mei'),
        ('06', 'Juni'),
        ('07', 'Juli'),
        ('08', 'Agustus'),
        ('09', 'September'),
        ('10', 'Oktober'),
        ('11', 'November'),
        ('12', 'Desember'),
    ], string="Bulan")

    tipe_pencapaian  = fields.Char(string="Tipe", default="Target")

    nilai  = fields.Float(string="Target")

    # percentage_achievement = fields.Float(
    #     string="Persentase Pencapaian (%)", 
    #     compute='_compute_percentage_achievement', 
    #     store=True
    # )

    # @api.depends('target_value', 'actual_value')
    # def _compute_percentage_achievement(self):
    #     for record in self:
    #         if record.target_value > 0:
    #             record.percentage_achievement = (record.actual_value / record.target_value) * 100
    #         else:
    #             record.percentage_achievement = 0

class CRMRefereal(models.Model):
    _name           = 'crm.refereal'
    _description    = 'CRM Refereal'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name       = 'name'

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    company_id = fields.Many2one('res.partner', string='Perusahaan', domain="[('is_company', '=', True)]")
    alamat = fields.Selection([
        ('dalam_kota', 'Dalam Kota'),
        ('luar_kota', 'Luar Kota'),
    ], string='Alamat')
    kunjungan = fields.Selection([
        ('ceremony', 'Ceremony'),
        ('proses_sv_rc', 'Proses SV atau RC'),
        ('complain', 'Complain'),
        ('ec', 'Engagement Consultan'),
        ('dll', 'Dll'),
    ], string='Kunjungan')