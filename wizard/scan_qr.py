
from odoo import fields, models


class ApichatQr(models.TransientModel):
    _name = 'whatsapp.account.scan.qr'
    _description = 'Scan WhatsApp QR Code'

    qr_code_img = fields.Image('Qr code')
    account_id = fields.Many2one('whatsapp.account', string='Account', ondelete='cascade',
                                 required=True)
