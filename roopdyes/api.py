from __future__ import unicode_literals
import frappe
import json
from frappe.utils import flt, getdate, cstr
from frappe import _, sendmail, db
from erpnext.utilities.product import get_price
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_contact_details, get_default_contact
from erpnext.manufacturing.doctype.work_order.work_order import WorkOrder
from frappe.utils import nowdate
from erpnext.selling.doctype.customer.customer import Customer
from erpnext.accounts.utils import get_fiscal_year
from erpnext.manufacturing.doctype.bom.bom import add_additional_cost
from six import itervalues

@frappe.whitelist()
def get_customer_ref_code(item_code, customer):
	ref_code = db.get_value("Item Customer Detail", {'parent': item_code, 'customer_name': customer}, 'ref_code')
	return ref_code if ref_code else ''

@frappe.whitelist()	
def si_on_submit(self, method):
	pass
	#create_jv(self)
	# In exim app

@frappe.whitelist()	
def si_on_cancel(self, method):
	pass
	#cancel_jv(self)
	# In exim app
	
def create_jv(self):
	abbr = frappe.db.get_value("Company", self.company, 'abbr')
	
	if self.currency != "INR":
		if self.total_duty_drawback:
			drawback_receivable_account = frappe.db.get_value("Company", { "company_name": self.company}, "duty_drawback_receivable_account")
			drawback_income_account = frappe.db.get_value("Company", { "company_name": self.company}, "duty_drawback_income_account")
			drawback_cost_center = frappe.db.get_value("Company", { "company_name": self.company}, "duty_drawback_cost_center")
			if not drawback_receivable_account:
				frappe.throw(_("Set Duty Drawback Receivable Account in Company"))
			elif not drawback_income_account:
				frappe.throw(_("Set Duty Drawback Income Account in Company"))
			elif not drawback_cost_center:
				frappe.throw(_("Set Duty Drawback Cost Center in Company"))
			else:
				jv = frappe.new_doc("Journal Entry")
				jv.voucher_type = "Duty Drawback Entry"
				jv.posting_date = self.posting_date
				jv.company = self.company
				jv.cheque_no = self.name
				jv.cheque_date = self.posting_date
				jv.user_remark = "Duty draw back against " + self.name + " for " + self.customer
				jv.append("accounts", {
					"account": drawback_receivable_account,
					"cost_center": drawback_cost_center,
					"debit_in_account_currency": self.total_duty_drawback
				})
				jv.append("accounts", {
					"account": drawback_income_account,
					"cost_center": drawback_cost_center,
					"credit_in_account_currency": self.total_duty_drawback
				})
				try:
					jv.save(ignore_permissions=True)
					jv.submit()
				except Exception as e:
					frappe.throw(str(e))
				else:
					self.db_set('duty_drawback_jv',jv.name)
				
				#self.save(ignore_permissions=True)
		
		if self.total_meis:
			meis_receivable_account = frappe.db.get_value("Company", { "company_name": self.company}, "meis_receivable_account")
			meis_income_account = frappe.db.get_value("Company", { "company_name": self.company}, "meis_income_account")
			meis_cost_center = frappe.db.get_value("Company", { "company_name": self.company}, "meis_cost_center")
			if not meis_receivable_account:
				frappe.throw(_("Set MEIS Receivable Account in Company"))
			elif not meis_income_account:
				frappe.throw(_("Set MEIS Income Account in Company"))
			elif not meis_cost_center:
				frappe.throw(_("Set MEIS Cost Center in Company"))
			else:
				meis_jv = frappe.new_doc("Journal Entry")
				meis_jv.voucher_type = "MEIS Entry"
				meis_jv.posting_date = self.posting_date
				meis_jv.company = self.company
				meis_jv.cheque_no = self.name
				meis_jv.cheque_date = self.posting_date
				meis_jv.user_remark = "MEIS against " + self.name + " for " + self.customer
				meis_jv.append("accounts", {
					"account": meis_receivable_account,
					"cost_center": meis_cost_center,
					"debit_in_account_currency": self.total_meis
				})
				meis_jv.append("accounts", {
					"account": meis_income_account,
					"cost_center": meis_cost_center,
					"credit_in_account_currency": self.total_meis
				})
				
				try:
					meis_jv.save(ignore_permissions=True)
					meis_jv.submit()
				except Exception as e:
					frappe.throw(str(e))
				else:
					self.db_set('meis_jv',meis_jv.name)
					
