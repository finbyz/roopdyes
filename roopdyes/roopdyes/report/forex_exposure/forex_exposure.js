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
		},
		{
			"fieldname":"timespan",
			"label": __("Timespan"),
			"fieldtype": "Select",
			"width": "80",
			"default":"this fiscal year",
			"options":"\nlast week\nlast month\nlast quarter\nlast 6 months\nlast year\ntoday\nthis week\nthis month\nthis quarter\nthis year\nthis fiscal year\nnext week\nnext month\nnext quarter\nnext 6 months\nnext year"
		}
	]
}