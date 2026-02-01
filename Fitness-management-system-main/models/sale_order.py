# -*- coding: utf-8 -*-
from odoo import models,fields,_,api
from odoo.exceptions import ValidationError
import json
import io
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import base64


class SaleOrder(models.Model):
    _inherit= "sale.order"
    
    valid_customer = fields.Boolean(string="Valid Customer")

    def sale_report_writer(self):
              
        #initialization-----
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        #worksheet-- xlsx data-------------
        row=1
        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
           
        format_new = workbook.add_format({
            'bold': False,
            'align': 'left',
            'font_size':10,
            'font': 'Times New Roman',
            'border': False
        })
        
        col=1
        sheet = workbook.add_worksheet('Customers Report')
        sheet.write(row,col,'Customer Name',format_title )
        sheet.write(row,col+1,'Order date',format_title )
        sheet.write(row,col+2,'validity',format_title )
        
        row=row+1
        sheet.write(row,col,self.partner_id.name,format_new)
        sheet.write(row,col+1,self.date_order,format_new)
        sheet.write(row,col+2,self.validity_date,format_new)
        row = row + 5


        sheet.write(row-1,col,'Product',format_title )
        sheet.write(row-1,col+1,'Quantity',format_title )
        sheet.write(row-1,col+2,'Units',format_title )
        sheet.write(row-1,col+3,'Total',format_title )
        if(self.order_line):
            for orders in self.order_line:
                sheet.write(row,col,orders.product_template_id.name,format_title)
                sheet.write(row,col+1,str(orders.product_uom_qty) + "Nos",format_title)
                sheet.write(row,col+2,str(orders.price_unit) + "$",format_title)
                sheet.write(row,col+3,str(orders.price_subtotal) + "$",format_title)

                # sheet.write(row,col+2,orders.quantity,format_title)
                # sheet.write(row,col+3,orders.unit_price,format_title)
                # sheet.write(row,col+4,orders.sub_total,format_title)
                row=row+1

        sheet.write(row+3,col+1,'Sub Total',format_title )
        total = 0
        if (self.order_line):
            total= 0
            for order in self.order_line:
                total = total + order.price_subtotal

        sheet.write(row+3,col+2,total,format_title )


        #worksheet-- xlsx data---------closed------
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        report_id = self.env['common.xlsx.out'].sudo().create({'filedata': result, 'filename': 'customers.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=common.xlsx.out&field=filedata&id=%s&filename=%s.xls' % (
                report_id.id, self.name),
            'target': 'new',
        }
        output.close()

    def test_button(self):
        pass

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder,self)._prepare_invoice()
        invoice_vals['amount'] = self.amount_total   
        return invoice_vals



    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder,self)._prepare_invoice()
        return invoice_vals
    

    