def cancel_jv(self):
	if self.duty_drawback_jv:
		jv = frappe.get_doc("Journal Entry", self.duty_drawback_jv)
		jv.cancel()
		self.db_set('duty_drawback_jv','')
		
	if self.meis_jv:
		jv = frappe.get_doc("Journal Entry", self.meis_jv)
		jv.cancel()
		self.db_set('meis_jv','')
		
@frappe.whitelist()
def override_po_functions(self, method):
	WorkOrder.get_status = get_status
	WorkOrder.update_work_order_qty = update_work_order_qty

def get_status(self, status=None):

	'''Return the status based on stock entries against this production order'''
	if not status:
		status = self.status

	if self.docstatus==0:
		status = 'Draft'
	elif self.docstatus==1:
		if status != 'Stopped':
			stock_entries = frappe._dict(frappe.db.sql("""select purpose, sum(fg_completed_qty)
				from `tabStock Entry` where work_order=%s and docstatus=1
				group by purpose""", self.name))

			status = "Not Started"
			if stock_entries:
				status = "In Process"
				produced_qty = stock_entries.get("Manufacture")

				under_production = frappe.db.get_value("Manufacturing Settings", None, "under_production_allowance_percentage")
				allowed_qty = flt(self.qty) * (100 - float(under_production)) / 100.0
				
				if flt(produced_qty) >= flt(allowed_qty):
					status = "Completed"
	else:
		status = 'Cancelled'

	return status

def update_work_order_qty(self):
	"""Update **Manufactured Qty** and **Material Transferred for Qty** in Production Order
		based on Stock Entry"""

	for purpose, fieldname in (("Manufacture", "produced_qty"),
		("Material Transfer for Manufacture", "material_transferred_for_manufacturing")):
		qty = flt(frappe.db.sql("""select sum(fg_completed_qty)
			from `tabStock Entry` where work_order=%s and docstatus=1
			and purpose=%s""", (self.name, purpose))[0][0])

		self.db_set(fieldname, qty)

@frappe.whitelist()
def se_on_submit(self, method):
	if self.purpose in ["Material Transfer for Manufacture", "Manufacture"] and self.work_order:
		if self.purpose == 'Manufacture':
			po = frappe.get_doc("Work Order",self.work_order)
			if not self.volume:
				frappe.throw(_("Please add Fuel Gas Qty before submitting the stock entry"))

			if self.volume:
				update_po_volume(self, po)
	
			last_item = self.items[len(self.items)-1]
			
			batch = frappe.get_doc("Batch", last_item.batch_no)
			batch.db_set('batch_yield', self.batch_yield)
			batch.db_set('concentration', self.concentration)
			batch.db_set('lot_no', last_item.lot_no)

			po = frappe.get_doc("Work Order", self.work_order)
			po.db_set('batch_yield', self.batch_yield)
			po.db_set('concentration', self.concentration)
			po.db_set('batch', last_item.batch_no)
			po.db_set('lot_no', last_item.lot_no)

@frappe.whitelist()
def stock_entry_on_cancel(self, method):
	if self.work_order:
		pro_doc = frappe.get_doc("Work Order", self.work_order)
		if self.volume:		
			update_po_volume(self, pro_doc)
		pro_doc.save()
		frappe.db.commit()
	
def update_po_volume(self, po, ignore_permissions = True):
	if self._action == 'submit':
		
		po.volume += self.volume
		self.volume_cost = flt(flt(self.volume) * flt(self.volume_rate))		
		po.volume_cost +=  self.volume_cost
		#self.save(ignore_permissions = True)
		po.save(ignore_permissions = True)

	elif self._action == 'cancel':
		po.volume -= self.volume
		po.volume_cost -= self.volume_cost
		po.lot_no = ''
		po.batch_yield = 0.0
		po.save(ignore_permissions=True)
		
@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		for row in source.items:
			target.append("items", {
				"item_code": row.item_code,
				"item_name": row.item_name,
				"schedule_date": source.schedule_date,
				"item_group": row.item_group,
				"brand": row.brand,
				"image": row.image,
				"description": row.description,
				"uom": row.uom,
				"qty":row.qty
			})
	
	doclist = get_mapped_doc("Opportunity", source_name, {
			"Opportunity": {
				"doctype": "Request for Quotation",
				"field_map": {	
				}
			},
		}, target_doc, set_missing_values)
	return doclist

@frappe.whitelist()
def get_party_details(party=None, party_type="Customer", ignore_permissions=False):

	if not party:
		return {}

	if not frappe.db.exists(party_type, party):
		frappe.throw(_("{0}: {1} does not exists").format(party_type, party))

	return _get_party_details(party, party_type, ignore_permissions)

