document$.subscribe(function () {
    var tables = document.querySelectorAll("article table:not([class])")
    tables.forEach(function (table) {
        var tf = new TableFilter(table, {
            base_path: "https://unpkg.com/tablefilter@0.7.3/dist/tablefilter/",
            highlight_keywords: true,
            // col_0: "select",
            // col_1: "select",
            grid_layout: false,
            responsive: true,
            watermark: ["Filter table ...", "Filter table ..."],

            auto_filter: {
                delay: 100 //milliseconds
            },
            filters_row_index: 1,
            state: true,
            // alternate_rows: true,
            rows_counter: true,
            status_bar: true,

            themes: [{
                name: "transparent",
            }],

            btn_reset: {
                tooltip: "Reset",
                toolbar_position: "right",
            },
            no_results_message: {
                content: "No matching records found",
            },
            toolbar: true,
            extensions: [{
                name: "sort",
            },
            {
                name: 'filtersVisibility',
                description: 'Sichtbarkeit der Filter',
                toolbar_position: 'right',
            },],
        })
        tf.init()
    })
})