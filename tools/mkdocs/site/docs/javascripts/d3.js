document$.subscribe(function () {
    // Function to parse table and return data
    function parseTable(table) {
        var data = [];
        var rows = table.querySelectorAll("tr");
        rows.forEach((row, i) => {
            // Skipping header row and filter row
            if (i > 1) {
                var cells = row.querySelectorAll("td");
                data.push({ source: cells[0].textContent, target: cells[1].textContent, level: cells[2].textContent });
            }
        });
        return data;
    }

    // Function to create graph
    function createGraph(data, elementId) {
        // Extract nodes and links
        var nodes = Array.from(new Set(data.flatMap(d => [d.source, d.target])))
            .map(id => ({ id }));

        var links = data.map(d => ({ source: d.source, target: d.target }));

        // Set up the dimensions of the graph
        var width = 800, height = 600;

        // Append SVG for the graph
        var svg = d3.select(elementId).append("svg")
            .attr("width", width)
            .attr("height", height);

        // Create a force simulation
        var simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2));

        // Create links
        var link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("stroke-width", d => Math.sqrt(d.value));

        // Create nodes
        var node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("r", 5)
            .attr("fill", "#69b3a2");

        // Update positions on each simulation 'tick'
        simulation.on("tick", () => {
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });
    }

    // Find all tables that have a th with the class .graph and generate graphs
    document.querySelectorAll("table").forEach((table, index) => {
        var graphHeader = table.querySelector("th.graph");
        if (graphHeader) {
            var data = parseTable(table);
            console.log(data);
            var graphId = "graph" + index;
            var div = document.createElement("div");
            div.id = graphId;
            table.after(div);
            createGraph(data, "#" + graphId);
        }
    });
});
