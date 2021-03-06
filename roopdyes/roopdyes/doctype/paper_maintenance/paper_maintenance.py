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

	def update_paper(source, target, source_parent):
		source.renewed = 1
		source.save()
		#frappe.db.commit()
		
	doclist = get_mapped_doc("Paper Maintenance", source_name, {
			"Paper Maintenance":{
				"doctype": "Paper Maintenance",	
				"field_no_map": [
					"document_expiry_date"
				],
				'postprocess':update_paper
			}
		}, target_doc)

	return doclist