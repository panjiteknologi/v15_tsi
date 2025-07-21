from odoo import models, fields, api, SUPERUSER_ID, _, tools

class Hazard(models.Model):
    _name           = 'tsi.hazard'
    _description    = 'Hazard'

    name            = fields.Char(string='Nama')

class EnvAspect(models.Model):
    _name           = 'tsi.env_aspect'
    _description    = 'Environmental Aspect'

    name            = fields.Char(string='Nama')

class AltScope(models.Model):
    _name           = 'tsi.alt_scope'
    _description    = 'Alt Scope'

    name            = fields.Char(string='Nama')

class ISPOFindingType(models.Model):
    _name           = 'ispo.finding.type'
    _description    = 'ISPO Finding Type'

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)

class PencapaianChartCRM(models.Model): 
    _name = 'pencapaian.chart.crm'
    _description = 'Pencapaian Chart CRM'
    _auto = False

    issue_date = fields.Date(string="Date", store=True)
    issue_year = fields.Char(string="Year", store=True)
    issue_month = fields.Char(string="Month", store=True)
    sales = fields.Many2one('res.users', string="Sales Person", store=True)
    closing_by = fields.Selection([
                ('konsultan',  'Konsultan'),
                ('direct',   'Direct'),
                ], string='Closing By', store=True)
    state_crm =fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('lanjut', 'Lanjut'),
            ('lost','Loss'),
            ('suspend', 'Suspend'),
            ], string='Status', store=True)
    category = fields.Selection([
                ('bronze',  'Bronze'),
                ('silver',   'Silver'),
                ('gold', 'Gold')
                ], string='Kategori', store=True)
    audit_stage = fields.Selection([
                            ('surveilance1',     'Surveillance 1'),
                            ('surveilance2',     'Surveillance 2'),
                            # ('surveilance3',     'Surveillance 3'),
                            # ('surveilance4',     'Surveillance 4'),
                            ('recertification', 'Recertification'),
                        ], string='Level Audit', tracking=True, store=True)
    referal = fields.Char(string='Referal', store=True)
    product_id = fields.Char(string="Standard", store=True)
    price = fields.Float(string="Value", store=True)
    reference_id = fields.Many2one('tsi.audit.request', string="Audit Reference", store=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "pencapaian_chart_crm")
        self.env.cr.execute("""
            CREATE VIEW pencapaian_chart_crm AS (
                SELECT
                    l.id AS id,
                    a.issue_date AS issue_date,
                    TO_CHAR(a.issue_date, 'YYYY') AS issue_year,  -- Tahun (Col di Chart)
                    TO_CHAR(a.issue_date, 'Month') AS issue_month, -- Bulan (Row di Chart)
                    CASE 
                        WHEN pt.name ILIKE '%ISPO%' THEN 'ISPO' 
                        ELSE 'ISO' 
                    END AS product_id,
                    l.price AS price,
                    a.audit_stage AS audit_stage,
                    a.state_crm AS state_crm,
                    a.referal AS referal,
                    a.closing_by AS closing_by,
                    a.category AS category,
                    a.sales AS sales
                FROM audit_request_line l
                JOIN tsi_audit_request a ON l.reference_id = a.id
                JOIN product_product p ON l.product_id = p.id
                JOIN product_template pt ON p.product_tmpl_id = pt.id
                WHERE EXTRACT(YEAR FROM a.issue_date) 
                    BETWEEN EXTRACT(YEAR FROM CURRENT_DATE) 
                    AND EXTRACT(YEAR FROM CURRENT_DATE) + 2
            )
        """)

class PencapaianChartCRMISPO(models.Model): 
    _name = 'pencapaian.chart.crm.ispo'
    _description = 'Pencapaian Chart CRM ISPO'
    _auto = False

    issue_date = fields.Date(string="Date", store=True)
    issue_year = fields.Char(string="Year", store=True)
    issue_month = fields.Char(string="Month", store=True)
    sales = fields.Many2one('res.users', string="Sales Person", store=True)
    closing_by = fields.Selection([
                ('konsultan',  'Konsultan'),
                ('direct',   'Direct'),
                ], string='Closing By', store=True)
    state_crm =fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ('reject', 'Reject'),
            ('lanjut', 'Lanjut'),
            ('lost','Loss'),
            ('suspend', 'Suspend'),
            ], string='Status', store=True)
    category = fields.Selection([
                ('bronze',  'Bronze'),
                ('silver',   'Silver'),
                ('gold', 'Gold')
                ], string='Kategori', store=True)
    audit_stage = fields.Selection([
                    ('surveilance1',     'Surveilance 1'),
                    ('surveilance2',     'Surveilance 2'),
                    ('surveilance3',     'Surveilance 3'),
                    ('surveilance4',     'Surveilance 4'),
                    ('recertification', 'Recertification'),
                ], string='Audit Stage', tracking=True)
    referal = fields.Char(string='Referal', store=True)
    product_id = fields.Char(string="Standard", store=True)
    price = fields.Float(string="Value", store=True)
    reference_id  = fields.Many2one('tsi.audit.request.ispo', string="Reference")

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "pencapaian_chart_crm_ispo")
        self.env.cr.execute("""
            CREATE VIEW pencapaian_chart_crm_ispo AS (
                SELECT
                    l.id AS id,
                    a.issue_date AS issue_date,
                    TO_CHAR(a.issue_date, 'YYYY') AS issue_year,  -- Tahun (Col di Chart)
                    TO_CHAR(a.issue_date, 'Month') AS issue_month, -- Bulan (Row di Chart)
                    'ISPO' AS product_id,
                    l.price AS price,
                    a.audit_stage AS audit_stage,
                    a.state_crm AS state_crm,
                    a.referal AS referal,
                    a.closing_by AS closing_by,
                    a.category AS category,
                    a.sales AS sales
                FROM audit_request_ispo_line l
                JOIN tsi_audit_request_ispo a ON l.reference_id = a.id
                JOIN product_product p ON l.product_id = p.id
                JOIN product_template pt ON p.product_tmpl_id = pt.id
                WHERE EXTRACT(YEAR FROM a.issue_date) 
                    BETWEEN EXTRACT(YEAR FROM CURRENT_DATE) 
                    AND EXTRACT(YEAR FROM CURRENT_DATE) + 2
            )
        """)

