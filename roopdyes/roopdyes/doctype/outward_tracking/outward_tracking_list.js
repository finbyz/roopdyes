frappe.listview_settings['Outward Tracking'] = {
	add_fields: ["tracking_status"],
	get_indicator: function (doc) {
		return [__(doc.tracking_status), {
			"On the way": "orange",
			"Delivered": "green"
		}[doc.tracking_status], "tracking_status,=," + doc.tracking_status];
	}
};