from chemical.chemical.doctype.ball_mill_data_sheet.ball_mill_data_sheet import BallMillDataSheet as _BallMillDataSheet
import frappe
from chemical.comments_api import creation_comment,status_change_comment,cancellation_comment,delete_comment
from frappe.utils import flt
from erpnext.stock.doctype.item.item import get_item_defaults


class BallMillDataSheet(_BallMillDataSheet):
	def on_submit(self):
		creation_comment(self)
		# maintain_as_is_new = frappe.db.get_value("Company", self.company, "maintain_as_is_new")
		if self.get('create_stock_entry') == 0:
			create_stock_entry = 0
		else:
			create_stock_entry = 1
		if create_stock_entry:
			se = frappe.new_doc("Stock Entry")
			se.purpose = "Repack"
			se.company = self.company
			se.stock_entry_type = "Repack"
			se.set_posting_time = 1
			se.posting_date = self.date
			se.posting_time = self.posting_time
			se.from_ball_mill = 1
			# se.branch = self.branch
			cost_center = frappe.db.get_value("Company",self.company,"cost_center")
			if hasattr(self,'send_to_party'):
				se.send_to_party = self.send_to_party
			if hasattr(self,'party_type'):
				se.party_type = self.party_type
			if hasattr(self,'party'):
				se.party = self.party

			for row in self.items:
				item = get_item_defaults(row.item_name, self.company)
				item_dict = {
					'item_code': row.item_name,
					's_warehouse': row.source_warehouse,
					'qty': row.qty,
					'basic_rate': row.basic_rate,
					't_warehouse':None,
					'uom':frappe.db.get_value("Item",row.item_name,"stock_uom"),
					'stock_uom':frappe.db.get_value("Item",self.product_name,"stock_uom"),
					'basic_amount': row.basic_amount,
					'cost_center': item.get("buying_cost_center") or item.get("selling_cost_center") or cost_center,
					'batch_no': row.batch_no,
					'concentration':row.concentration,
					'packaging_material':row.packaging_material,
					'packing_size':row.packing_size,
					'no_of_packages':row.no_of_packages,
					"use_serial_batch_fields": True
				}

				se.append('items', item_dict)
			for d in self.packaging:
				item = get_item_defaults(self.product_name, self.company)
				item_dict = {
					'item_code': self.product_name,
					't_warehouse': d.warehouse or self.warehouse,
					's_warehouse':None,
					'uom':frappe.db.get_value("Item",self.product_name,"stock_uom"),
					'stock_uom':frappe.db.get_value("Item",self.product_name,"stock_uom"),
					'qty': d.qty,
					'packaging_material': d.packaging_material,
					'packing_size': d.packing_size,
					'no_of_packages': d.no_of_packages,
					'lot_no': d.lot_no,
					'concentration': d.concentration or self.concentration,
					'basic_rate': self.per_unit_amount,
					'valuation_rate': self.per_unit_amount,
					'basic_amount': flt(d.qty * self.per_unit_amount),
					'cost_center': item.get("buying_cost_center") or item.get("selling_cost_center") or cost_center,
					'uv_value':self.get("weighted_average_uv_value"),
					"use_serial_batch_fields": True,
					"batch_yield":self.total_yield
				}

				se.append('items', item_dict)
			for d in self.ball_mill_additional_cost:	
				se.append('additional_costs',{
					'expense_account':d.expense_account ,
					'description': d.description,
					'amount': flt(d.amount),
					'rate':flt(d.amount),
					'qty':1
				})

			se.save()
			se.submit()
			self.db_set('stock_entry',se.name)
			batch = None
			for row in self.packaging:
				batch_name = frappe.db.sql("""
					SELECT sed.batch_no from `tabStock Entry` se LEFT JOIN `tabStock Entry Detail` sed on (se.name = sed.parent)
					WHERE 
						se.name = '{name}'
						and (sed.t_warehouse != '' or sed.t_warehouse IS NOT NULL) 
						and sed.qty = {qty}
						and sed.packaging_material = '{packaging_material}'
						and sed.packing_size = '{packing_size}'
						and sed.no_of_packages = {no_of_packages}""".format(
							name=se.name,
							qty=row.qty,
							packaging_material=row.packaging_material,
							packing_size=row.packing_size,
							no_of_packages=row.no_of_packages,
						))
				if batch_name:
					batch = batch_name[0][0] or ''
				if batch:
					row.db_set('batch_no', batch)
					if self.customer_name:
						frappe.db.set_value("Batch",batch,'customer',self.customer_name)
					# if self.lot_no:
					# 	frappe.db.set_value("Batch",batch,'sample_ref_no',self.lot_no)
