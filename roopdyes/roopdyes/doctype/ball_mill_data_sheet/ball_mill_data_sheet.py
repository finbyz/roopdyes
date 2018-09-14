# -*- coding: utf-8 -*-
# Copyright (c) 2018, FinByz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, erpnext
from frappe.model.document import Document
from frappe.utils import nowtime, flt
from erpnext.stock.utils import get_incoming_rate
from erpnext.stock.stock_ledger import get_valuation_rate
from frappe.model.mapper import get_mapped_doc

class BallMillDataSheet(Document):

	def validate(self):
		self.set_incoming_rate()

	def set_incoming_rate(self):
		for d in self.items:
			if d.source_warehouse:
				args = self.get_args_for_incoming_rate(d)
				d.basic_rate = get_incoming_rate(args)
			elif not d.source_warehouse:
				d.basic_rate = 0.0
			elif self.warehouse and not d.basic_rate:
				d.basic_rate = get_valuation_rate(d.item_code, self.warehouse,
					self.doctype, d.name, 1,
					currency=erpnext.get_company_currency(self.company))

			d.basic_amount = d.basic_rate * d.quantity

	def get_args_for_incoming_rate(self, item):
		warehouse = item.source_warehouse or self.warehouse
		return frappe._dict({
			"item_code": item.item_name,
			"warehouse": warehouse,
			"posting_date": self.date,
			"posting_time": nowtime(),
			"qty": warehouse and -1*flt(item.quantity) or flt(item.quantity),
			"voucher_type": self.doctype,
			"voucher_no": item.name,
			"company": self.company,
			"allow_zero_valuation": 1,
		})
	
	def on_submit(self):
		se = frappe.new_doc("Stock Entry");
		se.purpose = "Repack"
		se.set_posting_time = 1
		se.posting_date = self.date
		se.posting_time = nowtime()
		for row in self.items:
			se.append('items',{
				'item_code': row.item_name,
				's_warehouse': row.source_warehouse,
				'batch_no': row.batch_no,
				'basic_rate': row.basic_rate,
				'basic_amount': row.basic_amount,
				'qty': row.quantity
			})
			
		se.append('items',{
			'item_code': self.product_name,
			't_warehouse': self.warehouse,
			'batch_no' : self.batch_no,
			'qty': self.actual_qty,
			'basic_rate': self.per_unit_amount,
			'basic_amount': self.amount
		})


		se.save()
		self.db_set('stock_entry',se.name)
		se.submit()
		frappe.db.commit()
		
	def on_cancel(self):
		se = frappe.get_doc("Stock Entry",self.stock_entry)
		se.cancel()
		self.db_set('stock_entry','')
		frappe.db.commit()

@frappe.whitelist()
def make_outward_sample(source_name, target_doc=None):
	def postprocess(source, doc):
		from roopdyes.api import get_spare_price

		doc.link_to = "Customer"
		customer_name, destination = frappe.db.get_value("Customer", doc.party, ['customer_name', 'territory'])
		doc.party_name = customer_name
		doc.destination_1 = doc.destination = destination

		total_amount = 0.0
		for d in doc.details:
			price = get_spare_price(d.item_name, "Standard Buying").price_list_rate

			if d.batch_yield:
				bomyield = frappe.db.get_value("BOM",{'item': d.item_name},"batch_yield")
				if bomyield != 0:
					d.rate = (price * flt(bomyield)) / d.batch_yield
				else:
					d.rate = (price * 2.2) / d.batch_yield
			else:
				d.rate = price
			
			d.price_list_rate = price
			d.amount = flt(d.rate) * d.quantity
			total_amount += d.amount

		doc.total_amount = total_amount
		doc.per_unit_price = total_amount / doc.total_qty

	doc = get_mapped_doc("Ball Mill Data Sheet", source_name, {
		"Ball Mill Data Sheet": {
			"doctype": "Outward Sample",
			"validation": {
				"docstatus": ["=", 1]
			},
			"field_map": {
				"name": 'ball_mill_ref',
				"customer_name": "party",
				"total_yield": "batch_yield"
			},
			"field_no_map": [
				"naming_series",
				"remarks"
			]
		},
		"Ball Mill Data Sheet Item": {
			"doctype": "Outward Sample Detail",
		}
	}, target_doc, postprocess)

	return doc