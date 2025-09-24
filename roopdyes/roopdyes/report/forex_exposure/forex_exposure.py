# Copyright (c) 2013, FinByz and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe import _
from frappe.utils import (
	today,
	getdate,
	add_days,
	add_months,
	add_years,
	get_first_day,
	get_last_day,
	get_first_day_of_week,
	get_last_day_of_week,
	get_year_start,
	get_year_ending,
	get_quarter_start,
	get_quarter_ending,
)


def execute(filters=None):
	"""
	Generates a report with columns, data, and a chart based on the provided filters.
	"""
	filters = frappe.parse_json(filters)
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)
	return columns, data, None, chart


def get_columns():
	"""
	Defines the columns for the report.
	"""
	columns = [
		{
			"label": _("Document"),
			"fieldname": "document",
			"fieldtype": "Dynamic Link",
			"options": "document_type",
			"width": 120,
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 80,
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 140,
		},
		{
			"label": _("CCY"),
			"fieldname": "ccy",
			"fieldtype": "Link",
			"options": "Currency",
			"width": 80,
		},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Rate"),
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 80,
		},
		{
			"label": _("INR Amount"),
			"fieldname": "inr_amount",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 100,
		},
		{
			"label": _("Amount Hedged"),
			"fieldname": "amount_hedged",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Amount Unhedged"),
			"fieldname": "amount_unhedged",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Natural Hedged"),
			"fieldname": "natural_hedged",
			"fieldtype": "Currency",
			"options": "currency",
			"width": 120,
		},
		{
			"label": _("Due Date"),
			"fieldname": "delivery_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Document Type"),
			"fieldname": "document_type",
			"fieldtype": "Select",
			"options": ["Sales Order", "Sales Invoice"],
			"width": 80,
		},
	]
	return columns


def get_timespan_date_range(timespan, to_date=None):
	"""
	Calculates the date range based on a given timespan string.
	"""
	valid_timespans = [
		"Today", "Last Week", "Last Month", "Last Quarter", "Last 6 Months",
		"Last Year", "This Week", "This Month", "This Quarter", "This Year",
		"This Fiscal Year", "Next Week", "Next Month", "Next Quarter",
		"Next 6 Months", "Next Year",
	]

	if timespan not in valid_timespans:
		frappe.throw(_("Invalid timespan: {0}").format(timespan))

	if to_date is None:
		to_date = getdate(today())

	from_date = to_date

	if timespan == "Today":
		from_date = to_date
	elif timespan == "Last Week":
		from_date = get_first_day_of_week(add_days(to_date, -7))
		to_date = get_last_day_of_week(add_days(to_date, -7))
	elif timespan == "Last Month":
		from_date = get_first_day(add_months(to_date, -1))
		to_date = get_last_day(add_months(to_date, -1))
	elif timespan == "Last Quarter":
		from_date = get_quarter_start(add_months(to_date, -3))
		to_date = get_quarter_ending(add_months(to_date, -3))
	elif timespan == "Last 6 Months":
		from_date = get_first_day(add_months(to_date, -6))
		to_date = get_last_day(to_date)
	elif timespan == "Last Year":
		from_date = get_year_start(add_years(to_date, -1))
		to_date = get_year_ending(add_years(to_date, -1))
	elif timespan == "This Week":
		from_date = get_first_day_of_week(to_date)
		to_date = get_last_day_of_week(to_date)
	elif timespan == "This Month":
		from_date = get_first_day(to_date)
		to_date = get_last_day(to_date)
	elif timespan == "This Quarter":
		from_date = get_quarter_start(to_date)
		to_date = get_quarter_ending(to_date)
	elif timespan == "This Year":
		from_date = get_year_start(to_date)
		to_date = get_year_ending(to_date)
	elif timespan == "This Fiscal Year":
		fiscal_year = frappe.get_cached_value("Global Defaults", None, "current_fiscal_year")
		if not fiscal_year:
			frappe.throw(_("Current Fiscal Year is not set in Global Defaults"))
		fiscal_year_doc = frappe.get_cached_doc("Fiscal Year", fiscal_year)
		from_date = fiscal_year_doc.year_start_date
		to_date = fiscal_year_doc.year_end_date
	elif timespan == "Next Week":
		from_date = get_first_day_of_week(add_days(to_date, 7))
		to_date = get_last_day_of_week(add_days(to_date, 7))
	elif timespan == "Next Month":
		from_date = get_first_day(add_months(to_date, 1))
		to_date = get_last_day(add_months(to_date, 1))
	elif timespan == "Next Quarter":
		from_date = get_quarter_start(add_months(to_date, 3))
		to_date = get_quarter_ending(add_months(to_date, 3))
	elif timespan == "Next 6 Months":
		from_date = get_first_day(add_months(to_date, 1))
		to_date = get_last_day(add_months(to_date, 6))
	elif timespan == "Next Year":
		from_date = get_year_start(add_years(to_date, 1))
		to_date = get_year_ending(add_years(to_date, 1))

	return from_date, to_date


