# -*- coding: utf-8 -*-
# Copyright (c) 2021, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import  get_url_to_form

class SupplierItems(Document):
	
	def validate(self):
		if frappe.db.exists("Supplier Items",{'supplier':self.supplier,'item_code':self.item_code}):
			name = frappe.db.get_value("Supplier Items",{'supplier':self.supplier,'item_code':self.item_code})
			url = get_url_to_form("Supplier Items",name)
			frappe.throw(_("Record already exist. <br><b><a href='{url}'>{name}</a></b>.".format(url=url, name=name)))
