from odoo import models, api, fields

class DashboardData(models.AbstractModel):
    _name = 'user.performance.dashboard'
    _description = 'User Performance Dashboard Data'

    @api.model
    def get_dashboard_data(self, start_date=None, end_date=None, target_user_id=None):
        user = self.env['res.users'].browse(target_user_id) if target_user_id else self.env.user
        uid = user.id
        
        # Domain for metrics (based on dates and user)
        # Assuming customers are linked via user_id
        # Assuming incentives are payments linked via user_id on partner
        
        customer_count = self.env['res.partner'].search_count([('user_id', '=', uid)])
        
        # Incentives (Payments) logic
        payment_domain = [('state', '=', 'paid'), ('partner_id.user_id', '=', uid)]
        if start_date:
            payment_domain.append(('date', '>=', start_date))
        if end_date:
            payment_domain.append(('date', '<=', end_date))

        payments = self.env['account.payment'].search(payment_domain)
        payments_posted_count = len(payments)
        payments_posted_amount = sum(payments.mapped('amount'))

        # Build user list for filter (e.g., all internal users)
        all_users = self.env['res.users'].search_read([('share', '=', False)], ['id', 'name'])

        # Quotations (sale.order in quotation states)
        quotation_domain = [('partner_id.user_id', '=', uid), ('state', 'in', ['draft', 'sent'])]
        if start_date:
            quotation_domain.append(('date_order', '>=', start_date))
        if end_date:
            quotation_domain.append(('date_order', '<=', end_date))
        quotations = self.env['sale.order'].search(quotation_domain)
        quotations_count = len(quotations)
        quotations_amount = sum(quotations.mapped('amount_total'))

        # Sale Orders (confirmed)
        so_domain = [('partner_id.user_id', '=', uid), ('state', '=', 'sale')]
        if start_date:
            so_domain.append(('date_order', '>=', start_date))
        if end_date:
            so_domain.append(('date_order', '<=', end_date))
        sale_orders = self.env['sale.order'].search(so_domain)
        sale_orders_count = len(sale_orders)
        sale_orders_amount = sum(sale_orders.mapped('amount_total'))

        # Invoices (out_invoice)
        invoice_domain = [('move_type', '=', 'out_invoice'),('state', '=', 'posted'), ('partner_id.user_id', '=', uid)]
        if start_date:
            invoice_domain.append(('invoice_date', '>=', start_date))
        if end_date:
            invoice_domain.append(('invoice_date', '<=', end_date))
        invoices = self.env['account.move'].search(invoice_domain)


        invoices_unpaid = invoices.filtered(lambda m: m.payment_state != 'paid')
        invoices_paid = invoices.filtered(lambda m: m.payment_state == 'paid')
        invoices_unpaid_count = len(invoices_unpaid)
        invoices_unpaid_amount = sum(invoices_unpaid.mapped('amount_residual'))
        invoices_paid_count = len(invoices_paid)
        invoices_paid_amount = sum(invoices_paid.mapped('amount_total'))

        # Amount Due: sum of partners' payment_amount_due for partners assigned to the user
        partners = self.env['res.partner'].search([('user_id', '=', uid)])
        amount_due = sum(partners.mapped('payment_amount_due')) if partners else 0.0
        amount_due_count = sum(len(partner.unreconciled_aml_ids) for partner in partners)

        test = 0.00
        return {
            'name': user.name,
            'job_title': user.partner_id.function or 'No Job Title',
            'image_url': f'/web/image?model=res.users&id={user.id}&field=avatar_128', # Smaller for sidebar
            'customer_count': customer_count,
            'all_users': all_users,
            'current_user_id': user.id,
            'is_admin': self.env.user.id == 2,
            # Quotations
            'quotations_count': quotations_count,
            'quotations_amount': f"SAR {quotations_amount:,.2f}",
            # Sale Orders
            'sale_orders_count': sale_orders_count,
            'sale_orders_amount': f"SAR {sale_orders_amount:,.2f}",
            # Invoices unpaid / paid
            'invoices_unpaid_count': invoices_unpaid_count,
            'invoices_unpaid_amount': f"SAR {invoices_unpaid_amount:,.2f}",
            'invoices_paid_count': invoices_paid_count,
            'invoices_paid_amount': f"SAR {invoices_paid_amount:,.2f}",
            # Payments posted
            'payments_posted_count': payments_posted_count,
            'payments_posted_amount': f"SAR {payments_posted_amount:,.2f}",
            # Amount due (sum of partners' payment_amount_due)
            'amount_due': f"SAR {amount_due:,.2f}",
            'amount_due_count': amount_due_count,
            # Backwards compatibility
            'payment_amount': f"SAR {test:,.2f}",
        }
