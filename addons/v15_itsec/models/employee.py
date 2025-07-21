from odoo import models, fields, api
from datetime import datetime

# HR Kompetensi Values
class comp_values(models.Model):
    _name           = 'itsec.comp_values'
    _description    = 'Assesment Competency QMS'
    _rec_name       = 'name'
    _order          = 'id DESC'

    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
        ('ABMS', 'ABMS'),
        ('HACCP', 'HACCP'),
        ('FSMS', 'FSMS'),
    ], string='Type Schema', store=True)
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    line_assesment_qms   = fields.One2many('itsec.line_assesment_qms', 'assesment_qms_id')

    @api.onchange('type_schema')
    def _onchange_type_schema(self):
        if self.type_schema:
            standard_kompetensi = self.env['itsec.standard.kompetensi'].search([
                ('type_schema', '=', self.type_schema)
            ], limit=1)

            self.line_assesment_qms = [(5, 0, 0)]
            lines = []

            evidence_training = ""
            evidence_experience = ""
            evidence_education = ""

            if self.name and self.type_schema:
                training_list = [
                    f"{t.name} - {t.periode}" for t in self.name.training_ids
                    if t.type_schema == self.type_schema
                ]
                experience_list = [
                    f"{e.name} - {e.periode}" for e in self.name.experience_ids
                    if e.type_schema == self.type_schema
                ]
                education_list = [
                    f"{ed.name} - {ed.periode}" for ed in self.name.education_ids
                ]

                evidence_training = "\n".join(training_list)
                evidence_experience = "\n".join(experience_list)
                evidence_education = "\n".join(education_list)

            for line in standard_kompetensi.line_standard_kompetensi:
                lines.append((0, 0, {
                    'nomor': line.no,
                    'standard': line.standard,
                    'requirement': line.requierement,
                    'evidence_training': evidence_training,
                    'evidence_experience': evidence_experience,
                    'evidence_education': evidence_education,
                }))

            self.line_assesment_qms = lines



    def set_to_running(self):
        self.write({'state': 'approval'})
        return action