def _get_party_details(party=None, party_type="Customer", ignore_permissions=False):

	out = frappe._dict({
		party_type.lower(): party
	})

	party = out[party_type.lower()]

	if not ignore_permissions and not frappe.has_permission(party_type, "read", party):
		frappe.throw(_("Not permitted for {0}").format(party), frappe.PermissionError)

	party = frappe.get_doc(party_type, party)
	
	set_address_details(out, party, party_type)
	set_contact_details(out, party, party_type)
	set_other_values(out, party, party_type)
	set_organisation_details(out, party, party_type)
	return out

def set_address_details(out, party, party_type):
	billing_address_field = "customer_address" if party_type == "Lead" \
		else party_type.lower() + "_address"
	out[billing_address_field] = get_default_address(party_type, party.name)
	
	# address display
	out.address_display = get_address_display(out[billing_address_field])

def set_contact_details(out, party, party_type):
	out.contact_person = get_default_contact(party_type, party.name)

	if not out.contact_person:
		out.update({
			"contact_person": None,
			"contact_display": None,
			"contact_email": None,
			"contact_mobile": None,
			"contact_phone": None,
			"contact_designation": None,
			"contact_department": None
		})
	else:
		out.update(get_contact_details(out.contact_person))

def set_other_values(out, party, party_type):
	# copy
	if party_type=="Customer":
		to_copy = ["customer_name", "customer_group", "territory", "language"]
	else:
		to_copy = ["supplier_name", "supplier_type", "language"]
	for f in to_copy:
		out[f] = party.get(f)
		
def set_organisation_details(out, party, party_type):

	organisation = None

	if party_type == 'Lead':
		organisation = frappe.db.get_value("Lead", {"name": party.name}, "company_name")
	elif party_type == 'Customer':
		organisation = frappe.db.get_value("Customer", {"name": party.name}, "customer_name")
	elif party_type == 'Supplier':
		organisation = frappe.db.get_value("Supplier", {"name": party.name}, "supplier_name")

	out.update({'party_name': organisation})

@frappe.whitelist()
def send_lead_mail(recipients, person):

	from frappe.utils.file_manager import get_file

	message = """<p>
				    Respected """ + person + """,
				</p>
				<p>
				    First of all thank you very much to sparing your precious time to visit our
				    booth at the 18th China Interdye Exhibition 2018. It was pleasure
				    to meet with you personally and discuss about the business.
				</p>
				<p>
				    This is with the reference to our personal meeting in China Interdye. Hence
				    sending introduction of our company as below.
				</p>
				<p>
				    This is Aum Shah from Roop Dyes &amp; Intermediates, India. We are
				    manufacturers and exporters of Dyestuff and intermediates since 1978 and
				    have 02 plants with combined installed capacity of 600 MT. We are very
				    strong in all kinds of Blacks, Bi-functional and Tri-functional Dyes and
				    Vinyl Sulfonic Based Dyes. We wish and hope to build a strong cooperation
				    with your esteemed company for a mutually beneficial association. We
				    request you to kindly share your requirements so that we can submit our
				    price quotations and samples for your evaluation.
				</p>
				<p>
				    Moreover if you provide us your quality standard samples, we promise you to
				    develop and send you exactly matching counter samples as required by you.
				</p>
				<p>
				    The Salient Features are as follows:
				</p>
				<p>
				    1. Plant with installed capacity of <strong>400 MT for Black</strong>.
				</p>
				<p>
				2. Plant with installed capacity of <strong>200 MT for Blue. Red, Orange and Yellow series</strong>
				</p>
				<p>
				3. In-house Spray dryer with a capacity of <strong>750 liters per hour</strong>.
				</p>
				<p>
				    4. In-house <strong>R.O. water treatment</strong> plant.
				</p>
				<p>
				    <strong>5.</strong>
				    <strong style='color: rgb(192,0,0)'>
				        Specialized in complete PCA (Para Chloro Aniline) free products (&gt;5
				        ppm which is untraceable).
				    </strong>
				</p>
				<p>
				    6. Dedicated Staff at every level of Production, Quality Control &amp;
				    Dispatch.
				</p>
				<p>
				    7. Dedicated Personnel for Sales and after Sales Services.
				</p>
				<p>
				    8. Totally Professional Corporate working environment.
				</p>
				<p>
				    9. An <strong>ISO 9001:2008, 14001:2004</strong> certified company
				</p>
				<p>
				10. Various Quality and Compliance Certifications like,    <strong>Pre-Reach, GOTS &amp; Oeko-Tex 100</strong>.
				</p>
				<p>
				    11. The Quality complies with global Standards
				</p>
				<p>
				    12. Star Export house and winner of <strong>National Export Award</strong>,
				    Government of India.
				</p>
				<p>
				    13. Customized Dyes as per required quality standards.
				</p>
				<p>
				    14. Best competitive pricing with unmatched quality
				</p>
				<p>
				    Moreover, we can also supply Turquoise Series through outsourcing but the
				    "Quality Check and Control" is done in-house at Roop Dyes Laboratory.
				</p>
				<p>
				    We hope to get into long lasting business cooperation with your esteemed
				    company and create a new growth index by working together as beneficiary to
				    each other. I would also like to have word with you, please let me know the
				    suitable time to call you.
				</p>
				<p>
				    Awaiting your positive response.
				</p>
				<p>
				    <strong>Thanks, and Best Regards</strong>
				</p>
				<p>
					Ajay Shah
				</p>
				<p>
				    <strong>Partner</strong>
				</p>
				<p>
				    <strong>
				        Web: <a href="http://www.roopdyes.com">www.roopdyes.com</a>
				    </strong>
				</p>
				<p>
				    <img width="209" height="49" src="/files/Roop_Dyes_&_Intermediates.png"/>
				</p>
				<div style='color: rgb(192,0,0)'>
				<p>
				    <strong>A/911 ATMA House, </strong>
				</p>
				<p>
				    <strong>Opp Old RBI, Ashram Road, </strong>
				</p>
				<p>
				    <strong>Ahmedabad - 380009 </strong>
				</p>
				<p>
				    <strong>Gujarat, India.</strong>
				</p>
				<p>
				    Ph. No.: (O) +91-79-30071490
				</p>
				<p>
				    (M) +91 9724443213
				</p>
				<p>
				    Email : <a href="mailto:info@roopdyes.com">info@roopdyes.com</a>
				</p></div>"""

	attachment = [{'fid': 'ec7268460a'}]

	sendmail(recipients=recipients,
			subject = "ROOPDYES // Manufacturer & Exporter of Dyes",
			message = message,
			attachments = attachment)

	return "Success"


