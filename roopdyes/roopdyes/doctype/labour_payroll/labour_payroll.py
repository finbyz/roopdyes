# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class LabourPayroll(Document):

	def get_advance(self):
		advance = frappe.db.sql("""
			select 
				labour, labour_name, date, advanced_payment, name
			from
				`tabLabour Advance Payment`
			where
				docstatus = 1 and status = "Unallocated" and labour = '%s'
		""" % self.labour,as_dict=1)
		
		self.set("labour_advance_detail",[])
		
		if advance:
			for row in advance:
				self.append("labour_advance_detail",{
					"advance_no": row.name,
					"labour": row.labour,
					"date": row.date,
					"labour_name": row.labour_name,
					"advance_payment": row.advanced_payment
				})
		else:
			frappe.msgprint("No Advance given")
			
	def on_submit(self):
		days,hours = frappe.db.get_value("Labour",self.labour,["total_working_days","total_extra_hours"])
		frappe.db.set_value("Labour",self.labour,"total_working_days",(days-self.working_days))
		frappe.db.set_value("Labour",self.labour,"total_extra_hours",(hours-self.extra_hours))
		
		for row in self.labour_advance_detail:
			frappe.db.set_value("Labour Advance Payment",row.advance_no,"status","Allocated")
		
	def on_cancel(self):
		days,hours = frappe.db.get_value("Labour",self.labour,["total_working_days","total_extra_hours"])
		frappe.db.set_value("Labour",self.labour,"total_working_days",(days+self.working_days))
		frappe.db.set_value("Labour",self.labour,"total_extra_hours",(hours+self.extra_hours))
		
		for row in self.labour_advance_detail:
			frappe.db.set_value("Labour Advance Payment",row.advance_no,"status","Unallocated")
			
			