# Kompetensi General
class kompetensi(models.Model):
    _name           = 'itsec.kompetensi'
    _inherit        = 'mail.thread'
    _description    = 'Kompetensi Karyawan'
    _rec_name       = 'name'
    _order          = 'id DESC'

    name = fields.Many2one(
            comodel_name='hr.employee',
            string="Name of Candidate",
        )
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    line_assesment   = fields.One2many('itsec.line_assesment_general', 'assesment_competency_id')
    hardskill_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id1')
    softskill_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id2')
    education_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id7')
    training_ids    = fields.One2many('itsec.qms_extra', 'qms_extra_id9')

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action
    
    @api.model
    def create(self, vals):
        record = super(kompetensi, self).create(vals)

        # Ambil employee yang dipilih dari field 'name'
        employee = record.name

        # Siapkan isi evidence gabungan dari employee
        evidence_combined = []

        # Pastikan 'name' (hr.employee) ada
        if employee:
            # Ambil data training, experience, dan education
            training_list = [f"Training: {t.name} - {t.periode}" for t in employee.training_ids]
            experience_list = [f"Experience: {e.name} - {e.periode}" for e in employee.experience_ids]
            education_list = [f"Education: {ed.name} - {ed.periode}" for ed in employee.education_ids]

            # Gabungkan semua evidence menjadi satu list
            evidence_combined.extend(training_list)
            evidence_combined.extend(experience_list)
            evidence_combined.extend(education_list)

        # Gabungkan semua evidence dalam satu string, dipisahkan dengan newline
        evidence_string = "\n".join(evidence_combined)

        default_lines = [
            {
                "nomor": 1,
                "requirement": "Knowledge of audit principles, practices and technique",
                "standard": (
                    "Education:\n"
                    "Has professional education which an equivalent level of university education\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year in management system practitioner as consultant or "
                    "internal auditor or Management Representative\n\n"
                    "Training:\n"
                    "Has successfully completed at least five days of training, the scope of which "
                    "covers audit management based on ISO 19011 and specific standard of management "
                    "system (e.g. QMS, EMS, FSMS)"
                )
            },
            {
                "nomor": 2,
                "requirement": "Knowledge of specific management system standard/normative document",
                "standard": (
                    "Education:\n"
                    "Has professional education which an equivalent level of university education\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year in management system practitioner as consultant or "
                    "internal auditor or Management Representative\n\n"
                    "Training:\n"
                    "Has successfully completed at least five days of training, the scope of which "
                    "covers audit management based on ISO 19011 and specific standard of management "
                    "system (e.g. QMS, EMS, FSMS)"
                )
            },
            {
                "nomor": 3,
                "requirement": "Knowledge certification Body Processes",
                "standard": (
                    "Education, Experience and training is the same with above  \n"
                    "Additional  Training  (mandatory)  :  Knowledge  about  ISO/IEC  17021-1 latest version \n\n"
                )
            },
            {
                "nomor": 4,
                "requirement": "Knowledge of business management practices",
                "standard": (
                    "Education Background :\n"
                    "Has professional  education  which    an equivalent  level  of  university education  and  Has  the  majoring related  the scope of accreditation\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year  in  the  company  with  the  same sector/business"
                    "Has at least 10 mandays as 2nd / 3rd party auditor in management system (auditexperience may be from other CB’s)\n\n"
                    "Training:\n"
                    "Has successfully completed specific training in the business/sector related the scope of accreditation."
                )
            },
            {
                "nomor": 5,
                "requirement": "Knowledge client business/sector",
                "standard": (
                    "Education Background :\n"
                    "Has professional  education  which    an equivalent  level  of  university education  and  Has  the  majoring related  the scope of accreditation\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year  in  the  company  with  the  same sector/business"
                    "Has at least 10 mandays as 2nd / 3rd party auditor in management system (auditexperience may be from other CB’s)\n\n"
                    "Training:\n"
                    "Has successfully completed specific training in the business/sector related the scope of accreditation."
                )
            },
            {
                "nomor": 6,
                "requirement": "Knowledge client product/processes and organization",
                "standard": (
                    "Education Background :\n"
                    "Has professional  education  which    an equivalent  level  of  university education  and  Has  the  majoring related  the scope of accreditation\n\n"
                    "Work Experience:\n"
                    "Has at least 1 (one) year  in  the  company  with  the  same sector/business"
                    "Has at least 10 mandays as 2nd / 3rd party auditor in management system (auditexperience may be from other CB’s)\n\n"
                    "Training:\n"
                    "Has successfully completed specific training in the business/sector related the scope of accreditation."
                )
            },
            {
                "nomor": 7,
                "requirement": "Language skill appropriate to all levels within the client organization",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 8,
                "requirement": "Note talking and report writing skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 9,
                "requirement": "Presentation skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 10,
                "requirement": "Interviewing skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            {
                "nomor": 11,
                "requirement": "Audit Management skills",
                "standard": (
                    "Work experience (audit experience):\n"
                    "Has at least 10 mandays as 3rd party auditor  in  management  system (audit experience may be from other CB’s)\n\n"
                    "Other Criteria :\n"
                    "Has good result while conduct  the  audit  and  witnessed  by senior auditor"
                )
            },
            # Tambahkan baris lain jika perlu...
        ]

        for line in default_lines:
            # Buat baris 'line_assesment_general'
            line_assesment = self.env['itsec.line_assesment_general'].create({
                'assesment_competency_id': record.id,
                'nomor': line['nomor'],
                'requirement': line['requirement'],
                'standard': line['standard'],
            })

            # Buat satu record untuk evidence gabungan dalam satu line
            evidence_vals = [
                (0, 0, {
                    'training': evidence_string,  # Semua evidence digabungkan dalam satu string untuk training
                    'experience': "",  # Kosongkan karena kita sudah gabungkan dalam string 'training'
                    'education': "",  # Kosongkan karena kita sudah gabungkan dalam string 'education'
                })
            ]

            # Relasikan evidence ke 'line_assesment_general'
            line_assesment.write({
                'line_evidence_ids': evidence_vals
            })

        return record

