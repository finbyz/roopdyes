# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe.model.document import Document

class LabourAttendanceTool(Document):
	def get_labour_list(self):
		condition = ''

		if self.placed_by:
			condition += " and placed_by = '%s' " % self.placed_by

			if self.placed_by == "Contractor" and self.contractor:
				condition += "and supplier = '%s' " % self.contractor

		labour_list = frappe.db.sql("""
			select name, labour_name, placed_by
			from `tabLabour`
			where status != 'Left' {0} """.format(condition) ,as_dict=1)
		
		self.set("labour_list",[])
		
		for row in labour_list:
			self.append("labour_list",{
				"labour": row.name,
				"labour_name": row.labour_name,
				"placed_by": row.placed_by
			})

	def validate(self):
		if not self.get('labour_list'):
			self.get_labour_list()

	def on_submit(self):
		self.update_labour_attendance()

	def on_cancel(self):
		self.update_labour_attendance()

	def update_labour_attendance(self):
		for row in self.labour_list:
			labour = frappe.get_doc("Labour",row.labour)
			if row.present:
				if self._action == "submit":
					labour.total_working_days += 1
					labour.total_extra_hours += row.extra_hours
				elif self._action == 'cancel':
					labour.total_working_days -= 1
					labour.total_extra_hours -= row.extra_hours
			labour.save()
		else:
			frappe.db.commit()
