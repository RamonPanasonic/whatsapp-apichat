
import mimetypes
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class WhatsAppComposer(models.TransientModel):
    _inherit = 'whatsapp.composer'

    @api.model
    def default_get(self, fields):
        '''
        :override
        '''
        result = super().default_get(fields)
        if result['wa_template_id']:
            WhatsAppTemplate = self.env['whatsapp.template']
            result['wa_account_id'] = WhatsAppTemplate.browse(result['wa_template_id']).wa_account_id.id
        return result

    wa_account_id = fields.Many2one('whatsapp.account', string='Account')
    is_open_message = fields.Boolean(related='wa_template_id.is_open_message')
    open_message_text = fields.Text('Message')
    binary_attachment = fields.Binary('Attachment File')
    binary_filename = fields.Char('Attachment Filename')

    @api.onchange('wa_account_id')
    def _onchage_wa_account_id(self):
        self.ensure_one()
        out = {'domain': {'wa_template_id': []}}
        if self.wa_account_id:
            template = self.env['whatsapp.template']._find_default_for_account(self.res_model, self.wa_account_id)
            if not template:
                raise ValidationError(_('No template available for this model and account'))
            self.wa_template_id = template.id
            out = {'domain': {'wa_template_id': [('wa_account_id', '=', self.wa_account_id.id)]}}
        return out

    @api.onchange('binary_filename')
    def _onchange_binary_filename(self):
        self.ensure_one()
        if self.binary_filename:
            mimetype, _guessed_ext = mimetypes.guess_type(self.binary_filename)
            if mimetype.startswith('audio'):
                self.open_message_text = False

    def _send_whatsapp_template(self, force_send_by_cron=False):
        '''
        :override
        '''
        for record in self.filtered(lambda r: r.is_open_message and not (r.open_message_text or r.binary_filename)):
            if not (record.wa_template_id.header_attachment_ids or record.wa_template_id.report_id):
                raise ValidationError(_('Message is empty.'))
        IrAttachment = self.env['ir.attachment'].sudo()
        for record in self.filtered(lambda r: r.is_open_message and r.binary_filename):
            mimetype, _guessed_ext = mimetypes.guess_type(record.binary_filename)
            if record.open_message_text and mimetype.startswith('audio'):
                raise ValidationError(_('Audio message cannot have text.'))
            vals = {
                'name': record.binary_filename,
                'datas': record.binary_attachment,
                'mimetype': mimetype,
                'res_model': record._name,
                'res_id': record.id,
            }
            record.attachment_id = IrAttachment.create(vals).id
        return super()._send_whatsapp_template(force_send_by_cron)

    def _get_free_text_fields(self):
        '''
        :override
        '''
        return super()._get_free_text_fields() + ['open_message_text']

    def _get_html_preview_whatsapp(self, rec):
        '''
        :override
        '''
        out = None
        if self.is_open_message:
            out = self.open_message_text
        else:
            out = super()._get_html_preview_whatsapp(rec)
        return out
