
import logging
from odoo import models, api
from odoo.addons.whatsapp.tools.whatsapp_api import WhatsAppApi

_logger = logging.getLogger(__name__)


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    @api.depends('message_ids')
    def _compute_whatsapp_channel_valid_until(self):
        '''
        :override
        '''
        wa_channels = self.filtered(lambda c: c.channel_type == 'whatsapp' and
                                    c.wa_account_id and
                                    c.wa_account_id.is_apichat())
        wa_channels.whatsapp_channel_valid_until = False
        return super(DiscussChannel, self - wa_channels)._compute_whatsapp_channel_valid_until()

    @api.model_create_multi
    def create(self, vals_list):
        '''
        :override
        '''
        self.add_profile_picture_and_name(vals_list)
        return super().create(vals_list)

    def _channel_info(self):
        '''
        :override
        '''
        channel_infos = super()._channel_info()
        channel_infos_dict = {c['id']: c for c in channel_infos}

        for channel in self:
            if channel.channel_type == 'whatsapp' and channel.wa_account_id:
                channel_infos_dict[channel.id]['account_type'] = channel.wa_account_id.account_type
        return list(channel_infos_dict.values())

    @api.model
    def add_profile_picture_and_name(self, vals_list):
        WhatsappAccount = self.env['whatsapp.account']
        Partner = self.env['res.partner']
        for vals in filter(lambda val: val.get('wa_account_id') and val.get('whatsapp_number'), vals_list):
            account = WhatsappAccount.browse(vals.get('wa_account_id'))
            if account.is_apichat():
                wa_api = WhatsAppApi(account)
                try:
                    chat_data = wa_api.get_chat(vals['whatsapp_number'])
                    if vals.get('name') and chat_data.get('name'):
                        vals['name'] = vals['name'].strip()
                        if vals['name'] == vals['whatsapp_number'] and {chat_data["name"]}:
                            vals['name'] = f'{chat_data["name"]} ({vals["name"]})'
                    if chat_data.get('image'):
                        vals['image_128'] = wa_api.get_profile_picture(chat_data['image'])
                        if vals.get('whatsapp_partner_id'):
                            partner = Partner.browse(vals['whatsapp_partner_id'])
                            if not partner.image_1920:
                                partner.write({'image_1920': vals['image_128']})
                except Exception as e:
                    _logger.error(e)
