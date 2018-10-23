from __future__ import unicode_literals
import frappe
import json
from frappe.utils import flt
from frappe import _, sendmail, db
from erpnext.utilities.product import get_price
from frappe.model.mapper import get_mapped_doc
from frappe.contacts.doctype.address.address import get_address_display, get_default_address
from frappe.contacts.doctype.contact.contact import get_contact_details, get_default_contact
from erpnext.manufacturing.doctype.production_order.production_order import ProductionOrder
from frappe.utils import nowdate

@frappe.whitelist()
def override_po_functions(self, method):
	ProductionOrder.get_status = get_status
	ProductionOrder.update_production_order_qty = update_production_order_qty

def get_status(self, status=None):

	'''Return the status based on stock entries against this production order'''
	if not status:
		status = self.status

	if self.docstatus==0:
		status = 'Draft'
	elif self.docstatus==1:
		if status != 'Stopped':
			stock_entries = frappe._dict(frappe.db.sql("""select purpose, sum(fg_completed_qty)
				from `tabStock Entry` where production_order=%s and docstatus=1
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

def update_production_order_qty(self):
	"""Update **Manufactured Qty** and **Material Transferred for Qty** in Production Order
		based on Stock Entry"""

	for purpose, fieldname in (("Manufacture", "produced_qty"),
		("Material Transfer for Manufacture", "material_transferred_for_manufacturing")):
		qty = flt(frappe.db.sql("""select sum(fg_completed_qty)
			from `tabStock Entry` where production_order=%s and docstatus=1
			and purpose=%s""", (self.name, purpose))[0][0])

		self.db_set(fieldname, qty)

@frappe.whitelist()
def se_on_submit(self, method):
	if self.purpose in ["Material Transfer for Manufacture", "Manufacture"]:
		last_item = self.items[len(self.items)-1]
		
		batch = frappe.get_doc("Batch", last_item.batch_no)
		batch.db_set('batch_yield', self.batch_yield)
		batch.db_set('concentration_', self.concentration)

		po = frappe.get_doc("Production Order", self.production_order)
		po.db_set('batch_yield', self.batch_yield)
		po.db_set('concentration', self.concentration)
		po.db_set('batch', last_item.batch_no)

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
	per_unit_price = flt(self.total_cost) / flt(self.quantity)

	if self.per_unit_price != per_unit_price:
		self.db_set('per_unit_price', per_unit_price)
		db.commit()

@frappe.whitelist()
def enqueue_update_cost():
	frappe.enqueue("roopdyes.api.update_cost")
	frappe.msgprint(_("Queued for updating latest price in all Bill of Materials. It may take a few minutes."))

def update_cost():
	from erpnext.manufacturing.doctype.bom.bom import get_boms_in_bottom_up_order

	bom_list = get_boms_in_bottom_up_order()
	for bom in bom_list:
		bom_obj = frappe.get_doc("BOM", bom)
		bom_obj.update_cost(update_parent=False, from_child_bom=True)

		per_unit_price = flt(bom_obj.total_cost) / flt(bom_obj.quantity)

		if bom_obj.per_unit_price != per_unit_price:
			bom_obj.db_set('per_unit_price', per_unit_price)

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
	doc = frappe.get_doc("Production Order", name)
	doc.db_set("status", "Completed")

	return "Completed"