
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.whatsapp.tools.whatsapp_api import WhatsAppApi
from odoo.addons.whatsapp.tools.whatsapp_exception import WhatsAppError
from odoo.addons.phone_validation.tools import phone_validation


class WhatsAppAccount(models.Model):
    _inherit = 'whatsapp.account'

    account_type = fields.Selection([('meta', 'Meta'),
                                     ('apichat', 'Apichat')], string='Account Type',
                                    default='meta', required=True)
    phone_connected = fields.Char('Phone Connected', readonly=True)

    def is_apichat(self):
        return self.account_type == 'apichat'

    @api.onchange('account_uid', 'token')
    def _onchange_credentials(self):
        for account in self.filtered(lambda e: e.is_apichat()):
            account.phone_uid = account.account_uid
            account.app_uid = account.account_uid
            account.app_secret = account.token

    def _process_messages(self, value):
        '''
        :override
        '''
        super()._process_messages(value)
        Bus = self.env['bus.bus']
        for status in value.get('phone-statuses', []):
            if status.get('status') == 'connected':
                self.phone_connected = self.apichat_format_number(status.get('phone'))
            if status.get('qr'):
                status['qr'] = status['qr'].split(',')[1]
            Bus._sendone('whatsapp.account.scan.qr', 'phone_status', {
                'id': self.id,
                'status': status,
            })

    def button_test_connection(self):
        '''
        :override
        '''
        self.ensure_one()
        out = None
        if self.is_apichat():
            wa_api = WhatsAppApi(self)
            try:
                wa_api.setup_apichat_webhook()
                data: dict = wa_api._test_connection()
                self.phone_connected = False
                if data.get('is_connected'):
                    self.phone_connected = self.apichat_format_number(data['display_phone_number'])
                    out = self.env['acrux.apichat.pop.message'].message(_('All good!'), _('%s connected.') % self.phone_connected)
                elif data.get('qr'):
                    qr_code = data['qr'].split(',')[1]
                    cxt = self.env.context.copy()
                    cxt['default_qr_code_img'] = qr_code
                    cxt['default_account_id'] = self.id
                    out = {
                        'name': _('Scan WhatsApp QR Code'),
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_model': 'whatsapp.account.scan.qr',
                        'views': [[False, 'form']],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': cxt
                    }
                else:
                    raise WhatsAppError(data.get('reason', _('Can not connected, contact to apichat.')))
            except WhatsAppError as e:
                raise UserError(str(e))
        else:
            out = super().button_test_connection()
        return out

    def button_close_apichat_connection(self):
        self.ensure_one()
        wa_api = WhatsAppApi(self)
        try:
            wa_api.close_apichat_session()
            self.phone_connected = False
        except WhatsAppError as e:
            raise UserError(str(e))
        return self.env['acrux.apichat.pop.message'].message(_('Session Closed'),
                                                             _('Your Whatsapp session was closed.'))

    def apichat_format_number(self, phone):
        self.ensure_one()
        out = phone
        if phone:
            try:
                country_id = self.allowed_company_ids[0].country_id
                out = phone_validation.phone_format(phone, country_id.code, country_id.phone_code) or phone
            except Exception:
                out = phone
        return out

    def apichat_real_number(self, phone):
        self.ensure_one()
        if self.is_apichat() and phone:
            wa_number = phone.lstrip('+')
            if wa_number.startswith('52') and not wa_number.startswith('521'):
                phone = wa_number.replace('52', '521', 1)
        return phone
