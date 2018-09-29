# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class PaperMaintenance(Document):
	pass

@frappe.whitelist()
def make_renew_doc(source_name, target_doc=None):
	doclist = get_mapped_doc("Paper Maintenance", source_name, {
			"Paper Maintenance":{
				"doctype": "Paper Maintenance",
				# "field_map": {
					# "total_working_days": "working_days",
					# "total_extra_hours": "extra_hours"
				# },
				"field_no_map": [
					"document_expiry_date"
				]
			}
		}, target_doc)

	return doclist