class AssesmentCompetencyGeneral(models.Model):
    _name           = 'itsec.line_assesment_general'
    _description    = 'Assesment Kompetensi General'

    assesment_competency_id = fields.Many2one(
        'itsec.kompetensi', ondelete='cascade'
    )
    nomor                   = fields.Char(string="No")
    requirement             = fields.Text(string="Requirement")
    standard                = fields.Text(string="Standard")
    evaluator_comment       = fields.Char(string="Evaluator Comment")
    ass_method              = fields.Char(string="Assesment Method")
    line_evidence_ids       = fields.One2many('itsec.line_evidence','evidence_ids')
    evidence_education = fields.Text(string="Evidence - Education", compute="_compute_evidence_fields")
    evidence_experience = fields.Text(string="Evidence - Experience", compute="_compute_evidence_fields")
    evidence_training = fields.Text(string="Evidence - Training", compute="_compute_evidence_fields")

    @api.depends('line_evidence_ids')
    def _compute_evidence_fields(self):
        for rec in self:
            education_list = [str(e) for e in rec.line_evidence_ids.mapped('education') if e]
            experience_list = [str(e) for e in rec.line_evidence_ids.mapped('experience') if e]
            training_list = [str(e) for e in rec.line_evidence_ids.mapped('training') if e]

            rec.evidence_education = ', '.join(education_list)
            rec.evidence_experience = ', '.join(experience_list)
            rec.evidence_training = ', '.join(training_list)

class AssesmentCompetencyQMS(models.Model):
    _name           = 'itsec.line_assesment_qms'
    _description    = 'Assesment Kompetensi QMS'

    assesment_qms_id = fields.Many2one(
        'itsec.comp_values', ondelete='cascade'
    )
    nomor                   = fields.Char(string="No")
    requirement             = fields.Text(string="Requirement")
    standard                = fields.Text(string="Standard")
    evaluator_comment       = fields.Char(string="Evaluator Comment")
    ass_method              = fields.Char(string="Assesment Method")
    line_evidence_ids       = fields.One2many('itsec.line_evidence','reference_id')
    evidence_education = fields.Text(string="Evidence - Education",)
    evidence_experience = fields.Text(string="Evidence - Experience",)
    evidence_training = fields.Text(string="Evidence - Training",)

class AssmentEvidence(models.Model):
    _name           = 'itsec.line_evidence'
    _description    = 'Lines Assesment Evidence'

    evidence_ids    = fields.Many2one('itsec.line_assesment_general', ondelete='cascade')
    reference_id    = fields.Many2one('itsec.line_assesment_qms', ondelete='cascade')
    reference_id1    = fields.Many2one('itsec.scope_assesment', ondelete='cascade')
    education       = fields.Text(string="Education")
    experience      = fields.Text(string="Experience")
    training        = fields.Text(string="Training")

class qms_extra(models.Model):
    _name           = 'itsec.qms_extra'
    _description    = 'Extra Info'

    standard_ids     = fields.Many2many('standard.employee', string='Standards')
    ea_code_ids      = fields.Many2many('ea_code.employee', string='EA Code')
    auditor         = fields.Boolean(string='Auditor')
    lead_auditor    = fields.Boolean(string='Lead Auditor')
    pk              = fields.Boolean(string='PK')
    keterangan      = fields.Char(string="Keterangan")
    description     = fields.Char(string="description")
    periode         = fields.Char(string="periode")
    name            = fields.Char(string="name")
    compval         = fields.Many2one('itsec.comp_values', ondelete='cascade')
    qms_extra_id1   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id2   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id7   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id9   = fields.Many2one('itsec.kompetensi', ondelete='cascade')
    qms_extra_id3   = fields.Many2one('hr.employee', ondelete='cascade')
    qms_extra_id4   = fields.Many2one('hr.employee', ondelete='cascade')
    qms_extra_id5   = fields.Many2one('hr.employee', ondelete='cascade')
    qms_extra_id6   = fields.Many2one('hr.employee', ondelete='cascade')
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
        ('ABMS', 'ABMS'),
        ('HACCP', 'HACCP'),
        ('FSMS', 'FSMS'),
    ], string='Type Schema', store=True)
    
