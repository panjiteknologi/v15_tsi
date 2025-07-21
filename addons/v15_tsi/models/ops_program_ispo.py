from odoo import models, fields, api, SUPERUSER_ID, _
from datetime import datetime

class AuditProgramISPO(models.Model):
    _name           = 'ops.program.ispo'
    _description    = 'Audit Program ISPO'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name                = fields.Char(string='Document No', tracking=True)
    ispo_reference       = fields.Many2one('tsi.ispo', string="Reference", tracking=True)
# related, ea_code ???
    notification_id = fields.Many2one('audit.notification.ispo', string="Notification", tracking=True)    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True) 
    audit_request_id    = fields.Many2one('tsi.audit.request', string="Audit Request",  readonly=True)   

    customer            = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer', tracking=True, readonly=False)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)
    contact_person      = fields.Char(string="Contact Person", related='ispo_reference.contact_person', tracking=True, readonly=False)
    head_office         = fields.Char(string="Jumlah Head Office", related='ispo_reference.head_office', tracking=True, readonly=False)
    site_office         = fields.Char(string="Jumlah Site Office", related='ispo_reference.site_office', tracking=True, readonly=False)
    off_location        = fields.Char(string="Jumlah Off Location", related='ispo_reference.off_location', tracking=True, readonly=False)
    part_time           = fields.Char(string="Jumlah Part Time", related='ispo_reference.part_time', tracking=True, readonly=False)
    subcon              = fields.Char(string="Jumlah Sub Contractor", related='ispo_reference.subcon', tracking=True, readonly=False)
    unskilled           = fields.Char(string="Jumlah Unskilled", related='ispo_reference.unskilled', tracking=True, readonly=False)
    seasonal            = fields.Char(string="Jumlah Seasonal", related='ispo_reference.seasonal', tracking=True, readonly=False)
    total_emp           = fields.Integer(string="Total Employee", related='customer.total_emp', tracking=True, readonly=False)
    accreditation       = fields.Many2one('tsi.iso.accreditation', string="Accreditation", tracking=True)
    # scope               = fields.Text('Scope', related='ispo_reference.scope', tracking=True, readonly=False)
    scope = fields.Selection([
                            ('Integrasi','INTEGRASI'),
                            ('Pabrik', 'PABRIK'),
                            ('Kebun',  'KEBUN'),
                            ('Plasma / Swadaya', 'PLASMA / SWADAYA'),
                        ], string='Scope', index=True, related='ispo_reference.scope')
    boundaries          = fields.Text('Boundaries', related='ispo_reference.boundaries', tracking=True, readonly=False)
    telepon             = fields.Char(string="No Telepon", related='ispo_reference.telepon', tracking=True, readonly=False)

    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code", tracking=True)
    type_client         = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Type Client', tracking=True)
    apprev_date         = fields.Datetime(string="Review Date", related="sales_order_id.application_review_ids.finish_date", tracking=True, readonly=False)    
    contract_date       = fields.Datetime(string="Contract Date", tracking=True)       
    contract_number     = fields.Char(string="Contract Number", tracking=True) 


    tgl_sertifikat              = fields.Date('Tanggal Sertifikat', tracking=True)
    tgl_sertifikat_original     = fields.Date('Tanggal Sertifikat Original', tracking=True)
    tgl_sertifikat_update       = fields.Date('Tanggal Sertifikat Terkini', tracking=True)
    tgl_sertifikat_descision    = fields.Date('Tanggal Sertifikat Decision', tracking=True)
    pic_decision                = fields.Char(string='Nama Decision Maker', tracking=True)
    tgl_audit_stage_2           = fields.Date('Tanggal Audit Stage 2', tracking=True)

    pic_auditor_2               = fields.Many2many('hr.employee', string="Nama Auditor", tracking=True)

    tgl_review_stage_1          = fields.Date('Tanggal Review Stage 1', tracking=True)
    pic_reviewer                = fields.Char(string='PIC Reviewer Stage 1', tracking=True)
    
    tgl_audit_stage_1           = fields.Date('Tanggal Audit Stage 1 Awal', tracking=True)
    tgl_audit_stage_1_akhir           = fields.Date('Tanggal Audit Stage 1 Akhir', tracking=True)
    pic_auditor_1               = fields.Char(string='PIC Auditor 1', tracking=True)

    tgl_application_form        = fields.Date('Tanggal Application Form', tracking=True)
    tgl_kontrak                 = fields.Date('Tanggal Kontrak', tracking=True)
    upload_dokumen              = fields.Binary('Attachment', tracking=True)
    tgl_notifikasi              = fields.Date(string="Notification Date", default=datetime.today(), tracking=True)
    notification_printed = fields.Boolean(string='Notification Printed', default=False, tracking=True)
    dokumen_sosialisasi        = fields.Binary('Organization Chart', related="sales_order_id.dokumen_sosialisasi", tracking=True, readonly=False)
    file_name1      = fields.Char('Filename',related="sales_order_id.file_name1", tracking=True, readonly=False)
    state                       = fields.Selection([
                                        ('new',     'New'),
                                        ('confirm', 'Confirm'),
                                        ('done',    'Stage-1'),
                                        ('done_stage2', 'Stage-2'),
                                        ('done_surveillance1', 'Surveillance1'),
                                        ('done_surveillance2', 'Surveillance2'),
                                        ('done_surveillance3', 'Surveillance3'),
                                        ('done_surveillance4', 'Surveillance4'),
                                        ('done_recertification', 'Recertification'),
                                    ], string='Status', readonly=True, copy=False, index=True, default='new')

    program_lines               = fields.One2many('ops.program.program_ispo', 'reference_id', string="Reference", index=True)
    program_lines_aktual               = fields.One2many('ops.program.aktual_ispo', 'reference_id', string="Reference", index=True)

    has_surveillance1 = fields.Boolean(string="Has Surveillance 1", compute='_compute_audit_flags', store=True)
    has_stage02 = fields.Boolean(string="Has Stage 2", compute='_compute_audit_flags', store=True)
    has_surveillance2 = fields.Boolean(string="Has Surveillance 2", compute='_compute_audit_flags', store=True)
    has_recertification = fields.Boolean(string="Has Recertification", compute='_compute_audit_flags', store=True)

    @api.depends('program_lines_aktual.audit_type')
    def _compute_audit_flags(self):
        for record in self:
            audit_types = [line.audit_type for line in record.program_lines_aktual]
            record.has_surveillance1 = 'surveilance1' in audit_types
            record.has_stage02 = 'Stage-02' in audit_types
            record.has_surveillance2 = 'surveilance2' in audit_types
            record.has_recertification = 'recertification' in audit_types

    # STAGE 01
    def set_to_confirm(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['Stage-01', 'surveilance1', 'surveilance2', 'surveilance3', 'surveilance4', 'recertification']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan.ispo'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'confirm'})
        return True
    
    # STAGE 02
    def action_stage2(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['Stage-02']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan.ispo'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'done_stage2'})
        return True
    
    # SURVEILLANCE 1
    def action_surviellance1(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['surveilance1']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan.ispo'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'done_surveillance1'})
        return True
    
    # SURVEILLANCE 2
    def action_surviellance2(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['surveilance2']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan.ispo'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'done_surveillance2'})
        return True

    # SURVEILLANCE 3
    def action_surviellance3(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['surveilance3']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan.ispo'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'done_surveillance3'})
        return True

    # SURVEILLANCE 4
    def action_surviellance4(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['surveilance4']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan.ispo'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'done_surveillance4'})
        return True
    
    # RECERTIFICATION
    def action_recertification(self):
        self.ensure_one()

        def get_or_create_mandays_auditor(employee):
            AuditorModel = self.env['mandays.auditor']
            auditor = AuditorModel.search([('name_auditor', '=', employee.id)], limit=1)
            if not auditor:
                auditor = AuditorModel.create({
                    'name_auditor': employee.id,
                    'harga_mandays': 0.0
                })
            return auditor

        def create_pengajuan_mandays_line(employee, line):
            auditor = get_or_create_mandays_auditor(employee)

            mandays_rec = self.env['tsi.pengajuan.mandays'].search([
                ('auditor', '=', auditor.id)
            ], limit=1)

            if not mandays_rec:
                mandays_rec = self.env['tsi.pengajuan.mandays'].create({
                    'auditor': auditor.id
                })

            existing_line = self.env['tsi.pengajuan.mandays.line'].search([
                ('mandays_id', '=', mandays_rec.id),
                ('audit_date', '=', line.date_start),
                ('audit_type', '=', line.audit_type),
                ('customer', '=', self.customer.id),
            ], limit=1)

            if not existing_line:
                self.env['tsi.pengajuan.mandays.line'].create({
                    'mandays_id': mandays_rec.id,
                    'customer': self.customer.id,
                    'audit_date': line.date_start,
                    'audit_type': line.audit_type,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'volume': line.mandayss,
                    'satuan': 'Man',
                    'biaya_satuan': auditor.harga_mandays,
                })

            else:
                combined_standard_ids = list(set(existing_line.iso_standard_ids.ids + self.iso_standard_ids.ids))
                existing_line.write({
                    'iso_standard_ids': [(6, 0, combined_standard_ids)]
                })

        for line in self.program_lines_aktual:
            if line.audit_type in ['recertification']:
                vals = {
                    'auditor_1': line.auditor.id,
                    'auditor_2': line.auditor_2.id,
                    'auditor_3': line.auditor_3.id,
                    'technical_expert': line.expert.id,
                    'audit_method': line.metode,
                    'audit_stage': line.audit_type,
                    'audit_start': line.date_start,
                    'audit_end': line.date_end,
                    'auditor_lead': line.lead_auditor.id,
                    'iso_reference': self.iso_reference.id,
                    'sales_order_id': self.sales_order_id.id,
                    'iso_standard_ids': [(6, 0, self.iso_standard_ids.ids)],
                    'notification_id': self.notification_id.id,
                    'contract_number': self.contract_number,
                    'dokumen_sosialisasi': self.dokumen_sosialisasi,
                    'file_name1': self.file_name1,
                    'contract_date': self.contract_date,
                    'program_id': self.id
                }
                self.env['ops.plan'].create(vals)

                for employee in filter(None, [
                    line.lead_auditor,
                    line.auditor,
                    line.auditor_2,
                    line.auditor_3,
                    line.expert
                ]):
                    create_pengajuan_mandays_line(employee, line)
                    
        self.write({'state': 'new'})
        return True

    def set_to_done(self):
        # Periksa setiap record di model ini
        for record in self:
            # Inisialisasi variabel untuk menyimpan status
            audit_stage_value = []
            
            # Iterasi untuk setiap program_lines_aktual yang terkait dengan record ini
            for line in record.program_lines_aktual:
                # Tambahkan 'Stage-01' jika ada pada audit_type
                if 'Stage-01' in line.audit_type:
                    audit_stage_value.append('Stage-01')

                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-1' in line.audit_type:
                    audit_stage_value.append('surveilance1')
                
                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-2' in line.audit_type:
                    audit_stage_value.append('surveilance2')
                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-3' in line.audit_type:
                    audit_stage_value.append('surveilance3')
                # Tambahkan 'Surveillance-1' jika ada pada audit_type
                if 'Survillance-4' in line.audit_type:
                    audit_stage_value.append('surveilance4')

            # Tentukan state berdasarkan nilai audit_type yang ditemukan
            if 'Stage-01' in audit_stage_value:
                record.write({'state': 'done'})  # Jika Stage-01 ditemukan, set state ke 'done'
            if 'surveilance1' in audit_stage_value:
                record.write({'state': 'done_surveillance1'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'surveilance2' in audit_stage_value:
                record.write({'state': 'done_surveillance2'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'surveilance3' in audit_stage_value:
                record.write({'state': 'done_surveillance3'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
            if 'surveilance4' in audit_stage_value:
                record.write({'state': 'done_surveillance4'})  # Jika Surveillance-1 ditemukan, set state ke 'surveillance_1'
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True
    
    def set_to_stage1(self):
        self.write({'state': 'done'})            
        return True
    
    def set_to_stage2(self):
        self.write({'state': 'done_stage2'})            
        return True
    
    def set_to_surveillance1(self):
        self.write({'state': 'done_surveillance1'})            
        return True
    
    def set_to_surveillance2(self):
        self.write({'state': 'done_surveillance2'})            
        return True
    
    def set_to_surveillance3(self):
        self.write({'state': 'done_surveillance3'})            
        return True
    
    def set_to_surveillance4(self):
        self.write({'state': 'done_surveillance4'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.program.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditProgramISPO, self).create(vals)
        return result
    
    def audit_notification(self):
        # Code to generate Stage 1 report
        self.write({
            'tgl_notifikasi': fields.Datetime.now(),
            'notification_printed': True,
        })
        return self.env.ref('v15_tsi.audit_notification').report_action(self)

class PartnerCertificateISPO(models.Model):
    _name           = 'ops.program.program_ispo'
    _description    = 'certificate'

    reference_id        = fields.Many2one('ops.program.ispo', string="Reference", tracking=True)
    audit_type          = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('surveilance1',    'Surveilance 1'),
                            ('surveilance2',    'Surveilance 2'),
                            ('recertification',    'Recertification'),
                            # ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], tracking=True)
    date_start          = fields.Date(string='Date Start', tracking=True)
    date_end            = fields.Date(string='Date End', tracking=True)
    lead_auditor        = fields.Many2one('hr.employee', string="Lead Auditor", tracking=True)
    auditor             = fields.Many2one('hr.employee', string="Auditor", tracking=True)
    auditor_2             = fields.Many2one('hr.employee', string="Auditor 2", tracking=True)
    auditor_3             = fields.Many2one('hr.employee', string="Auditor 3", tracking=True)
    expert              = fields.Many2one('hr.employee', string="Technical Expert", tracking=True)
    remarks             = fields.Text(string='Remarks', tracking=True)
    mandayss            = fields.Char(string="Mandays", tracking=True)
    metode              = fields.Selection(string='Metode Audit', selection=[
                            ('online',   'Online'), 
                            ('onsite',   'Onsite'), 
                            ('hybrid',   'Hybrid'), 
                            ], tracking=True)

    @api.model
    def create(self, vals):
        record = super(PartnerCertificateISPO, self).create(vals)
        partner = record.reference_id
        partner.message_post(body=f"Created Audit Type: {record.audit_type}, Date Start: {record.date_start}, Date End: {record.date_end}, Lead Auditor: {record.lead_auditor.name}, Auditor: {record.auditor.name}, Auditor 2: {record.auditor_2.name}, Auditor 3: {record.auditor_3.name}, Technical Expert: {record.expert.name}, Remark: {record.remarks}, Mandays: {record.mandayss}, Metode Audit: {record.metode}")
        return record

    def write(self, vals):
        res = super(PartnerCertificateISPO, self).write(vals)
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Updated Audit Type: {record.audit_type}, Date Start: {record.date_start}, Date End:{record.date_end}, Lead Auditor: {record.lead_auditor.name}, Auditor: {record.auditor.name}, Auditor 2: {record.auditor_2.name}, Auditor 3: {record.auditor_3.name}, Technical Expert: {record.expert.name}, Remark: {record.remarks}, Mandays: {record.mandayss}, Metode Audit: {record.metode}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Deleted Audit Type: {record.audit_type}, Date Start: {record.date_start}, Date End:{record.date_end}, Lead Auditor: {record.lead_auditor.name}, Auditor: {record.auditor.name}, Auditor 2: {record.auditor_2.name}, Auditor 3: {record.auditor_3.name}, Technical Expert: {record.expert.name}, Remark: {record.remarks}, Mandays: {record.mandayss}, Metode Audit: {record.metode}")
        return super(PartnerCertificateISPO, self).unlink()

class PartnerCertificatesISPO(models.Model):
    _name           = 'ops.program.aktual_ispo'
    _description    = 'certificate'

    reference_id        = fields.Many2one('ops.program.ispo', string="Reference", tracking=True)
    referance_id = fields.Many2one('ops.plan.ispo', string="Reference", tracking=True)
    audit_type          = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('surveilance1',    'Surveilance 1'),
                            ('surveilance2',    'Surveilance 2'),
                            ('surveilance3',    'Surveilance 3'),
                            ('surveilance4',    'Surveilance 4'),
                            ('recertification',    'Recertification'),
                            # ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], tracking=True)
    date_start          = fields.Date(string='Date Start', tracking=True)
    date_end            = fields.Date(string='Date End', tracking=True)
    lead_auditor        = fields.Many2one('hr.employee', string="Lead Auditor", tracking=True)
    auditor             = fields.Many2one('hr.employee', string="Auditor", tracking=True)
    auditor_2             = fields.Many2one('hr.employee', string="Auditor 2", tracking=True)
    auditor_3             = fields.Many2one('hr.employee', string="Auditor 3", tracking=True)
    expert              = fields.Many2one('hr.employee', string="Technical Expert", tracking=True)
    remarks             = fields.Text(string='Remarks', tracking=True)
    mandayss            = fields.Char(string="Mandays", tracking=True)
    metode              = fields.Selection(string='Metode Audit', selection=[
                            ('online',   'Online'), 
                            ('onsite',   'Onsite'), 
                            ('hybrid',   'Hybrid'), 
                            ], tracking=True)

    @api.model
    def create(self, vals):
        record = super(PartnerCertificatesISPO, self).create(vals)
        partner = record.reference_id
        partner.message_post(body=f"Created Audit Type: {record.audit_type}, Date Start: {record.date_start}, Date End: {record.date_end}, Lead Auditor: {record.lead_auditor.name}, Auditor: {record.auditor.name}, Auditor 2: {record.auditor_2.name}, Auditor 3: {record.auditor_3.name}, Technical Expert: {record.expert.name}, Remark: {record.remarks}, Mandays: {record.mandayss}, Metode Audit: {record.metode}")
        return record

    def write(self, vals):
        res = super(PartnerCertificatesISPO, self).write(vals)
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Updated Audit Type: {record.audit_type}, Date Start: {record.date_start}, Date End:{record.date_end}, Lead Auditor: {record.lead_auditor.name}, Auditor: {record.auditor.name}, Auditor 2: {record.auditor_2.name}, Auditor 3: {record.auditor_3.name}, Technical Expert: {record.expert.name}, Remark: {record.remarks}, Mandays: {record.mandayss}, Metode Audit: {record.metode}")
        return res

    def unlink(self):
        for record in self:
            partner = record.reference_id
            partner.message_post(body=f"Deleted Audit Type: {record.audit_type}, Date Start: {record.date_start}, Date End:{record.date_end}, Lead Auditor: {record.lead_auditor.name}, Auditor: {record.auditor.name}, Auditor 2: {record.auditor_2.name}, Auditor 3: {record.auditor_3.name}, Technical Expert: {record.expert.name}, Remark: {record.remarks}, Mandays: {record.mandayss}, Metode Audit: {record.metode}")
        return super(PartnerCertificatesISPO, self).unlink()                        
