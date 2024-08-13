
import logging
import json
import time
import base64
from odoo import _
from odoo.addons.whatsapp.tools.whatsapp_api import WhatsAppApi
from odoo.addons.whatsapp.tools.whatsapp_exception import WhatsAppError

_logger = logging.getLogger(__name__)

DEFAULT_HOSTNAME = 'https://api.apichat.io'


def monkey_patch(BaseClass):
    def decorate(func):
        fn_name: str = func.__name__
        private_fn_name: str = func.__name__
        if fn_name.startswith('__'):
            private_fn_name = f'_{BaseClass.__name__}{fn_name}'
        setattr(func, 'super', getattr(BaseClass, private_fn_name, None))
        setattr(BaseClass, private_fn_name, func)
        if private_fn_name != fn_name:
            setattr(BaseClass, fn_name, func)
        return func
    return decorate


@monkey_patch(WhatsAppApi)
def __api_requests(self, request_type, url, **kwargs):
    if not kwargs.get('endpoint_include'):
        kwargs['endpoint_include'] = True
        url = f'{DEFAULT_HOSTNAME}/graph/v17{url}'
    # _logger.info(f'\n{request_type} {url}')
    return __api_requests.super(self, request_type, url, **kwargs)


@monkey_patch(WhatsAppApi)
def _test_connection(self):
    out = None
    if self.wa_account_id.is_apichat():
        response = self.__api_requests('GET', f'/{self.wa_account_id.account_uid}/phone_numbers', auth_type='bearer')
        data = response.json().get('data', [])
        phone_values = [phone['id'] for phone in data if 'id' in phone]
        if self.wa_account_id.phone_uid not in phone_values:
            raise WhatsAppError(_('Phone number Id is wrong.'), 'account')
        out = data[0]
    else:
        out = _test_connection.super(self)
    return out


@monkey_patch(WhatsAppApi)
def setup_apichat_webhook(self):
    data = {
        'notify_ack': True,
        'notify_chat_update': False,
        'notify_format': None,
        'notify_phone_status': True,
        'webhook': self.wa_account_id.callback_url,
        'is_apigraph': True,
        'is_chatapi': False,
        'tz': self.wa_account_id.env.user.tz,
    }
    json_data = json.dumps(data)
    self.__api_requests(
        'PUT',
        f'/{self.wa_account_id.account_uid}/account',
        auth_type='bearer',
        data=json_data,
        headers={'Content-Type': 'application/json'},
    )


@monkey_patch(WhatsAppApi)
def close_apichat_session(self):
    self.__api_requests('POST', f'/{self.wa_account_id.account_uid}/logout', auth_type='bearer')


@monkey_patch(WhatsAppApi)
def _send_whatsapp(self, number, message_type, send_vals, parent_message_id=False):
    if self.wa_account_id.is_apichat() and self.wa_account_id.env.context.get('wait_before_send'):
        time.sleep(5)  # wait before send
    number = self.wa_account_id.apichat_real_number(number)
    return _send_whatsapp.super(self, number, message_type, send_vals, parent_message_id=parent_message_id)


@monkey_patch(WhatsAppApi)
def get_chat(self, number):
    number = self.wa_account_id.apichat_real_number(number)
    response = self.__api_requests(
        'GET',
        f'/{self.wa_account_id.account_uid}/chat',
        params={'number': number},
        auth_type='bearer'
    )
    return response.json()


@monkey_patch(WhatsAppApi)
def get_profile_picture(self, url):
    file_response = self.__api_requests('GET', url, endpoint_include=True)
    return base64.b64encode(file_response.content).decode('utf-8')