# HR Employee
class itsec_employee(models.Model):
    _inherit        = 'hr.employee'
    _description    = 'Personnel'
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')
    file_bin1       = fields.Binary('NDA')
    file_name1      = fields.Char('Filename NDA')
    file_bin2       = fields.Binary('Background Checking')
    file_name2      = fields.Char('Filename Background')
    file_bin3       = fields.Binary('Exit Clearance')
    file_name3      = fields.Char('Filename Clearance')
    file_bin4       = fields.Binary('Access Privilege')
    file_name4      = fields.Char('Filename Provilege')
    file_bin5       = fields.Binary('Certificate')
    file_name5      = fields.Char('Filename Certificate')
    training_ids    = fields.One2many('itsec.qms_extra', 'qms_extra_id3')
    experience_ids  = fields.One2many('itsec.qms_extra', 'qms_extra_id4')
    education_ids   = fields.One2many('itsec.qms_extra', 'qms_extra_id5')
    skill_ids       = fields.One2many('itsec.qms_extra', 'qms_extra_id6')
    audit_exp_ids   = fields.One2many('itsec.emp_audit', 'emp_audit_id')
    ass_scope_ids   = fields.One2many('itsec.assesment_scope', 'assesment_scope_id')
    ass_hr_ids      = fields.One2many('itsec.assesment_hr', 'assesment_hr_id')
    ass_competency_ids  = fields.One2many('itsec.assessment_competency', 'ass_competency_id')
    site_mandays_ids   = fields.One2many('itsec.site_mandays', 'site_mandays_id')
    auditor = fields.Selection([
                            ('Yes', 'Yes'),
                            ('No', 'No'),
                        ], string='Auditor', index=True, tracking=True,)
    
    def action_import_personal_information(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Data Wizard',
            'res_model': 'tsi.wizard.personal.information',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_employee_id': self.id
            }
        }

    # def action_import_audit_exp(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Import Audit Log',
    #         'res_model': 'tsi.wizard.audit.log',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'default_emp_audit_id': self.id}
    #     }
    
    # def action_import_auditor_skill(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Import Auditor Skill',
    #         'res_model': 'tsi.wizard.audit.skill',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {'default_qms_extra_id6': self.id}
    #     }

class emp_site_mandays(models.Model):
    _name           = 'itsec.site_mandays'
    _description    = 'Mandays Auditor'

    site_mandays_id     = fields.Many2one('hr.employee', ondelete='cascade')
    mandays             = fields.Char(string="Mandays")
    harga_mandays       = fields.Float(string="Harga Mandays")

class emp_audit(models.Model):
    _name           = 'itsec.emp_audit'
    _description    = 'Employee Audit'

    emp_audit_id    = fields.Many2one('hr.employee', ondelete='cascade')
    comp_name       = fields.Char(string="Client Name")
    standard        = fields.Char(string="standard")
    audit_date      = fields.Date(string="Audit Date")
    mandays         = fields.Char(string="Mandays")
    role            = fields.Char(string="role")
    audit_type      = fields.Char(string="Audit Type")
    ea_code         = fields.Many2many('ea_code.employee', string="Ea Code")
    audit_behalf    = fields.Char(string="Audit on Behalf")

class assesment_scope(models.Model):
    _name           = 'itsec.assesment_scope'
    _description    = 'Assesment Scoper'

    assesment_scope_id    = fields.Many2one('hr.employee', ondelete='cascade')
    nomor                 = fields.Char(string="Nomor")
    bisnis_sector         = fields.Char(string="Business Sector")
    standard              = fields.Char(string="Standard")
    evidence              = fields.Char(string="Evidence")
    ass_method            = fields.Char(string="Assesment Method")
    comment               = fields.Char(string="Evaluator Comment")

class ScopeAssement(models.Model):
    _name           = 'itsec.scope_assesment'
    _description    = 'Scope Assesment'

    ass_scope_qhse_id    = fields.Many2one('itsec.jobdesc', ondelete='cascade')
    ass_scope_food_id    = fields.Many2one('itsec.assesment_scope_food', ondelete='cascade')
    nomor                 = fields.Char(string="nomor")
    requirement           = fields.Text(string="REQUIREMENT")
    standard              = fields.Text(string="STANDARD")
    ass_method            = fields.Char(string="ASSESMENT METHOD")
    evaluator_comment     = fields.Char(string="EVALUATOR COMMENT")
    line_evidence_ids = fields.One2many('itsec.line_evidence', 'reference_id1')
    evidence_education = fields.Text(string="Evidence - Education", compute="_compute_evidence_fields")
    evidence_experience = fields.Text(string="Evidence - Experience", compute="_compute_evidence_fields")
    evidence_training = fields.Text(string="Evidence - Training", compute="_compute_evidence_fields")

    @api.depends('line_evidence_ids')
    def _compute_evidence_fields(self):
        for rec in self:
            education_list = [str(e) for e in rec.line_evidence_ids.mapped('education') if e]
            experience_list = [str(e) for e in rec.line_evidence_ids.mapped('experience') if e]
            training_list = [str(e) for e in rec.line_evidence_ids.mapped('training') if e]

            rec.evidence_education = ', '.join(education_list)
            rec.evidence_experience = ', '.join(experience_list)
            rec.evidence_training = ', '.join(training_list)

