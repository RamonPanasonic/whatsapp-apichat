# -*- coding: utf-8 -*-
from odoo import models


class IrWebsocket(models.AbstractModel):
    _inherit = 'ir.websocket'

    def _build_bus_channel_list(self, channels):
        channels = list(channels)
        channels.append('whatsapp.account.scan.qr')
        return super()._build_bus_channel_list(channels)
