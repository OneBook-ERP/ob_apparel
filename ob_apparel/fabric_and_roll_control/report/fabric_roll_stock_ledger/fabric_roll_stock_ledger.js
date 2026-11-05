frappe.query_reports["Fabric Roll Stock Ledger"] = {
    filters: [
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            options: "Warehouse"
        },
        {
            fieldname: "qc_grade",
            label: __("QC Grade"),
            fieldtype: "Select",
            options: "\nGrade A\nGrade B\nGrade C / Seconds\nQuarantine"
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nAvailable\nReserved\nIn Spreading\nQuarantine\nConsumed\nRemnant"
        }
    ]
};