@frappe.whitelist()
def get_spare_price(item_code, price_list, customer_group="All Customer Groups", company="ROOP DYES & INTERMEDIATES"):
	price = get_price(item_code, price_list, customer_group, company)
	
	if not price:
		price = frappe._dict({'price_list_rate': 0.0})

	return price

@frappe.whitelist()
def upadte_item_price(item, price_list, per_unit_price):
	if db.exists("Item Price",{"item_code":item,"price_list":price_list}):
		name = db.get_value("Item Price",{"item_code":item,"price_list":price_list},'name')
		db.set_value("Item Price",name,"price_list_rate", per_unit_price)
	else:
		item_price = frappe.new_doc("Item Price")
		item_price.price_list = price_list
		item_price.item_code = item
		item_price.price_list_rate = per_unit_price
		
		item_price.save()
	db.commit()
		
	return "Item Price Updated!"
	
@frappe.whitelist()	
def upadte_item_price_daily():
	data = db.sql("""
		select 
			item, per_unit_price , buying_price_list
		from
			`tabBOM` 
		where 
			docstatus < 2 
			and is_default = 1 """,as_dict =1)
			
	for row in data:
		upadte_item_price(row.item, row.buying_price_list, row.per_unit_price)
		
	return "Latest price updated in Price List."
@frappe.whitelist()
def bom_before_save(self, method):
	cal_operatinal_cost(self)

@frappe.whitelist()
def bom_on_update(self, method):
	cal_operatinal_cost(self)

def cal_operatinal_cost(self):
	self.operating_cost = self.fuel_gas_quantity * self.fuel_gas_rate
	self.total_cost = self.operating_cost + self.raw_material_cost - self.scrap_material_cost
	self.per_unit_price = flt(self.total_cost) / flt(self.quantity)

@frappe.whitelist()
def enqueue_update_cost():
	frappe.enqueue("roopdyes.api.update_cost")
	frappe.msgprint(_("Queued for updating latest price in all Bill of Materials. It may take a few minutes..."))

