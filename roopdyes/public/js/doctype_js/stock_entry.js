frappe.ui.form.on("Stock Entry Detail", {
    batch_no:function(frm,cdt,cdn){
        frm.events.cal_qty(frm)
    },
    rate: function(frm,cdt,cdn){
        frm.events.cal_qty(frm)
    }
});

frappe.ui.form.on("Stock Entry", {
    validate: function (frm) {
        frm.trigger('cal_qty');
    },
    cal_qty: function (frm) {
        let qty = 0;
        frm.doc.items.forEach(function (d) {
            if(d.batch_no){                
                frappe.db.get_value("Batch", d.batch_no, ['packaging_material', 'packing_size', 'lot_no', 'batch_yield', 'concentration'], function (r) {
                    frappe.model.set_value(d.doctype, d.name, 'packaging_material', r.packaging_material);
                    frappe.model.set_value(d.doctype, d.name, 'packing_size', r.packing_size);
                    frappe.model.set_value(d.doctype, d.name, 'lot_no', r.lot_no);
                    frappe.model.set_value(d.doctype, d.name, 'batch_yield', r.batch_yield);
                    frappe.model.set_value(d.doctype, d.name, 'concentration', r.concentration);
                    frm.refresh_fields()
                })
            }
        });
        frm.refresh_field('items');
    },
}
)