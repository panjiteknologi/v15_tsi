{
    'name': 'Odoo Meta WhatsApp Discuss | Odoo Whatsapp Bidirectional Integration',
    'version': '15.0.0',
    'author': 'TechUltra Solutions Private Limited',
    'category': 'Discuss',
    'live_test_url': 'https://www.techultrasolutions.com/blog/news-2/odoo-whatsapp-integration-a-boon-for-business-communication-25',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'price': 89,
    'currency': 'USD',
    'summary': 'whatsapp discuss , Whatsapp bi-directional chat is the whatsapp chat room where user can interact to the customer and bi-directional chat can be done via this module',
    'description': """
        whatsapp chatroom is the functionality where user can use the discuss features of the odoo base to extend that to use the whatsapp communication between the user and customer
    """,
    'depends': ['tus_meta_whatsapp_base'],
    'data': [
        'data/cron.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'mail.assets_discuss_public': [
            'tus_meta_wa_discuss/static/src/js/components/*/*.js',
            'tus_meta_wa_discuss/static/src/js/models/*/*.js',
            'tus_meta_wa_discuss/static/src/css/thread_view_nav.css',
        ],
        'web.assets_backend': [
            'tus_meta_wa_discuss/static/src/js/components/*/*.js',
            'tus_meta_wa_discuss/static/src/js/models/*/*.js',
            'tus_meta_wa_discuss/static/src/js/AgentsList.js',
            'tus_meta_wa_discuss/static/src/js/MessagesList.js',
            
            # custom
            'tus_meta_wa_discuss/static/src/js/ButtonFormMessage.js',
            
            'tus_meta_wa_discuss/static/src/js/wa_thread_view.js',
            'tus_meta_wa_discuss/static/src/js/action_dialog.js',
            'tus_meta_wa_discuss/static/src/css/thread_view_nav.css',
            'tus_meta_wa_discuss/static/src/css/discuss.css',
            'tus_meta_wa_discuss/static/src/css/changes.css',
            'https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js',
            'https://cdn.datatables.net/1.10.24/css/jquery.dataTables.min.css',
        ],
        'web.assets_qweb': [
            'tus_meta_wa_discuss/static/src/xml/thread_view_nav.xml',
            'tus_meta_wa_discuss/static/src/xml/thread_view.xml',
            'tus_meta_wa_discuss/static/src/xml/chat_view_nav.xml',
            'tus_meta_wa_discuss/static/src/xml/chatter_topbar.xml',
            'tus_meta_wa_discuss/static/src/xml/thread_view_topbar.xml',
            'tus_meta_wa_discuss/static/src/xml/chat_window_header.xml',
            'tus_meta_wa_discuss/static/src/xml/message_list.xml',
            'tus_meta_wa_discuss/static/src/xml/composer.xml',
            'tus_meta_wa_discuss/static/src/xml/message.xml',

            'tus_meta_wa_discuss/static/src/xml/wa_thread_view.xml',
            'tus_meta_wa_discuss/static/src/xml/discuss.xml',
            'tus_meta_wa_discuss/static/src/xml/AgentsList.xml',
            'tus_meta_wa_discuss/static/src/xml/MessagesList.xml',
            
            # custom
            'tus_meta_wa_discuss/static/src/xml/ButtonFormMessage.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images':['static/description/main_screen.gif'],
}

