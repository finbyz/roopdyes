// Copyright (c) 2026, FinByz Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.query_reports["Trial Balance RoopDyes"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
		},
		{
			fieldname: "accounts",
			label: __("Accounts"),
			fieldtype: "Link",
			options: "Account",
			get_query: function () {
				return {
					filters: {
						company: frappe.query_report.get_filter_value("company"),
						is_group: 1
					}
				};
			}
		},
	],
	formatter: erpnext.financial_statements.formatter,
	tree: true,
	name_field: "account",
	parent_field: "parent_account",
	initial_depth: 3,
};

erpnext.utils.add_dimensions("Trial Balance", 6);