class assesment_hr(models.Model):
    _name           = 'itsec.assesment_hr'
    _description    = 'Assesment HR'

    assesment_hr_id       = fields.Many2one('hr.employee', ondelete='cascade')
    nomor                 = fields.Char(string="Nomor")
    requirement           = fields.Char(string="Requirement", related='standard.requirement')
    standard              = fields.Many2one('standard.employee', string="Standard")
    education             = fields.Char(string="Education", related='standard.education')
    experience            = fields.Char(string="Experience", related='standard.experience')
    training              = fields.Char(string="Training", related='standard.training')

class AssessmentCompetency(models.Model):
    _name           = 'itsec.assessment_competency'
    _description    = 'Assessment Competency'

    ass_competency_id     = fields.Many2one('hr.employee', ondelete='cascade')
    nomor                 = fields.Char(string="Nomor")
    requirement           = fields.Char(string="Requirement", related='standard.requirement')
    standard              = fields.Many2one('standard.employee', string="Standard")
    education             = fields.Char(string="Education", related='standard.education')
    experience            = fields.Char(string="Experience", related='standard.experience')
    training              = fields.Char(string="Training", related='standard.training')

class qms_jobdesc(models.Model):
    _name = 'itsec.jobdesc'
    _inherit        = 'mail.thread'
    _description    = 'Assesment Competency QHSE'
    _rec_name       = 'name'

    ass_scope_ids   = fields.One2many('itsec.scope_assesment', 'ass_scope_qhse_id')
    name            = fields.Char(string="Name of Candidate")
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    # Ini untuk Technical Scope
    conclusion = fields.Text(string="Conclusion")
    agriculture = fields.Boolean(string="01 Agriculture, forestry and fishing")
    mining = fields.Boolean(string="02 Mining & Quarrying")
    food_products = fields.Boolean(string="03 Food products, beverages and tobacco")
    textiles = fields.Boolean(string="04 Textiles and textile products")
    leather = fields.Boolean(string="05 Leather and leather products")
    wood = fields.Boolean(string="06 Wood and wood products")
    pulp_paper = fields.Boolean(string="07 Pulp, paper and paper products")
    publishing = fields.Boolean(string="08 Publishing companies")
    printing = fields.Boolean(string="09 Printing companies")
    petroleum = fields.Boolean(string="10 Manufacture of coke and refined petroleum products")
    nuclear_fuel_1 = fields.Boolean(string="11 Nuclear fuel")
    chemical = fields.Boolean(string="12 Chemical, Chemicals product and fibres")
    nuclear_fuel_2 = fields.Boolean(string="13 Nuclear fuel")
    rubber = fields.Boolean(string="14 Rubber and plastic products")
    non_metallic = fields.Boolean(string="15 Non-metallic mineral products")
    concrete = fields.Boolean(string="16 Concrete, cement, lime plaster, etc")
    basic_metal = fields.Boolean(string="17 Basic metal and fabricated metal products")
    machinery = fields.Boolean(string="18 Machinery and equipment")
    electrical_equipment = fields.Boolean(string="19 Electrical and optical equipment")
    shipbuilding = fields.Boolean(string="20 Shipbuilding")
    aerospace = fields.Boolean(string="21 Aerospace")
    other_transport = fields.Boolean(string="22 Other transport equipment")
    manufacturing_other = fields.Boolean(string="23 Manufacturing not elsewhere classified")
    recycling = fields.Boolean(string="24 Recycling")
    electricity_supply = fields.Boolean(string="25 Electricity supply")
    gas_supply = fields.Boolean(string="26 Gas supply")
    water_supply = fields.Boolean(string="27 Water supply")
    construction = fields.Boolean(string="28 Construction")
    wholesale_repair = fields.Boolean(string="29 Wholesale and retail trade; Repair of motor vehicles, motorcycles and personal and household goods")
    hotels_restaurants = fields.Boolean(string="30 Hotels and restaurants")
    transport_storage = fields.Boolean(string="31 Transport, storage and communication")
    financial_realestate = fields.Boolean(string="32 Financial intermediation; real estate; renting")
    information_tech = fields.Boolean(string="33 Information technology")
    engineering_services = fields.Boolean(string="34 Engineering services")
    other_services = fields.Boolean(string="35 Other services")
    public_admin = fields.Boolean(string="36 Public administration")
    education = fields.Boolean(string="37 Education")
    health_social = fields.Boolean(string="38 Health and social work")
    social_services = fields.Boolean(string="39 Other social services")

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action

