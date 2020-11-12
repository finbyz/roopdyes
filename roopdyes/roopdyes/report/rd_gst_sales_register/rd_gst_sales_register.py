# Copyright (c) 2013, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from erpnext.accounts.report.sales_register.sales_register import _execute

# def execute(filters=None):
# 	return _execute(filters, additional_table_columns=[
# 		dict(fieldtype='Data', label='Invoice No', width=120),
# 		dict(fieldtype='Data', label='Customer GSTIN', width=120),
# 		dict(fieldtype='Data', label='Billing Address GSTIN', width=140),
# 		dict(fieldtype='Data', label='Company GSTIN', width=120),
# 		dict(fieldtype='Data', label='Place of Supply', width=120),
# 		dict(fieldtype='Data', label='Reverse Charge', width=120),
# 		dict(fieldtype='Data', label='Invoice Type', width=120),
# 		dict(fieldtype='Data', label='Export Type', width=120),
# 		dict(fieldtype='Data', label='E-Commerce GSTIN', width=130)
# 	], additional_query_columns=[
# 		'invoice_no',
# 		'customer_gstin',
# 		'billing_address_gstin',
# 		'company_gstin',
# 		'place_of_supply',
# 		'reverse_charge',
# 		'invoice_type',
# 		'export_type',
# 		'ecommerce_gstin'
# 	])


def execute(filters=None):
	return _execute(filters, additional_table_columns=[
		dict(fieldtype='Data', label='Invoice No', fieldname="invoice_no", width=120),
		dict(fieldtype='Data', label='Customer GSTIN', fieldname="customer_gstin", width=120),
		dict(fieldtype='Data', label='Billing Address GSTIN', fieldname="billing_address_gstin", width=140),
		dict(fieldtype='Data', label='Company GSTIN', fieldname="company_gstin", width=120),
		dict(fieldtype='Data', label='Place of Supply', fieldname="place_of_supply", width=120),
		dict(fieldtype='Data', label='Reverse Charge', fieldname="reverse_charge", width=120),
		dict(fieldtype='Data', label='Invoice Type', fieldname="invoice_type", width=120),
		dict(fieldtype='Data', label='Export Type', fieldname="export_type", width=120),
		dict(fieldtype='Data', label='E-Commerce GSTIN', fieldname="ecommerce_gstin", width=130)
	], additional_query_columns=[
		'invoice_no',
		'customer_gstin',
		'billing_address_gstin',
		'company_gstin',
		'place_of_supply',
		'reverse_charge',
		'invoice_type',
		'export_type',
		'ecommerce_gstin'
	])

