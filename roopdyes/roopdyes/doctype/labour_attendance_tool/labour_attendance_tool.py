# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import db,get_doc

class LabourAttendanceTool(Document):

	def get_labour_list(self):
		labour_list = db.sql("""
			select
				name, labour_name
			from	
				`tabLabour`
			where
				status != 'Left'
		""",as_dict=1)
		
		self.set("labour_list",[])
		
		for row in labour_list:
			self.append("labour_list",{
				"labour": row.name,
				"labour_name": row.labour_name
			})

	def before_submit(self):
		for row in self.labour_list:
			labour = get_doc("Labour",row.labour)
			if row.present == 1:		
				labour.total_working_days += 1
			labour.total_extra_hours += row.extra_hours
			labour.save()
			db.commit()
		
	def on_cancel(self):
		for row in self.labour_list:
			labour = get_doc("Labour",row.labour)
			labour.total_working_days -= 1
			labour.total_extra_hours -= row.extra_hours
			labour.save()
			db.commit()
			
			
			
			
			
		
	# def before_submit(self):
		# for row in self.labour_list:
			# labour = get_doc("Labour",row.labour)
			# for d in labour.daily_attendance:
				# frappe.errprint(d.date)
				# if str(d.date) == str(self.date):
					# frappe.throw("Record already exist for date %s"%self.date)
				
			# labour.append("daily_attendance",{
				# "date": self.date,
				# "present": row.present,
				# "extra_hours": row.extra_hours
			# })
			
			# labour.save()
			# db.commit()

