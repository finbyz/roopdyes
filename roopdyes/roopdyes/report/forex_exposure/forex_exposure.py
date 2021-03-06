# Copyright (c) 2013, FinByz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe import _
from frappe.utils import getdate
from finbyz_dashboard.finbyz_dashboard.dashboard_overrides.data import get_timespan_date_range

def execute(filters=None):
	filters = frappe.parse_json(filters)
	columns, data = [], []
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart

def get_columns():
	columns = [
		{
			"label": _("Document"),
			"fieldname": "document",
			"fieldtype": "Dynamic Link",
			"options": "document_type",
			"width": 120
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 80
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140
		},
		{
			"label": _("CCY"),
			"fieldname": "ccy",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 80
		},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 80
		},
		{
			"label": _("INR Amount"),
			"fieldname": "inr_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100
		},
		{
			"label": _("Amount Hedged"),
			"fieldname": "amount_hedged",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"label": _("Amount Unhedged"),
			"fieldname": "amount_unhedged",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"label": _("Natural Hedged"),
			"fieldname": "natural_hedged",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120
		},
		{
			"label": _("Due Date"),
			"fieldname": "delivery_date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Document Type"),
			"fieldname": "document_type",
			"fieldtype": "Select",
			"options": ["Sales Order","Sales Invoice"],
			"width": 80
		},
	]
	return columns
	
def get_data(filters):
	timespan_so_condition = timespan_si_condition = ''
	if filters.get('timespan') and not filters.timespan == "":
		from_date, to_date = get_timespan_date_range(filters.timespan)
		timespan_so_condition = " and so.transaction_date between '{}' AND '{}'".format(from_date,to_date)
		timespan_si_condition = " and si.posting_date between '{}' AND '{}'".format(from_date,to_date)

	where_clause = ''
	where_clause += filters.currency and " and currency = '%s'" % \
		filters.currency.replace("'","\'") or " and currency != 'INR'"
	
	so_data = frappe.db.sql("""
		select 
			so.name as "document",
			so.transaction_date as "date",
			so.customer as "customer",
			so.currency as "ccy",
			(so.grand_total-(so.advance_paid/so.conversion_rate)) as "total_amount",
			so.conversion_rate as "rate",
			so.base_grand_total as "inr_amount",
			so.amount_hedged as "amount_hedged",
			so.amount_unhedged as "amount_unhedged",
			so.natural_hedge as "natural_hedged",
			so.delivery_date as "delivery_date",
			so.status as "status",
			"Sales Orer" as "document_type"
		from	
			`tabSales Order` so
		where
			so.docstatus = 1
			and so.status != 'Closed'
			and so.status != 'Completed'
			and so.amount_hedged < so.grand_total
			{} {}
		order by so.delivery_date asc""".format(timespan_so_condition,where_clause),as_dict=True)

	si_data = frappe.db.sql("""
		select 
			si.name as "document",
			si.posting_date as "date",
			si.customer as "customer",
			si.currency as "ccy",
			si.outstanding_amount as "total_amount",
			si.conversion_rate as "rate",
			(si.outstanding_amount * si.conversion_rate) as "inr_amount",
			si.amount_hedged as "amount_hedged",
			si.amount_unhedged as "amount_unhedged",
			si.natural_hedge as "natural_hedged",
			si.due_date as "delivery_date",
			si.status as "status",
			"Sales Invoice" as "document_type"
		from	
			`tabSales Invoice` si
		where
			si.docstatus = 1
			and si.status != 'Paid'
			and si.amount_hedged < si.grand_total
			{} {}
		order by si.due_date asc""".format(timespan_si_condition,where_clause),as_dict=True)

	data = so_data + si_data
	
	return data
		
def get_chart_data(data):
	
	total_amount, total_hedged, total_unhedged = [], [], []
	labels = []
	dates = []
	
	for row in data:
		date = getdate(row.delivery_date) # Delivery Date field
		if str(date.strftime("%b-%Y")) not in dates:
			dates.append(str(date.strftime("%b-%Y")))
	
	sorted(dates, key=lambda x: datetime.datetime.strptime(x, '%b-%Y'))
	
	for month in dates:
		amt = 0
		hedged = 0
		unhedged = 0
		for row in data:
			d = getdate(row.delivery_date) # Delivery Date field
			period = str(d.strftime("%b-%Y"))
			if period == month:
				amt += row.total_amount # Total Amount field
				hedged += row.amount_hedged # Amount Hedged field
				unhedged += row.amount_unhedged # Amount Unhedged field
				
		total_amount.append(amt)
		total_hedged.append(hedged)
		total_unhedged.append(unhedged)
		labels.append(month)
		
	datasets = []
	
	if total_amount:
		datasets.append({
			'title': "Total Amount",
			'values': total_amount
		})
	
	if total_hedged:
		datasets.append({
			'title': "Total Hedged",
			'values': total_hedged
		})
	
	if total_unhedged:
		datasets.append({
			'title': "Total Unhedged",
			'values': total_unhedged
		})
	
	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}
	chart["type"] = "bar"
	return chart