from odoo import models, fields, api, SUPERUSER_ID, _

class AuditPlanISPO(models.Model):
    _name           = 'ops.plan.ispo'
    _description    = 'Audit Plan'
    _order          = 'id DESC'
    _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Document No', tracking=True)
    ispo_reference   = fields.Many2one('tsi.ispo', string="Reference")    

    notification_id = fields.Many2one('audit.notification.ispo', string="Notification")    
    sales_order_id      = fields.Many2one('sale.order', string="Sales Order",  readonly=True)    

# related, ea_code ???
    customer            = fields.Many2one('res.partner', string="Customer", related='ispo_reference.customer', tracking=True)
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')
    contact_person      = fields.Char(string="Contact Person", related='ispo_reference.contact_person', tracking=True)
    head_office         = fields.Char(string="Jumlah Head Office", related='ispo_reference.head_office', tracking=True)
    site_office         = fields.Char(string="Jumlah Site Office", related='ispo_reference.site_office', tracking=True)
    off_location        = fields.Char(string="Jumlah Off Location", related='ispo_reference.off_location', tracking=True)
    part_time           = fields.Char(string="Jumlah Part Time", related='ispo_reference.part_time', tracking=True)
    subcon              = fields.Char(string="Jumlah Sub Contractor", related='ispo_reference.subcon', tracking=True)
    unskilled           = fields.Char(string="Jumlah Unskilled", related='ispo_reference.unskilled', tracking=True)
    seasonal            = fields.Char(string="Jumlah Seasonal", related='ispo_reference.seasonal', tracking=True)
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

    ea_code             = fields.Many2one('tsi.ea_code', string="EA Code", related="program_id.ea_code", tracking=True)
    program_id          = fields.Many2one('ops.program.ispo', string='Program', tracking=True)
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
                        ], string='Certification Type', index=True, readonly=True, related='ispo_reference.certification', tracking=True)
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
    program_id = fields.Many2one('ops.program.ispo', string='Program Reference')
    audit_stage           = fields.Selection([
                            ('Stage-01',     'Stage 1'),
                            ('Stage-02', 'Stage 2'),
                            ('surveilance1',    'Surveilance 1'),
                            ('surveilance2',    'Surveilance 2'),
                            ('surveilance3',    'Surveilance 3'),
                            ('surveilance4',    'Surveilance 4'),
                            ('Recertification',    'Recertification'),
                            ('special',    'Special Audit')
                        ], string='Audit Type', tracking=True)

    audit_objectives    = fields.Many2many('ops.objectives.ispo',string='Audit Objectives')

    plan_detail_ids = fields.One2many('ops.plan_detail.ispo', 'plan_id', string="Plan", index=True)
    plan_objectives_ids = fields.One2many('ops.objectives.ispo', 'plan_id', string="Plan", index=True)
    state           = fields.Selection([
                            ('new',     'New'),
                            ('confirm', 'Confirm'),
                            ('done',    'Done')
                        ], string='Status', readonly=True, copy=False, index=True, default='new', tracking=True)

    def set_to_confirm(self):
        self.write({'state': 'confirm'})            
        return True

    def set_to_done(self):
        self.write({'state': 'done'})            
        return True

    def set_to_draft(self):
        self.write({'state': 'new'})            
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('ops.plan.ispo')
        vals['name'] = sequence or _('New')
        result = super(AuditPlanISPO, self).create(vals)
        return result

    # def generate_stage1_report(self):
    #     # Code to generate Stage 1 report
    #     return self.env.ref('v15_tsi.report_plan_stage1').report_action(self)

    # def generate_stage2_report(self):
    #     # Code to generate Stage 2 report
    #     return self.env.ref('v15_tsi.report_plan_stage2').report_action(self)
    
    # def generate_survilance1_report(self):
    #     # Code to generate Stage 2 report
    #     return self.env.ref('v15_tsi.report_plan_surveillance1').report_action(self)
    
    # def generate_survilance2_report(self):
    #     # Code to generate Stage 2 report
    #     return self.env.ref('v15_tsi.report_plan_surveillance2').report_action(self)

    # def generate_report(self):
    #     if self.audit_stage == 'Stage-01':
    #         self.generate_stage1_report()
    #     elif self.audit_stage == 'Stage-02':
    #         self.generate_stage2_report()
    #     elif self.audit_stage == 'Survillance-1':
    #         self.generate_survilance1_report()
    #     elif self.audit_stage == 'Survillance-2':
    #         self.generate_survilance2_report()
    #     # elif self.audit_type == 'recertification':
    #     #     self.generate_recertification_report()

class AuditPlanDetailISPO(models.Model):
    _name           = 'ops.plan_detail.ispo'
    _description    = 'Audit Plan Detail'

    plan_id         = fields.Many2one('ops.plan.ispo', string="Plan", ondelete='cascade', index=True, tracking=True)
    auditor         = fields.Char(string='Auditor', tracking=True)
    time            = fields.Char(string='Time', tracking=True)
    function        = fields.Many2one('ops.plan_function.ispo', string='Function', tracking=True)
    agenda          = fields.Many2many('ops.plan_agenda.ispo', string='Agenda', tracking=True)

    @api.model
    def create(self, vals):
        record = super(AuditPlanDetailISPO, self).create(vals)
        partner = record.plan_id
        partner.message_post(body=f"Created Auditor: {record.auditor}, Time: {record.time}, Function: {record.function.name}, Agenda: {record.agenda}")
        return record

    def write(self, vals):
        res = super(AuditPlanDetailISPO, self).write(vals)
        for record in self:
            partner = record.plan_id
            partner.message_post(body=f"Updated Auditor: {record.auditor}, Time: {record.time}, Function: {record.function.name}, Agenda: {record.agenda.kode.name}")
        return res

    def unlink(self):
        for record in self:
            partner = record.plan_id
            partner.message_post(body=f"Deleted Auditor: {record.auditor}, Time: {record.time}, Function: {record.function.name}, Agenda: {record.agenda.kode.name}")
        return super(AuditPlanDetailISPO, self).unlink()


class AuditPlanFunctionISPO(models.Model):
    _name           = 'ops.plan_function.ispo'
    _description    = 'Audit Plan Function'

    name            = fields.Char(string='Name')

class AuditPlangendaISPO(models.Model):
    _name           = 'ops.plan_agenda.ispo'
    _description    = 'Audit Plan Agenda'

    kode            = fields.Char(string='Kode')
    name            = fields.Char(string='Name')
    iso_standard_ids    = fields.Many2many('tsi.iso.standard', string='Standards')

    def name_get(self):
        result = []	
        for rec in self:
            result.append((rec.id, '[%s] %s' % (rec.kode,rec.name)))	
        return result

class AuditObjectivesISPO(models.Model):
    _name = 'ops.objectives.ispo'
    _description = 'Audit Objectives'

    plan_id = fields.Many2one('ops.plan.ispo', string="Plan", ondelete='cascade', index=True, tracking=True)
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
        record = super(AuditObjectivesISPO, self).create(vals)
        partner = record.plan_id
        if partner:
            standards = ", ".join(record.iso_standard_ids.mapped('name'))
            partner.message_post(body=f"Created Audit Stage: {record.audit_stage}, Objectives: {record.name}, Standards: {standards}")
        return record

    def write(self, vals):
        res = super(AuditObjectivesISPO, self).write(vals)
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
        return super(AuditObjectivesISPO, self).unlink()