def update_cost():
	from erpnext.manufacturing.doctype.bom.bom import get_boms_in_bottom_up_order

	bom_list = get_boms_in_bottom_up_order()
	for bom in bom_list:
		bom_obj = frappe.get_doc("BOM", bom)
		bom_obj.update_cost(update_parent=False, from_child_bom=True)

		operating_cost = flt(bom_obj.fuel_gas_quantity) * flt(bom_obj.fuel_gas_rate)
		bom_obj.db_set("total_cost",bom_obj.raw_material_cost + operating_cost - bom_obj.scrap_material_cost)
		per_unit_price = flt(bom_obj.total_cost) / flt(bom_obj.quantity)
		#print(bom_obj.name, flt(bom_obj.raw_material_cost) , flt(bom_obj.fuel_gas_quantity) * flt(bom_obj.fuel_gas_rate), flt(bom_obj.total_cost), flt(bom_obj.quantity), flt(bom_obj.total_cost) /flt(bom_obj.quantity))
		bom_obj.db_set('per_unit_price',flt(bom_obj.total_cost) / flt(bom_obj.quantity))
		bom_obj.db_set('operating_cost', operating_cost)

		# if bom_obj.per_unit_price != per_unit_price:
			# bom_obj.db_set('per_unit_price', per_unit_price)
		if frappe.db.exists("Item Price",{"item_code":bom_obj.item,"price_list":bom_obj.buying_price_list}):
			name = frappe.db.get_value("Item Price",{"item_code":bom_obj.item,"price_list":bom_obj.buying_price_list},'name')
			frappe.db.set_value("Item Price",name,"price_list_rate", per_unit_price)
		else:
			item_price = frappe.new_doc("Item Price")
			item_price.price_list = bom_obj.buying_price_list
			item_price.item_code = bom_obj.item
			item_price.price_list_rate = per_unit_price
			
			item_price.save()
		#frappe.db.commit()

@frappe.whitelist()
def update_outward_sample(doc_name):
	
	outward = frappe.get_doc("Outward Sample", doc_name)

	total_qty = 0
	total_amount = 0
	
	for row in outward.details:
		if row.item_name:
			price = get_spare_price(row.item_name, outward.price_list or "Standard Buying")
			row.db_set('rate', price.price_list_rate)
			row.db_set('price_list_rate', price.price_list_rate)

		if row.batch_yield:
			bomyield = frappe.db.get_value("BOM",{'item': row.item_name},"batch_yield")
			if bomyield != 0:
				row.db_set('rate',(flt(row.price_list_rate)) * flt(bomyield) / row.batch_yield)
			else:
				row.db_set('rate',(flt(row.price_list_rate) * 2.2) / row.batch_yield)

		row.db_set('amount', flt(row.quantity) * flt(row.rate))

		total_qty += row.quantity
		total_amount += flt(row.amount)

	outward.db_set("total_qty", total_qty)
	outward.db_set("total_amount", total_amount)
	outward.db_set("per_unit_price", (total_amount / total_qty))
	outward.db_set("price_updated_on",nowdate())

	return "Price Updated"

@frappe.whitelist()
def finish_production_order(name):
	doc = frappe.get_doc("Work Order", name)
	doc.db_set("status", "Completed")

	return "Completed"
	
# def create_igst_jv(self):
	# abbr = frappe.db.get_value("Company", self.company, 'abbr')
	
	# if len(self.taxes):
		# for row in self.taxes:
			# if self.export_type == "With Payment of Tax" and self.currency != "INR" and 'IGST' in row.account_head:
				# jv = frappe.new_doc("Journal Entry")
				# jv.voucher_type = "Export IGST Entry"
				# jv.posting_date = self.posting_date
				# jv.company = self.company
				# jv.cheque_no = self.invoice_no
				# jv.cheque_date = self.posting_date
				
				# #jv.user_remark = "IGST Payable against" + self.name + " for " + self.customer
					
				# jv.append("accounts", {
					# "account": 'Sales - %s' % abbr,
					# "cost_center": 'Main - %s' % abbr,
					# "debit_in_account_currency": row.base_tax_amount
				# })
				# if self.debit_to == "Debtors - %s" % abbr:
					# jv.multi_currency = 0
					# jv.append("accounts", {
						# "account": self.debit_to,
						# "cost_center": 'Main - %s' % abbr,
						# "party_type": 'Customer',
						# "party": self.customer,
						# "reference_type": 'Sales Invoice',
						# "reference_name": self.name,
						# "credit_in_account_currency": row.base_tax_amount
					# })
				# else:
					# jv.multi_currency = 1
					# jv.append("accounts", {
						# "account": self.debit_to,
						# "cost_center": 'Main - %s' % abbr,
						# "exchange_rate":  self.conversion_rate,
						# "party_type": 'Customer',
						# "party": self.customer,
						# "reference_type": 'Sales Invoice',
						# "reference_name": self.name,
						# "credit_in_account_currency": row.tax_amount_after_discount_amount
					# })
				# jv.save(ignore_permissions=True)
				# self.db_set('gst_jv', jv.name)
				# jv.submit()
				# frappe.db.commit()
	
