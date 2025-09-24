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
            fieldname: "timespan",
            label: __("Timespan"),
            fieldtype: "Select",
            width: "80",
            default: "This Fiscal Year",
            options: [
                { value: "Today", label: __("Today") },
                { value: "Last Week", label: __("Last Week") },
                { value: "Last Month", label: __("Last Month") },
                { value: "Last Quarter", label: __("Last Quarter") },
                { value: "Last 6 Months", label: __("Last 6 Months") },
                { value: "Last Year", label: __("Last Year") },
                { value: "This Week", label: __("This Week") },
                { value: "This Month", label: __("This Month") },
                { value: "This Quarter", label: __("This Quarter") },
                { value: "This Year", label: __("This Year") },
                { value: "This Fiscal Year", label: __("This Fiscal Year") },
                { value: "Next Week", label: __("Next Week") },
                { value: "Next Month", label: __("Next Month") },
                { value: "Next Quarter", label: __("Next Quarter") },
                { value: "Next 6 Months", label: __("Next 6 Months") },
                { value: "Next Year", label: __("Next Year") }
            ]
        }
	]
}
