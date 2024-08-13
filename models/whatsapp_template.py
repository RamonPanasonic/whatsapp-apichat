
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class WhatsAppTemplate(models.Model):
    _inherit = 'whatsapp.template'

    is_open_message = fields.Boolean('Is Open Message', default=False)

    def button_submit_template(self):
        '''
        :override
        '''
        self.ensure_one()
        if self.wa_account_id:
            if self.wa_account_id.is_apichat():
                if self.button_ids:
                    raise ValidationError(_('Buttons are not allowed in apichat.'))
                self.status = 'approved'
            else:
                if self.is_open_message:
                    raise ValidationError(_('Only Apichat can be open message.'))
                super().button_submit_template()
        else:
            super().button_submit_template()

    @api.model
    def _find_default_for_account(self, model_name, wa_account_id):
        domain = [('wa_account_id', '=', wa_account_id.id)]
        domain.extend([
            ('model', '=', model_name),
            ('status', '=', 'approved'),
            '|',
            ('allowed_user_ids', '=', False),
            ('allowed_user_ids', 'in', self.env.user.ids)
        ])
        out = self.search(domain, limit=1)
        return out

    @api.constrains('is_open_message', 'wa_account_id')
    def _constrains_is_open_message(self):
        for record in self.filtered(lambda r: r.is_open_message):
            if not (record.wa_account_id and record.wa_account_id.is_apichat()):
                raise ValidationError(_('Only Apichat can be open message.'))