# def cancel_igst_jv(self):
	# if self.gst_jv:
		# jv = frappe.get_doc("Journal Entry", self.gst_jv)
		# jv.cancel()
		# self.db_set('gst_jv', '')
	# frappe.db.commit()
		

@frappe.whitelist()
def make_stock_entry(work_order_id, purpose, qty=None):
	#from erpnext.stock.doctype.stock_entry.stock_entry import get_additional_costs

	work_order = frappe.get_doc("Work Order", work_order_id)
	if not frappe.db.get_value("Warehouse", work_order.wip_warehouse, "is_group") \
			and not work_order.skip_transfer:
		wip_warehouse = work_order.wip_warehouse
	else:
		wip_warehouse = None

	stock_entry = frappe.new_doc("Stock Entry")
	stock_entry.purpose = purpose
	stock_entry.stock_entry_type = purpose
	stock_entry.work_order = work_order_id
	stock_entry.company = work_order.company
	stock_entry.from_bom = 1
	stock_entry.bom_no = work_order.bom_no
	stock_entry.use_multi_level_bom = work_order.use_multi_level_bom
	stock_entry.fg_completed_qty = qty or (flt(work_order.qty) - flt(work_order.produced_qty))
	if work_order.bom_no:
		stock_entry.inspection_required = frappe.db.get_value('BOM',
			work_order.bom_no, 'inspection_required')

	if purpose=="Material Transfer for Manufacture":
		stock_entry.to_warehouse = wip_warehouse
		stock_entry.project = work_order.project
	else:
		stock_entry.from_warehouse = wip_warehouse
		stock_entry.to_warehouse = work_order.fg_warehouse
		stock_entry.project = work_order.project
		# if purpose=="Manufacture":
		# 	additional_costs = get_additional_costs(work_order, fg_qty=stock_entry.fg_completed_qty)
		# 	stock_entry.set("additional_costs", additional_costs)

	get_items(stock_entry)
	return stock_entry.as_dict()

def get_items(self):
	self.set('items', [])
	self.validate_work_order()

	if not self.posting_date or not self.posting_time:
		frappe.throw(_("Posting date and posting time is mandatory"))

	self.set_work_order_details()

	if self.bom_no:

		if self.purpose in ["Material Issue", "Material Transfer", "Manufacture", "Repack",
				"Subcontract", "Material Transfer for Manufacture", "Material Consumption for Manufacture"]:

			if self.work_order and self.purpose == "Material Transfer for Manufacture":
				item_dict = self.get_pending_raw_materials()
				if self.to_warehouse and self.pro_doc:
					for item in itervalues(item_dict):
						item["to_warehouse"] = self.pro_doc.wip_warehouse
				self.add_to_stock_entry_detail(item_dict)

			elif (self.work_order and (self.purpose == "Manufacture" or self.purpose == "Material Consumption for Manufacture")
				and not self.pro_doc.skip_transfer and frappe.db.get_single_value("Manufacturing Settings",
				"backflush_raw_materials_based_on")== "Material Transferred for Manufacture"):
				get_transfered_raw_materials(self)

			elif (self.work_order and (self.purpose == "Manufacture" or self.purpose == "Material Consumption for Manufacture")
				and self.pro_doc.skip_transfer and frappe.db.get_single_value("Manufacturing Settings",
				"backflush_raw_materials_based_on")== "Material Transferred for Manufacture"):
				get_material_transfered_raw_materials(self)

			elif self.work_order and (self.purpose == "Manufacture" or self.purpose == "Material Consumption for Manufacture") and \
				frappe.db.get_single_value("Manufacturing Settings", "backflush_raw_materials_based_on")== "BOM" and \
				frappe.db.get_single_value("Manufacturing Settings", "material_consumption")== 1:
				self.get_unconsumed_raw_materials()

			else:
				if not self.fg_completed_qty:
					frappe.throw(_("Manufacturing Quantity is mandatory"))

				item_dict = self.get_bom_raw_materials(self.fg_completed_qty)

				#Get PO Supplied Items Details
				if self.purchase_order and self.purpose == "Subcontract":
					#Get PO Supplied Items Details
					item_wh = frappe._dict(frappe.db.sql("""
						select rm_item_code, reserve_warehouse
						from `tabPurchase Order` po, `tabPurchase Order Item Supplied` poitemsup
						where po.name = poitemsup.parent
							and po.name = %s""",self.purchase_order))

				for item in itervalues(item_dict):
					if self.pro_doc and (cint(self.pro_doc.from_wip_warehouse) or not self.pro_doc.skip_transfer):
						item["from_warehouse"] = self.pro_doc.wip_warehouse
					#Get Reserve Warehouse from PO
					if self.purchase_order and self.purpose=="Subcontract":
						item["from_warehouse"] = item_wh.get(item.item_code)
					item["to_warehouse"] = self.to_warehouse if self.purpose=="Subcontract" else ""

				self.add_to_stock_entry_detail(item_dict)

				if self.purpose != "Subcontract":
					scrap_item_dict = self.get_bom_scrap_material(self.fg_completed_qty)
					for item in itervalues(scrap_item_dict):
						if self.pro_doc and self.pro_doc.scrap_warehouse:
							item["to_warehouse"] = self.pro_doc.scrap_warehouse

					self.add_to_stock_entry_detail(scrap_item_dict, bom_no=self.bom_no)

		# fetch the serial_no of the first stock entry for the second stock entry
		if self.work_order and self.purpose == "Manufacture":
			self.set_serial_nos(self.work_order)
			work_order = frappe.get_doc('Work Order', self.work_order)
			add_additional_cost(self, work_order)

		# add finished goods item
		if self.purpose in ("Manufacture", "Repack"):
			self.load_items_from_bom()

	self.set_actual_qty()
	self.calculate_rate_and_amount(raise_error_if_no_rate=False)