class ChartTargetActual(models.Model): 
    _name = 'chart.target.actual'
    _description = 'Chart Target Actual'
    _auto = False

    issue_date = fields.Date(string="Date", store=True)
    issue_year = fields.Char(string="Year", store=True)
    issue_month = fields.Char(string="Month", store=True)
    tipe = fields.Selection([
        ('actual', 'Actual'),
        ('target', 'Target'),
    ], string='Type', store=True)
    product_id = fields.Char(string="Standard", store=True)
    price = fields.Float(string="Value", store=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "chart_target_actual")
        self.env.cr.execute("""
            CREATE VIEW chart_target_actual AS (

                -- Data Actual dari tsi.audit.request
                SELECT 
                    l.id AS id,
                    a.issue_date AS issue_date,
                    TO_CHAR(a.issue_date, 'YYYY') AS issue_year,
                    TO_CHAR(a.issue_date, 'MM') AS issue_month,
                    CASE 
                        WHEN pt.name ILIKE '%ISPO%' THEN 'ISPO' 
                        ELSE 'ISO' 
                    END AS product_id,
                    l.price AS price,
                    'actual' AS tipe  
                FROM audit_request_line l
                JOIN tsi_audit_request a ON l.reference_id = a.id
                JOIN product_product p ON l.product_id = p.id
                JOIN product_template pt ON p.product_tmpl_id = pt.id
                WHERE pt.name NOT ILIKE '%ISPO%' -- Hanya mengambil selain ISPO

                UNION ALL

                -- Data Target dari crm.target.actual (Hanya yang ISO)
                SELECT 
                    t.id + 100000 AS id, -- Tambahkan ID agar unik
                    TO_DATE(t.year || '-' || t.month || '-01', 'YYYY-MM-DD') AS issue_date,
                    t.year AS issue_year,
                    t.month AS issue_month,
                    'ISO' AS product_id,  -- Hanya mengambil data yang ISO
                    t.nilai AS price,
                    'target' AS tipe  
                FROM crm_target_actual t
                WHERE t.pencapaian_crm = 'iso' -- Hanya mengambil data dengan pencapaian_crm = 'ISO'
            );
        """)

class ChartTargetActualISPO(models.Model): 
    _name = 'chart.target.actual.ispo'
    _description = 'Chart Target Actual ISPO'
    _auto = False

    issue_date = fields.Date(string="Date", store=True)
    issue_year = fields.Char(string="Year", store=True)
    issue_month = fields.Char(string="Month", store=True)
    tipe = fields.Selection([
        ('actual', 'Actual'),
        ('target', 'Target'),
    ], string='Type', store=True)
    product_id = fields.Char(string="Standard", store=True)
    price = fields.Float(string="Value", store=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, "chart_target_actual_ispo")
        self.env.cr.execute("""
            CREATE VIEW chart_target_actual_ispo AS (

                -- Data Actual dari tsi.audit.request.ispo
                SELECT 
                    l.id AS id,
                    a.issue_date AS issue_date,
                    TO_CHAR(a.issue_date, 'YYYY') AS issue_year,
                    TO_CHAR(a.issue_date, 'MM') AS issue_month,
                    'ISPO' AS product_id,
                    l.price AS price,
                    'actual' AS tipe  
                FROM audit_request_ispo_line l
                JOIN tsi_audit_request_ispo a ON l.reference_id = a.id
                JOIN product_product p ON l.product_id = p.id
                JOIN product_template pt ON p.product_tmpl_id = pt.id
                WHERE pt.name ILIKE '%ISPO%' -- Hanya mengambil ISPO

                UNION ALL

                -- Data Target dari crm.target.actual (Hanya yang ISPO)
                SELECT 
                    t.id + 100000 AS id, -- Tambahkan ID agar unik
                    TO_DATE(t.year || '-' || t.month || '-01', 'YYYY-MM-DD') AS issue_date,
                    t.year AS issue_year,
                    t.month AS issue_month,
                    'ISPO' AS product_id,  -- Hanya mengambil data yang ISPO
                    t.nilai AS price,
                    'target' AS tipe  
                FROM crm_target_actual t
                WHERE t.pencapaian_crm = 'ispo' -- Hanya mengambil data dengan pencapaian_crm = 'ISPO'
            );
        """)