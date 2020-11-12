// Copyright (c) 2016, FinByz and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Forex Exposure"] = {
	"filters": [
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Select",
			options: [
				{ "value": "USD", "label": __("USD") },
				{ "value": "EUR", "label": __("EUR") }
			]
		}
	]
}