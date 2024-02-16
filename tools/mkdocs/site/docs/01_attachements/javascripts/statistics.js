document$.subscribe(function () {

    function parseTable(table) {
        var data = [];
        table.querySelectorAll("tr").forEach((row, i) => {
            if (i > 0) {
                var cells = row.querySelectorAll("td");
                data.push({ name: cells[1].textContent, value: Number(cells[2].textContent) });
            }
        });
        return data;
    }

    function createPieChart(data, elementId) {
        // Set up the dimensions of the graph
        var width = 500, height = 500;

        // Append SVG for the graph
        var svg = d3.select(elementId).append("svg")
            .attr("width", width)
            .attr("height", height);

        // Set up the dimensions of the graph
        var radius = Math.min(width, height) / 2 - 20;

        // Append a group to the SVG
        var g = svg.append("g")
            .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

        // Set up the color scale
        var color = d3.scaleOrdinal()
            .domain(data.map(d => d.name))
            .range(d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length).reverse());

        // Compute the position of each group on the pie
        var pie = d3.pie()
            .value(d => d.value);
        var data_ready = pie(data);

        // Build the pie chart
        g.selectAll('whatever')
            .data(data_ready)
            .enter()
            .append('path')
            .attr('d', d3.arc()
                .innerRadius(0)
                .outerRadius(radius)
            )
            .attr('fill', d => color(d.data.name))
            .attr("stroke", "black")
            .style("stroke-width", "2px")
            .style("opacity", 0.7);

        // Add labels
        g.selectAll('whatever')
            .data(data_ready)
            .enter()
            .append('text')
            .text(d => d.data.name)
            .attr("transform", d => "translate(" + d3.arc().innerRadius(0).outerRadius(radius).centroid(d) + ")")
            .style("text-anchor", "middle")
            .style("font-size", 17);
    }

    function createBarChart(data, elementId, mode) {
        // Set up the dimensions of the graph
        var svgWidth = 1000, svgHeight = 1000;
        var margin = { top: 20, right: 200, bottom: 350, left: 60 }, // Increase bottom margin for x-axis labels
            width = svgWidth - margin.left - margin.right,
            height = svgHeight - margin.top - margin.bottom;

        // Append SVG for the graph
        var svg = d3.select(elementId).append("svg")
            .attr("width", svgWidth)
            .attr("height", svgHeight)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        // Set up the scales
        var x = d3.scaleBand()
            .range([0, width])
            .padding(0.2)
            .domain(data.map(d => d.name));

        var maxYValue = d3.max(data, d => d.value);
        if (mode == "log") {
            var minYValue = d3.min(data, d => d.value);
            if (minYValue <= 0) {
                console.error("Logarithmic scale requires strictly positive values");
                return;
            }
        }
        var y = mode == "log" ? d3.scaleLog().range([height, 0]).domain([1, maxYValue]) : d3.scaleLinear().range([height, 0]).domain([0, maxYValue + maxYValue * 0.1]);

        // Set up the color scale
        var color = d3.scaleOrdinal()
            .range(d3.schemeCategory10);

        // Set up the axes
        var xAxis = d3.axisBottom(x)
            .tickSize(0)
            .tickPadding(6);

        var yAxis = d3.axisLeft(y);

        // Add the bars
        svg.selectAll(".bar")
            .data(data)
            .enter().append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.name))
            .attr("y", d => {
                if (mode == "log") {
                    return y(Math.max(1, d.value));
                } else if (mode == "linear") {
                    return y(d.value);
                }
            })
            .attr("width", x.bandwidth())
            .attr("height", d => {
                if (mode == "log") {
                    return height - y(Math.max(1, d.value));
                } else if (mode == "linear") {
                    return height - y(d.value);
                }
            })
            .attr("fill", d => color(d.name));


        // Add and rotate x-axis labels
        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis)
            .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)"); // Rotate the labels

        // Add the y-axis
        svg.append("g")
            .call(yAxis);
    }


    document.querySelectorAll("table").forEach((table, index) => {
        var pieChart = table.querySelector("th.pie-chart");
        var barChart = table.querySelector("th.bar-chart");
        var logBarChart = table.querySelector("th.log-bar-chart");
        graphId = "graph" + index;
        var div = document.createElement("div");
        div.id = graphId;
        table.parentNode.insertBefore(div, table);
        if (pieChart) {
            var data = parseTable(table);
            createPieChart(data, "#" + graphId);
        }
        if (barChart) {
            var data = parseTable(table);
            createBarChart(data, "#" + graphId, "linear");
        }
        if (logBarChart) {
            var data = parseTable(table);
            createBarChart(data, "#" + graphId, "log");
        }
    })

});
