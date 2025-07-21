from odoo import models, fields, api, SUPERUSER_ID, _
import requests
import json

import logging
_logger = logging.getLogger(__name__)

class AuditPlan(models.Model):
    _name           = 'ops.plan'
    _description    = 'Audit Plan'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Document No', tracking=True)
    iso_reference   = fields.Many2one('tsi.iso', string="Reference")    

    notification_id = fields.Many2one('audit.notification', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

# related, ea_code ???
    customer            = fields.Many2one('res.partner', string="Customer", compute='_compute_customer', store=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", compute='_compute_customer', store=True)
    head_office         = fields.Char(string="Jumlah Head Office", compute='_compute_customer', store=True)
    site_office         = fields.Char(string="Jumlah Site Office", compute='_compute_customer', store=True)
    off_location        = fields.Char(string="Jumlah Off Location", compute='_compute_customer', store=True)
    part_time           = fields.Char(string="Jumlah Part Time", compute='_compute_customer', store=True)
    subcon              = fields.Char(string="Jumlah Sub Contractor", compute='_compute_customer', store=True)
    unskilled           = fields.Char(string="Jumlah Unskilled", compute='_compute_customer', store=True)
    seasonal            = fields.Char(string="Jumlah Seasonal", compute='_compute_customer', store=True)
    total_emp           = fields.Integer(string="Total Employee", compute='_compute_customer', store=True)
    scope               = fields.Text('Scope', compute='_compute_customer', store=True)
    boundaries          = fields.Text('Boundaries', compute='_compute_customer', store=True)
    # boundaries_id  = fields.Many2many('tsi.iso.boundaries', string="Boundaries", related="iso_reference.boundaries_id")
    telepon             = fields.Char(string="No Telepon", compute='_compute_customer', store=True)

    ea_code             = fields.Many2one('tsi.ea_code', string="IAF Code", related="program_id.ea_code", tracking=True)
    ea_code_plan        = fields.Many2many('tsi.ea_code', 'rel_ops_plan_ea_code', string="IAF Code Existing", related="program_id.ea_code_prog")
    program_id          = fields.Many2one('ops.program', string='Program', tracking=True)
    type_cient          = fields.Char(string="Seasonal", tracking=True)
    apprev_date         = fields.Date(string="Review Date", tracking=True)    
    contract_date       = fields.Datetime(string="Contract Date", tracking=True)      
    contract_number     = fields.Char(string="Contract Number", tracking=True)    
    dokumen_sosialisasi        = fields.Binary('Organization Chart', tracking=True)
    file_name1      = fields.Char('Filename', tracking=True)
    criteria        = fields.Char(string='Criteria', tracking=True)
    #bisa pilih salah satu
    # boundaries      = fields.Text(string='Boundaries')


# form
    contract_number     = fields.Char('Contract Number', tracking=True)
    audit_start         = fields.Date('Audit Start', tracking=True)
    audit_end           = fields.Date('Audit End', tracking=True)
    certification_type  = fields.Selection([
                            ('Single Site',  'SINGLE SITE'),
                            ('Multi Site',   'MULTI SITE'),
                        ], string='Certification Type', index=True, readonly=True, related='iso_reference.certification', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    audit_criteria      = fields.Char('Audit Criteria', tracking=True)
    audit_method        = fields.Selection(string='Metode Audit', selection=[
                            ('online',   'Online'), 
                            ('onsite',   'Onsite'), 
                            ('hybrid',   'Hybrid'), 
                            ], tracking=True)

    technical_expert    = fields.Many2one('hr.employee', string='Technical Expert', tracking=True)
    auditor_lead        = fields.Many2one('hr.employee', string="Lead Auditor", tracking=True)
    auditor_1           = fields.Many2one('hr.employee', string='Auditor 1', tracking=True)
    auditor_2           = fields.Many2one('hr.employee', string='Auditor 2', tracking=True)
    auditor_3           = fields.Many2one('hr.employee', string='Auditor 3', tracking=True)

    kan_1               = fields.Char('Name 1', tracking=True)
    kan_2               = fields.Char('Name 2', tracking=True)

    kan_function        = fields.Selection([
                            ('observer', 'Observer'),
                            ('expert',    'Technical Expert'),
                            ('witness',    'Witness'),
                        ], string='Function', tracking=True)
    program_id = fields.Many2one('ops.program', string='Program Reference')
    audit_stage           = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('surveilance1',    'Surveilance 1'),
                            ('surveilance2',    'Surveilance 2'),
                            ('recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], tracking=True)

    audit_objectives    = fields.Many2many('ops.objectives',string='Audit Objectives')

    plan_detail_ids = fields.One2many('ops.plan_detail', 'plan_id', string="Plan", index=True)
    plan_objectives_ids = fields.One2many('ops.objectives', 'plan_id', string="Plan", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('waiting_finance', 'Waiting Finance Set Lunas DP'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new')
    type_client         = fields.Selection([
                            ('termin',     'Termin'),
                            ('lunasawal',   'Lunas di Awal'),
                            ('lunasakhir',  'Lunas di Akhir')
                        ], string='Type Client', tracking=True, related="program_id.type_client")

    @api.depends('iso_reference', 'program_id')
    def _compute_customer(self):
        for rec in self:
            if rec.iso_reference:
                rec.customer = rec.iso_reference.customer
                rec.contact_person = rec.iso_reference.contact_person
                rec.head_office = rec.iso_reference.head_office
                rec.telepon = rec.iso_reference.telepon
                rec.scope = rec.iso_reference.scope
            elif rec.program_id:
                rec.customer = rec.program_id.customer
                rec.contact_person = rec.program_id.contact_person
                rec.head_office = rec.program_id.head_office
                rec.telepon = rec.program_id.telepon
                rec.scope = rec.program_id.scope
                rec.ea_code = rec.program_id.ea_code
                rec.contract_number = rec.program_id.contract_number
                rec.contract_date = rec.program_id.contract_date
            else:
                rec.customer = False
                rec.contact_person = False
                rec.head_office = False
                rec.telepon = False
                rec.scope = False
                rec.ea_code = False
                rec.contract_number = False
                rec.contract_date = False

    def send_whatsapp_status_done_to_finance(self):
        dokumen_id = self.sales_order_id.id
        nama_dokumen = self.sales_order_id.name
        nama_customer = self.sales_order_id.partner_id.name
        standard = self.iso_standard_ids.name
        audit_stage_map = {
            'Stage-01':'Stage 1',
            'Stage-02':'Stage 2',
            'surveilance1':'Surveilance 1',
            'surveilance2':'Surveilance 2',
            'Recertification':'Recertification',
            'special':'Special Audit'
        }

        tahap_audit = self.audit_stage
        tahap_audit_label = audit_stage_map.get(tahap_audit, 'Unknown')
        
        user = self.env['res.users'].sudo().search([("id", "=", 11)])
        nomor = user.sudo().employee_ids.phone_wa 
        
        dokumen_id = self.id
        url = "web#id=%s&menu_id=720&action=964&model=sale.order&view_type=form" % (dokumen_id)
        
        payload = {
                "messaging_product": "whatsapp",
                "to": nomor,
                "type": "template",
                "template": {
                    "name": "template_notif_status_done_to_finance_url_draf",
                    "language": {
                        "code": "en"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": nama_dokumen
                                },
                                {
                                    "type": "text",
                                    "text": nama_customer
                                },
                                {
                                    "type": "text",
                                    "text": standard
                                },
                                {
                                    "type": "text",
                                    "text": tahap_audit_label
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "url",
                            "index": 0,
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": url
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
                _logger.info("WhatsApp message sent successfully.")
                
            else:
                _logger.error("Failed to send WhatsApp message: %s", response.text)
        except Exception as e:
            _logger.exception("An error occurred while sending WhatsApp message: %s", e)

    def set_to_confirm(self):
        self.write({'state': 'confirm'})
        for plan in self:
            # Ambil semua record ops.program.aktual yang terhubung dengan plan ini
            program_lines = self.env['ops.program.aktual'].search([('referance_id', '=', plan.id)])
            for program_line in program_lines:
                # Ambil record ops.program yang terhubung dengan ops.program.aktual ini
                program = self.env['ops.program'].search([('program_lines_aktual', 'in', program_line.id)])
                if program:
                    # Update audit_stage di ops.program berdasarkan audit_stage di ops.plan
                    program.write({
                        'audit_stage': plan.audit_stage
                    })            
        return True

    def set_to_done(self):
        for rec in self:
            if rec.type_client == 'termin':
                rec.state = 'waiting_finance'
                # Call send_whatsapp_status_done_to_finance method jika state 'waiting_finance'
                self.send_whatsapp_status_done_to_finance()
            else:
                rec.state = 'done'
                # Call send_whatsapp_status_done_to_finance method jika state 'done'
                self.send_whatsapp_status_done_to_finance()
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.plan')
        vals['name'] = sequence or _('New')
        result = super(AuditPlan, self).create(vals)
        return result

    def generate_stage1_report(self):
        # Code to generate Stage 1 report
        return self.env.ref('v15_tsi.report_plan_stage1').report_action(self)

    def generate_stage2_report(self):
        # Code to generate Stage 2 report
        return self.env.ref('v15_tsi.report_plan_stage2').report_action(self)
    
    def generate_survilance1_report(self):
        # Code to generate Stage 2 report
        return self.env.ref('v15_tsi.report_plan_surveillance1').report_action(self)
    
    def generate_survilance2_report(self):
        # Code to generate Stage 2 report
        return self.env.ref('v15_tsi.report_plan_surveillance2').report_action(self)

    def generate_report(self):
        if self.audit_stage == 'Stage-01':
            self.generate_stage1_report()
        elif self.audit_stage == 'Stage-02':
            self.generate_stage2_report()
        elif self.audit_stage == 'Survillance-1':
            self.generate_survilance1_report()
        elif self.audit_stage == 'Survillance-2':
            self.generate_survilance2_report()
        # elif self.audit_type == 'recertification':
        #     self.generate_recertification_report()

class AuditPlanDetail(models.Model):
    _name           = 'ops.plan_detail'
    _description    = 'Audit Plan Detail'

    plan_id         = fields.Many2one('ops.plan', string="Plan", ondelete='cascade', index=True, tracking=True)
    auditor         = fields.Char(string='Auditor', tracking=True)
    time            = fields.Char(string='Time', tracking=True)
    function        = fields.Many2one('ops.plan_function', string='Function', tracking=True)
    agenda          = fields.Many2many('ops.plan_agenda', string='Agenda', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditPlanDetail, self).create(vals)
        partner = record.plan_id
        partner.message_post(body=f"Created Auditor: {record.auditor}, Time: {record.time}, Function: {record.function.name}, Agenda: {record.agenda}")
        return record

    def write(self, vals):
        res = super(AuditPlanDetail, self).write(vals)
        for record in self:
            partner = record.plan_id
            partner.message_post(body=f"Updated Auditor: {record.auditor}, Time: {record.time}, Function: {record.function.name}, Agenda: {record.agenda.kode.name}")
        return res

    def unlink(self):
        for record in self:
            partner = record.plan_id
            partner.message_post(body=f"Deleted Auditor: {record.auditor}, Time: {record.time}, Function: {record.function.name}, Agenda: {record.agenda.kode.name}")
        return super(AuditPlanDetail, self).unlink()


class AuditPlanFunction(models.Model):
    _name           = 'ops.plan_function'
    _description    = 'Audit Plan Function'

    name            = fields.Char(string='Name')

class AuditPlangenda(models.Model):
    _name           = 'ops.plan_agenda'
    _description    = 'Audit Plan Agenda'

    kode            = fields.Char(string='Kode')
    name            = fields.Char(string='Name')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')

    def name_get(self):
        result = []	
        for rec in self:
            result.append((rec.id, '[%s] %s' % (rec.kode,rec.name)))	
        return result

class AuditObjectives(models.Model):
    _name = 'ops.objectives'
    _description = 'Audit Objectives'

    plan_id = fields.Many2one('ops.plan', string="Plan", ondelete='cascade', index=True, tracking=True)
    audit_stage = fields.Selection([
        ('ia_1', 'Stage 1'),
        ('ia_2', 'Stage 2'),
        ('sv_1', 'Surveilance 1'),
        ('sv_2', 'Surveilance 2'),
        ('recert', 'Recertification'),
        ('special', 'Special Audit')
    ], tracking=True)
    name = fields.Char(string='Objectives', tracking=True)
    iso_standard_ids = fields.Many2many('tsi.iso.standard', string='Standards', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditObjectives, self).create(vals)
        partner = record.plan_id
        if partner:
            standards = ", ".join(record.iso_standard_ids.mapped('name'))
            partner.message_post(body=f"Created Audit Stage: {record.audit_stage}, Objectives: {record.name}, Standards: {standards}")
        return record

    def write(self, vals):
        res = super(AuditObjectives, self).write(vals)
        for record in self:
            partner = record.plan_id
            if partner:
                standards = ", ".join(record.iso_standard_ids.mapped('name'))
                partner.message_post(body=f"Updated Audit Stage: {record.audit_stage}, Objectives: {record.name}, Standards: {standards}")
        return res

    def unlink(self):
        for record in self:
            partner = record.plan_id
            if partner:
                standards = ", ".join(record.iso_standard_ids.mapped('name'))
                partner.message_post(body=f"Deleted Audit Stage: {record.audit_stage}, Objectives: {record.name}, Standards: {standards}")
        return super(AuditObjectives, self).unlink()

