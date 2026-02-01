from odoo import models,fields
from _datetime import datetime

class CommonXlsxOut(models.TransientModel):
    _name="common.xlsx.out"

    filedata=fields.Binary('Download file', readonly=True)
    filename=fields.Char('Filename ', size=64, readonly=True)
    