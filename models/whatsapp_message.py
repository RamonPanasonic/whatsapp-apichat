
from odoo import fields, models, _
from odoo.addons.whatsapp.tools.whatsapp_exception import WhatsAppError


class WhatsAppMessage(models.Model):
    _inherit = 'whatsapp.message'

    state = fields.Selection(selection_add=[('played', 'Played'),
                                            ('deleted', 'Deleted')])

    def _is_apichat_template(self):
        return self.wa_account_id.is_apichat() and self.wa_template_id

    def copy_message_n_add_attachment(self, attachment):
        self.ensure_one()
        post_values = {
            'attachment_ids': [attachment.id] if attachment else [],
            'body': '',
            'message_type': 'whatsapp_message',
            'partner_ids': self.mail_message_id.partner_ids.ids,
        }
        message = self.env['mail.message'].create(dict(
            post_values,
            res_id=self.mail_message_id.res_id,
            model=self.mail_message_id.model,
            subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note')
        ))
        message_vals = [{
            'mail_message_id': message.id,
            'mobile_number': self.mobile_number,
            'free_text_json': '{}',
            'wa_template_id': False,
            'wa_account_id': self.wa_account_id.id,
        }]
        return self.create(message_vals)

    def _send_cron(self):
        '''
        :override
        '''
        self_ctx = self.with_context(executed_from_cron=True)
        super(WhatsAppMessage, self_ctx)._send_cron()

    def _send_message(self, with_commit=False):
        '''
        :override
        '''
        new_messages = self.env['whatsapp.message']
        apichat_message = self.filtered(lambda record: record._is_apichat_template())
        for attach_msg in apichat_message:
            if attach_msg.mail_message_id.model != attach_msg.wa_template_id.model:
                raise WhatsAppError(failure_type='template')
            first_message_used = False
            for attachment in attach_msg.wa_template_id.header_attachment_ids:
                if first_message_used:
                    new_messages |= self.copy_message_n_add_attachment(attachment)
                else:
                    attach_msg.mail_message_id.attachment_ids = [(6, 0, attachment.ids)]
                    first_message_used = True
            if attach_msg.wa_template_id.report_id:
                RecordModel = self.env[attach_msg.mail_message_id.model].with_user(attach_msg.create_uid)
                from_record = RecordModel.browse(attach_msg.mail_message_id.res_id)
                attachment = attach_msg.wa_template_id._generate_attachment_from_report(from_record)
                if first_message_used:
                    new_messages |= self.copy_message_n_add_attachment(attachment)
                else:
                    attach_msg.mail_message_id.attachment_ids = [(6, 0, attachment.ids)]
        apichat_message.write({'wa_template_id': False})
        all_messages = self + new_messages
        if self.env.context.get('executed_from_cron') and len(all_messages) > 10:
            all_messages = all_messages.with_context(wait_before_send=True)
        super(WhatsAppMessage, all_messages)._send_message(with_commit)
        apichat_message._post_template_apichat_message()

    def _post_template_apichat_message(self):
        for record in self:
            channel = record.wa_account_id._find_active_channel(record.mobile_number_formatted)
            if channel:
                vals = dict(message_type='notification',
                            body=record.body,
                            attachment_ids=record.mail_message_id.attachment_ids.ids,
                            subtype_xmlid='mail.mt_comment',)
                if not record.body:
                    if len(record.mail_message_id.attachment_ids) == 1:
                        mimetype = record.mail_message_id.attachment_ids[0].mimetype
                        if mimetype:
                            if mimetype.startswith('image'):
                                vals['body'] = _('Sent an image.')
                            elif mimetype.startswith('video'):
                                vals['body'] = _('Sent a video.')
                            elif mimetype.startswith('audio'):
                                vals['body'] = _('Sent an audio.')
                            else:
                                vals['body'] = _('Sent a document.')
                        else:
                            vals['body'] = _('Sent an attachment.')
                    else:
                        vals['body'] = _('Sent multiple attachments.')
                channel.sudo().message_post(**vals)
