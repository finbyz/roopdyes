# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import db,_
from frappe.model.document import Document

class InwardSample(Document):

	def onclick_update_price(self):

		if db.exists("Purchase Price" ,{ "product_name":self.item_code , "price_list":self.price_list}):
			purchase_price = frappe.get_doc("Purchase Price",{"product_name":self.item_code,"price_list":self.price_list})
			purchase_price.price = self.item_price
			purchase_price.purchase_price = self.price_list
			purchase_price.save()
			#purchase_price.run_method('on_update_after_submit')

		else:

			purchase_price = frappe.new_doc("Purchase Price")
			frappe.errprint("goes inside onclick_update_price")
			purchase_price.ref_no = self.outward_reference_1
			purchase_price.product_name = self.item_code
			purchase_price.supplier_ref_no = self.ref_no
			purchase_price.supplier_product_name = self.item_code
			purchase_price.date = self.date
			purchase_price.price = self.item_price
			purchase_price.price_list = self.price_list

			purchase_price.save()
			self.db_set('purchase_price' , purchase_price.name)
			purchase_price.submit()
		frappe.db.commit()
		frappe.msgprint(_("Purchase Price Updated"))