def get_transfered_raw_materials(self):
	transferred_materials = frappe.db.sql("""
		select
			item_name, original_item, item_code, qty, sed.t_warehouse as warehouse,
			description, stock_uom, expense_account, cost_center, batch_no
		from `tabStock Entry` se,`tabStock Entry Detail` sed
		where
			se.name = sed.parent and se.docstatus=1 and se.purpose='Material Transfer for Manufacture'
			and se.work_order= %s and ifnull(sed.t_warehouse, '') != ''
		order by item_code
	""", self.work_order, as_dict=1)

	materials_already_backflushed = frappe.db.sql("""
		select
			item_code, sed.s_warehouse as warehouse, sum(qty) as qty
		from
			`tabStock Entry` se, `tabStock Entry Detail` sed
		where
			se.name = sed.parent and se.docstatus=1
			and (se.purpose='Manufacture' or se.purpose='Material Consumption for Manufacture')
			and se.work_order= %s and ifnull(sed.s_warehouse, '') != ''
	""", self.work_order, as_dict=1)

	backflushed_materials= {}
	for d in materials_already_backflushed:
		backflushed_materials.setdefault(d.item_code,[]).append({d.warehouse: d.qty})

	po_qty = frappe.db.sql("""select qty, produced_qty, material_transferred_for_manufacturing from
		`tabWork Order` where name=%s""", self.work_order, as_dict=1)[0]

	manufacturing_qty = flt(po_qty.qty)
	produced_qty = flt(po_qty.produced_qty)
	trans_qty = flt(po_qty.material_transferred_for_manufacturing)

	for item in transferred_materials:
		qty= item.qty
		item_code = item.original_item or item.item_code
		req_items = frappe.get_all('Work Order Item',
			filters={'parent': self.work_order, 'item_code': item_code},
			fields=["required_qty", "consumed_qty", "transferred_qty"]
			)
		if not req_items:
			frappe.msgprint(_("Did not found transfered item {0} in Work Order {1}, the item not added in Stock Entry")
				.format(item_code, self.work_order))
			continue

		req_qty = flt(req_items[0].transferred_qty)
		req_qty_each = flt(req_qty / manufacturing_qty)
		consumed_qty = flt(req_items[0].consumed_qty)

		if trans_qty and manufacturing_qty >= (produced_qty + flt(self.fg_completed_qty)):
			if qty >= req_qty:
				qty = (req_qty/trans_qty) * flt(self.fg_completed_qty)
			else:
				qty = qty - consumed_qty

			if self.purpose == 'Manufacture':
				# If Material Consumption is booked, must pull only remaining components to finish product
				if consumed_qty != 0:
					remaining_qty = consumed_qty - (produced_qty * req_qty_each)
					exhaust_qty = req_qty_each * produced_qty
					if remaining_qty > exhaust_qty :
						if (remaining_qty/(req_qty_each * flt(self.fg_completed_qty))) >= 1:
							qty =0
						else:
							qty = (req_qty_each * flt(self.fg_completed_qty)) - remaining_qty
				else:
					# qty = req_qty_each * flt(self.fg_completed_qty)
					qty = item.qty


		elif backflushed_materials.get(item.item_code):
			for d in backflushed_materials.get(item.item_code):
				if d.get(item.warehouse):
					if (qty > req_qty):
						qty = req_qty
						qty-= d.get(item.warehouse)

		if qty > 0:
			add_to_stock_entry_detail(self, {
				item.item_code: {
					"from_warehouse": item.warehouse,
					"to_warehouse": "",
					"qty": qty,
					"item_name": item.item_name,
					"description": item.description,
					"stock_uom": item.stock_uom,
					"expense_account": item.expense_account,
					"cost_center": item.buying_cost_center,
					"original_item": item.original_item,
					"batch_no": item.batch_no
				}
			})