class AssesnmentScopeFood(models.Model):
    _name = 'itsec.assesment_scope_food'
    _inherit        = 'mail.thread'
    _description    = 'Assesment Competency Scope Food'
    _rec_name       = 'name'

    ass_scope_food_ids   = fields.One2many('itsec.scope_assesment', 'ass_scope_food_id')
    name            = fields.Char(string="Name of Candidate")
    date_assesment  = fields.Date(string="Date of Assessment")
    job_position    = fields.Many2many('itsec.position', string="Position")
    doc_no          = fields.Char(string="Document Reference")
    authority       = fields.Text(string="Evaluator Name ")
    state = fields.Selection([
        ('New', 'New'),
        ('approval', 'Approval'),
    ], string='State', store=True, default="New")
    # Ini untuk Technical Scope
    conclusion = fields.Text(string="Conclusion")
    agriculture = fields.Boolean(string="01 Agriculture, forestry and fishing")
    mining = fields.Boolean(string="02 Mining & Quarrying")
    food_products = fields.Boolean(string="03 Food products, beverages and tobacco")
    textiles = fields.Boolean(string="04 Textiles and textile products")
    leather = fields.Boolean(string="05 Leather and leather products")
    wood = fields.Boolean(string="06 Wood and wood products")
    pulp_paper = fields.Boolean(string="07 Pulp, paper and paper products")
    publishing = fields.Boolean(string="08 Publishing companies")
    printing = fields.Boolean(string="09 Printing companies")
    petroleum = fields.Boolean(string="10 Manufacture of coke and refined petroleum products")
    nuclear_fuel_1 = fields.Boolean(string="11 Nuclear fuel")
    chemical = fields.Boolean(string="12 Chemical, Chemicals product and fibres")
    nuclear_fuel_2 = fields.Boolean(string="13 Nuclear fuel")
    rubber = fields.Boolean(string="14 Rubber and plastic products")
    non_metallic = fields.Boolean(string="15 Non-metallic mineral products")
    concrete = fields.Boolean(string="16 Concrete, cement, lime plaster, etc")
    basic_metal = fields.Boolean(string="17 Basic metal and fabricated metal products")
    machinery = fields.Boolean(string="18 Machinery and equipment")
    electrical_equipment = fields.Boolean(string="19 Electrical and optical equipment")
    shipbuilding = fields.Boolean(string="20 Shipbuilding")
    aerospace = fields.Boolean(string="21 Aerospace")
    other_transport = fields.Boolean(string="22 Other transport equipment")
    manufacturing_other = fields.Boolean(string="23 Manufacturing not elsewhere classified")
    recycling = fields.Boolean(string="24 Recycling")
    electricity_supply = fields.Boolean(string="25 Electricity supply")
    gas_supply = fields.Boolean(string="26 Gas supply")
    water_supply = fields.Boolean(string="27 Water supply")
    construction = fields.Boolean(string="28 Construction")
    wholesale_repair = fields.Boolean(string="29 Wholesale and retail trade; Repair of motor vehicles, motorcycles and personal and household goods")
    hotels_restaurants = fields.Boolean(string="30 Hotels and restaurants")
    transport_storage = fields.Boolean(string="31 Transport, storage and communication")
    financial_realestate = fields.Boolean(string="32 Financial intermediation; real estate; renting")
    information_tech = fields.Boolean(string="33 Information technology")
    engineering_services = fields.Boolean(string="34 Engineering services")
    other_services = fields.Boolean(string="35 Other services")
    public_admin = fields.Boolean(string="36 Public administration")
    education = fields.Boolean(string="37 Education")
    health_social = fields.Boolean(string="38 Health and social work")
    social_services = fields.Boolean(string="39 Other social services")

    def set_to_running(self):
        self.write({'state': 'approval'})
        return action


