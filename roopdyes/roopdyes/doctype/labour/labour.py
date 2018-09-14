# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class Labour(Document):
	pass

@frappe.whitelist()
def make_labour_payroll(source_name, target_doc=None):
	doclist = get_mapped_doc("Labour", source_name, {
			"Labour":{
				"doctype": "Labour Payroll",
				"field_map": {
					"total_working_days": "working_days",
					"total_extra_hours": "extra_hours"
				},
				"field_no_map": [
					"naming_series"
				]
			}
		}, target_doc)

	return doclist
	
@frappe.whitelist()
def make_labour_advance(source_name, target_doc=None):
	doclist = get_mapped_doc("Labour", source_name, {
			"Labour":{
				"doctype": "Labour Advance Payment",
				
				"field_no_map": [
					"naming_series",
					"status"
				]
			}
		}, target_doc)

	return doclist