def get_data(filters):
	"""
	Fetches data for Sales Orders and Sales Invoices based on filters.
	"""
	if not filters.get("timespan"):
		frappe.throw(_("Timespan filter is required"))

	where_clause = ""
	where_params = []

	# Handle currency filter
	if filters.get("currency"):
		where_clause = " and currency = %s"
		where_params = [filters.currency]
	else:
		where_clause = " and currency != %s"
		where_params = ["INR"]

	# Handle timespan filter
	from_date, to_date = get_timespan_date_range(filters.timespan)
	timespan_so_condition = " and so.transaction_date between %s and %s"
	timespan_si_condition = " and si.posting_date between %s and %s"
	timespan_params = [from_date, to_date]

	# Query for Sales Order data
	so_data = frappe.db.sql(
		"""
		select
			so.name as "document",
			so.transaction_date as "date",
			so.customer as "customer",
			so.currency as "ccy",
			(so.grand_total - (so.advance_paid / so.conversion_rate)) as "total_amount",
			so.conversion_rate as "rate",
			so.base_grand_total as "inr_amount",
			so.amount_hedged as "amount_hedged",
			so.amount_unhedged as "amount_unhedged",
			so.natural_hedge as "natural_hedged",
			so.delivery_date as "delivery_date",
			so.status as "status",
			"Sales Order" as "document_type"
		from
			`tabSales Order` so
		where
			so.docstatus = 1
			and so.status not in ('Closed', 'Completed')
			and so.amount_hedged < so.grand_total
			{0} {1}
		order by so.delivery_date asc
	""".format(timespan_so_condition, where_clause),
		timespan_params + where_params,
		as_dict=True,
	)

	# Query for Sales Invoice data
	si_data = frappe.db.sql(
		"""
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
			{0} {1}
		order by si.due_date asc
	""".format(timespan_si_condition, where_clause),
		timespan_params + where_params,
		as_dict=True,
	)

	data = so_data + si_data
	return data


def get_chart_data(data):
	"""
	Prepares data for the chart visualization.
	"""
	total_amount = []
	total_hedged = []
	total_unhedged = []
	labels = []
	dates = []

	# Get unique month-year labels from delivery dates
	for row in data:
		date = getdate(row.delivery_date)
		month_year = date.strftime("%b-%Y")
		if month_year not in dates:
			dates.append(month_year)

	# Sort dates chronologically
	dates = sorted(dates, key=lambda x: datetime.datetime.strptime(x, "%b-%Y"))

	# Aggregate amounts by month
	for month in dates:
		amt = 0
		hedged = 0
		unhedged = 0
		for row in data:
			d = getdate(row.delivery_date)
			period = d.strftime("%b-%Y")
			if period == month:
				amt += row.total_amount
				hedged += row.amount_hedged
				unhedged += row.amount_unhedged

		total_amount.append(amt)
		total_hedged.append(hedged)
		total_unhedged.append(unhedged)
		labels.append(month)

	datasets = []
	if total_amount:
		datasets.append({"title": "Total Amount", "values": total_amount})
	if total_hedged:
		datasets.append({"title": "Total Hedged", "values": total_hedged})
	if total_unhedged:
		datasets.append({"title": "Total Unhedged", "values": total_unhedged})

	chart = {"data": {"labels": labels, "datasets": datasets}, "type": "bar"}

	return chart
