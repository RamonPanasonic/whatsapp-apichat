# -*- coding: utf-8 -*-
# =====================================================================================
# License: OPL-1 (Odoo Proprietary License v1.0)
#
# By using or downloading this module, you agree not to make modifications that
# affect sending messages through apichat.io or avoiding contract a Plan with apichat.io.
# Support our work and allow us to keep improving this module and the service!
#
# Al utilizar o descargar este módulo, usted se compromete a no realizar modificaciones que
# afecten el envío de mensajes a través de apichat.io o a evitar contratar un Plan con apichat.io.
# Apoya nuestro trabajo y permite que sigamos mejorando este módulo y el servicio!
# =====================================================================================
{
    'name': 'Scan QR WhatsApp Enterprise - Odoo Apichat.io Integration',
    'summary': 'Connect WhatsApp Odoo Enterprise direct to apichat.io. Scan QR code and go. Independent of Chatroom.',
    'description': 'Connect WhatsApp Odoo Enterprise direct to apichat.io. Scan QR code and go. Independent of '
                   'Chatroom.',
    'version': '17.0.2.0',
    'author': 'AcruxLab',
    'support': 'info@acruxlab.com',
    'price': 99.2,
    'currency': 'USD',
    'images': ['static/description/apichat_Banner_base_v2.gif'],
    'website': 'https://acruxlab.com/whatsapp',
    'license': 'OPL-1',
    'application': True,
    'installable': True,
    'category': 'Productivity/Discuss',
    'depends': [
        'whatsapp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_template_data.xml',
        'wizard/custom_message_views.xml',
        'views/whatsapp_account_views.xml',
        'views/whatsapp_template_views.xml',
        'wizard/scan_qr_views.xml',
        'wizard/whatsapp_composer_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'whatsapp_apichat/static/src/jslib/chatroom.js',
        ],
    },
    'post_load': '',
    'external_dependencies': {},

}