def get_material_transfered_raw_materials(self):
	mti_data = frappe.db.sql("""select name
		from `tabMaterial Transfer Instruction`
		where docstatus = 1
			and work_order = %s """, self.work_order, as_dict = 1)

	if not mti_data:
		frappe.msgprint(_("No Material Transfer Instruction found!"))
		return

	transfer_data = []

	for mti in mti_data:
		mti_doc = frappe.get_doc("Material Transfer Instruction", mti.name)
		for row in mti_doc.items:
			self.append('items', {
				'item_code': row.item_code,
				'item_name': row.item_name,
				'description': row.description,
				'uom': row.uom,
				'stock_uom': row.stock_uom,
				'qty': row.qty,
				'batch_no': row.batch_no,
				'transfer_qty': row.transfer_qty,
				'conversion_factor': row.conversion_factor,
				's_warehouse': row.s_warehouse,
				'bom_no': row.bom_no,
				'lot_no': row.lot_no,
				'packaging_material': row.packaging_material,
				'packing_size': row.packing_size,
				'batch_yield': row.batch_yield,
				'concentration': row.concentration,
			})

def add_to_stock_entry_detail(self, item_dict, bom_no=None):
	cost_center = frappe.db.get_value("Company", self.company, 'cost_center')

	for d in item_dict:
		stock_uom = item_dict[d].get("stock_uom") or frappe.db.get_value("Item", d, "stock_uom")

		se_child = self.append('items')
		se_child.s_warehouse = item_dict[d].get("from_warehouse")
		se_child.t_warehouse = item_dict[d].get("to_warehouse")
		se_child.item_code = item_dict[d].get('item_code') or cstr(d)
		se_child.item_name = item_dict[d]["item_name"]
		se_child.description = item_dict[d]["description"]
		se_child.uom = item_dict[d]["uom"] if item_dict[d].get("uom") else stock_uom
		se_child.stock_uom = stock_uom
		se_child.qty = flt(item_dict[d]["qty"], se_child.precision("qty"))
		se_child.expense_account = item_dict[d].get("expense_account")
		se_child.cost_center = item_dict[d].get("cost_center") or cost_center
		se_child.allow_alternative_item = item_dict[d].get("allow_alternative_item", 0)
		se_child.subcontracted_item = item_dict[d].get("main_item_code")
		se_child.original_item = item_dict[d].get("original_item")
		se_child.batch_no = item_dict[d].get("batch_no")

		if item_dict[d].get("idx"):
			se_child.idx = item_dict[d].get("idx")

		if se_child.s_warehouse==None:
			se_child.s_warehouse = self.from_warehouse
		if se_child.t_warehouse==None:
			se_child.t_warehouse = self.to_warehouse

		# in stock uom
		se_child.conversion_factor = flt(item_dict[d].get("conversion_factor")) or 1
		se_child.transfer_qty = flt(item_dict[d]["qty"]*se_child.conversion_factor, se_child.precision("qty"))


		# to be assigned for finished item
		se_child.bom_no = bom_no


@frappe.whitelist()
def docs_before_naming(self, method):
	from erpnext.accounts.utils import get_fiscal_year

	date = self.get("transaction_date") or self.get("posting_date") or getdate()

	fy = get_fiscal_year(date)[0]
	fiscal = frappe.db.get_value("Fiscal Year", fy, 'fiscal')

	if fiscal:
		self.fiscal = fiscal
	else:
		fy_years = fy.split("-")
		fiscal = fy_years[0][2:] + '-' + fy_years[1][2:]
		self.fiscal = fiscal