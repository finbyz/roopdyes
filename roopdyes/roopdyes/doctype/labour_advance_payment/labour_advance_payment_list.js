// Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
// For license information, please see license.txt

frappe.listview_settings['Labour Advance Payment'] = {	
	add_fields: ["status"],		
	get_indicator: function (doc) {
		return [__(doc.status), {				
			"Allocated":"green",
			"Unallocated": "red"
		}[doc.status], "status,=," + doc.status];
	}
};