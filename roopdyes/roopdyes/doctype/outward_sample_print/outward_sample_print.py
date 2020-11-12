# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class OutwardSamplePrint(Document):
	def get_samples(self):
		where_clause = ''
		where_clause += self.date and " and date = '%s' " % self.date or ''
		where_clause += self.product_name and " and product_name = '%s' " %\
		 self.product_name.replace("'","\'") or ''
		where_clause += self.party and " and party = '%s' " %\
		 self.party.replace("'","\'") or ''
		where_clause += self.destination and " and destination = '%s' " %\
		 self.destination.replace("'","\'") or ''
		
		data = frappe.db.sql("""
			SELECT
				name
			FROM
				`tabOutward Sample`
			WHERE
				docstatus < 2
				%s """%where_clause, as_dict=1)

		self.set("items", [])
		if data:
			for row in data:
				self.append("items",{
						'outward_sample': row['name']
					})