# Worker Representative
class qms_worker_rep(models.Model):
    _name = 'itsec.qms_worker_rep'
    _inherit        = 'mail.thread'
    _description    = 'Worker Representative'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    name            = fields.Char(string="name")
    pic             = fields.Char(string="pic")
    address         = fields.Text(string="address")
    phone           = fields.Char(string="phone")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Worker Representative Contract
class qms_worker_rep_contract(models.Model):
    _name = 'itsec.qms_worker_rep_contract'
    _inherit        = 'mail.thread'
    _description    = 'Worker Representative Contract'
    _rec_name       = 'nomor'
    nomor           = fields.Char(required=True)
    worker_rep      = fields.Many2one('itsec.qms_worker_rep', ondelete='cascade', string="Representative", required=True)
    contract_title  = fields.Char(string="contract_title")
    contract_date   = fields.Date(default=datetime.today())
    expired_date    = fields.Date(default=datetime.today())
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

# Worker Representative Meeting
class qms_worker_rep_meet(models.Model):
    _name = 'itsec.qms_worker_rep_meet'
    _inherit        = 'mail.thread'
    _description    = 'Worker Representative Meeting'
    name            = fields.Char(required=True)
    worker_rep      = fields.Many2one('itsec.qms_worker_rep', ondelete='cascade', string="Representative", required=True)
    tanggal         = fields.Date(default=datetime.today())
    description     = fields.Text(string="description")
    file_bin        = fields.Binary('Attachment')
    file_name       = fields.Char('Filename')

class ISOStandardEmployee(models.Model):
    _name           = 'standard.employee'
    # _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description    = 'Standard Employee'

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)
    standard        = fields.Selection([
                            ('iso',  'ISO'),
                            ('ispo',  'ISPO'),
                        ], string='Standard', index=True, tracking=True)
    requirement           = fields.Char(string="Requirement")
    education             = fields.Char(string="Education")
    experience            = fields.Char(string="Experience")
    training              = fields.Char(string="Training")

class EACodeEmployee(models.Model):
    _name           = 'ea_code.employee'
    _description    = 'EA Code Employee'
    # _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)
    iso_standard_ids = fields.Many2many('standard.employee', string='Standards', tracking=True)

class FoodCategoryEmployee(models.Model):
    _name           = 'food_category.employee'
    _description    = 'Food Category Employee'
    # _inherit        = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name            = fields.Char(string='Nama', tracking=True)
    description     = fields.Char(string='Description', tracking=True)
    iso_standard_ids = fields.Many2many('standard.employee', string='Standards', tracking=True)

class JobPosition(models.Model):
    _name           = 'itsec.position'
    _description    = 'JOb Position'

    name               = fields.Char(string="Name")
    description        = fields.Char(string="Description")

class StandardKompetensi(models.Model):
    _name           = 'itsec.standard.kompetensi'
    _description    = 'Standard Kompetensi'
    _rec_name       = 'type_schema'
    _order          = 'id DESC'

    type_schema = fields.Selection([
        ('qms', 'QMS'),
        ('eoms', 'EOMS'),
        ('ems', 'EMS'),
        ('isms', 'ISMS'),
        ('oh&s_ms', 'OH&S MS'),
        ('ABMS', 'ABMS'),
        ('HACCP', 'HACCP'),
        ('FSMS', 'FSMS'),
    ], string='Type Schema', store=True)
    # standard          = fields.Char(string="Education")
    # requierement      = fields.(string="Experience")
    line_standard_kompetensi = fields.One2many('itsec.line.standard.kompetensi', 'standard_kompetensi_id')

class LineStandardKompetensi(models.Model):
    _name           = 'itsec.line.standard.kompetensi'
    _description    = 'Line Standard Kompetensi'

    standard_kompetensi_id = fields.Many2one(
         'itsec.standard.kompetensi', ondelete='cascade'
    )
    no = fields.Char(string="No")
    standard          = fields.Text(string="Standard")
    requierement      = fields.Text(string="Requierement")