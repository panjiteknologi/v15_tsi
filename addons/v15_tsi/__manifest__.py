# -*- coding: utf-8 -*-
{
    'name': "TSI Certification",

    'summary': """
        ERP for TSI Certification""",

    'description': """
        Long description of module's purpose
    """,

    'author': "TSICertification",
    'website': "http://www.tsicertification.com",
    'version': '15.0.0.0',
    'category': 'Application',
    'sequence': 2,
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','contacts','hr','hr_attendance','website','sale','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/iso_security.xml',
        'views/ispo.xml',
        'views/crm_survey.xml',
        'views/iso_form.xml',
        'views/iso_review.xml',
        'views/ispo_review.xml',
        'views/ispo_form.xml',
        'views/iso_param.xml',
        'views/iso_risk.xml',
        'views/iso.xml',
        'views/crm.xml',
        'views/param.xml',
        'views/task_pd.xml',
        'views/task_project_plan.xml',
        'views/sistem_perundangan.xml',
        'views/document_control.xml',
        'views/ops_program.xml',
        'views/ops_program_ispo.xml',
        'views/ops_plan.xml',
        'views/ops_plan_ispo.xml',
        'views/ops_report.xml',
        'views/ops_report_ispo.xml',
        'views/ops_review.xml',
        'views/ops_review_ispo.xml',
        'views/ops_sertifikat.xml',
        'views/ops_sertifikat_ispo.xml',
        'views/sertifikat_delivery.xml',
        'views/audit_notification.xml',
        'views/audit_notification_ispo.xml',
        'views/audit_request.xml',
        'views/audit_request_ispo.xml',
        'views/audit_system.xml',
        'views/pengeluaran_barang.xml',
        'views/cron_job_sertifikat.xml',
        'views/cronjob_sla.xml',
        # 'views/cron_job_crm.xml',
        'wizards/wizard_quotation.xml',
        'wizards/wizard_quotation_app.xml',
        'wizards/wizard_quotation_app_ispo.xml',
        'wizards/wizard_quotation_ispo.xml',
        'wizards/account_move.xml',
        'wizards/wizard_audit.xml',
        'wizards/wizard_crm.xml',
        'wizards/wizard_audit_quotation.xml',
        'wizards/wizard_audit_request.xml',
        'views/history_kontrak.xml',
        'views/crm_chatbot.xml',
        'views/auditor_schedule.xml',
        'views/ows.xml',
        'views/pnl.xml',
        'views/views.xml',
        'views/temuan_kan.xml',
        'views/qc_pass.xml',
        'views/email_templates.xml'
    ],
    'assets': {
        'web.assets_backend': [
            # 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.min.js'
            '/v15_tsi/static/lib/chartjs-plugin-datalabels.min.js',
            '/v15_tsi/static/src/js/graph_renderer.js',
            # '/v15_tsi/static/src/js/pareto_chart.js',
            '/v15_tsi/static/src/js/graph_view.js',
            # '/v15_tsi/static/src/js/ParetoChart.js',
            # '/v15_tsi/static/src/js/chartjs-plugin-datalabels.min.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
