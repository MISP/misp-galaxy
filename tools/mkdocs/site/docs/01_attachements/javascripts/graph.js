document$.subscribe(function () {

    const NODE_RADIUS = 8;
    const NODE_COLOR = "#69b3a2";
    const Parent_Node_COLOR = "#ff0000";


    function parseFilteredTable(tf, allData) {
        var data = [];
        tf.getFilteredData().forEach((row, i) => {
            sourcePath = allData[row[0] - 2].sourcePath;
            targetPath = allData[row[0] - 2].targetPath;
            data.push({
                source: row[1][0],
                sourcePath: sourcePath,
                target: row[1][1],
                targetPath: targetPath,
                level: row[1][2]
            });
        });
        return data;
    }

    function parseTable(table) {
        var data = [];
        table.querySelectorAll("tr").forEach((row, i) => {
            if (i > 1) {
                var cells = row.querySelectorAll("td");
                var sourceAnchor = cells[0].querySelector("a");
                var sourcePath = sourceAnchor ? sourceAnchor.getAttribute("href") : null;
                var targetAnchor = cells[1].querySelector("a");
                var targetPath = targetAnchor ? targetAnchor.getAttribute("href") : null;
                data.push({
                    source: cells[0].textContent,
                    target: cells[1].textContent,
                    sourcePath: sourcePath,
                    targetPath: targetPath,
                    level: cells[2].textContent
                });
            }
        });
        return data;
    }

    function processNewData(newData) {
        var nodePaths = {};
        newData.forEach(d => {
            nodePaths[d.source] = d.sourcePath || null;
            nodePaths[d.target] = d.targetPath || null;
        });
        var newNodes = Array.from(new Set(newData.flatMap(d => [d.source, d.target])))
            .map(id => ({
                id,
                path: nodePaths[id]
            }));

        var newLinks = newData.map(d => ({ source: d.source, target: d.target }));
        return { newNodes, newLinks };
    }

    function filterTableAndGraph(tf, simulation, data) {
        var filteredData = parseFilteredTable(tf, data);
        var { newNodes, newLinks } = processNewData(filteredData);

        simulation.update({ newNodes: newNodes, newLinks: newLinks });
    }

    function createForceDirectedGraph(data, elementId) {
        var nodePaths = {};
        data.forEach(d => {
            nodePaths[d.source] = d.sourcePath || null;
            nodePaths[d.target] = d.targetPath || null;
        });

        var nodes = Array.from(new Set(data.flatMap(d => [d.source, d.target])))
            .map(id => ({
                id,
                path: nodePaths[id]
            }));

        var links = data.map(d => ({ source: d.source, target: d.target }));

        var tooltip = d3.select("body").append("div")
            .attr("class", "tooltip") // Add relevant classes for styling
            .style("opacity", 0);

        // Set up the dimensions of the graph
        var width = 800, height = 1000;

        var svg = d3.select(elementId).append("svg")
            .attr("width", width)
            .attr("height", height);

        // Create a force simulation
        linkDistance = Math.sqrt((width * height) / nodes.length);

        var simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(linkDistance))
            .force("charge", d3.forceManyBody().strength(-50))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .alphaDecay(0.02); // A lower value, adjust as needed

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
            .attr("r", function (d, i) {
                return i === 0 ? NODE_RADIUS + 5 : NODE_RADIUS;
            })
            .attr("fill", function (d, i) {
                return i === 0 ? Parent_Node_COLOR : NODE_COLOR;
            });

        // Apply tooltip on nodes
        node.on("mouseover", function (event, d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(d.id)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
            .on("mousemove", function (event) {
                tooltip.style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function (d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
            });

        // Apply links on nodes
        node.on("dblclick", function (event, d) {
            location.href = d.path;
        });

        // Define drag behavior
        var drag = d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);

        // Apply drag behavior to nodes
        node.call(drag);

        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            // Do not reset the fixed positions
            if (!event.active) simulation.alphaTarget(0);
        }

        // Update positions on each simulation 'tick'
        simulation.on("tick", () => {
            nodes.forEach(d => {
                d.x = Math.max(NODE_RADIUS, Math.min(width - NODE_RADIUS, d.x));
                d.y = Math.max(NODE_RADIUS, Math.min(height - NODE_RADIUS, d.y));
            });
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        });

        return Object.assign(svg.node(), {
            update({ newNodes, newLinks }) {
                const oldNodesMap = new Map(node.data().map(d => [d.id, d]));
                nodes = newNodes.map(d => Object.assign(oldNodesMap.get(d.id) || {}, d));

                // Update nodes with new data
                node = node.data(nodes, d => d.id)
                    .join(
                        enter => enter.append("circle")
                            .attr("r", function (d, i) {
                                return i === 0 ? NODE_RADIUS + 5 : NODE_RADIUS;
                            })
                            .attr("fill", function (d, i) {
                                return i === 0 ? Parent_Node_COLOR : NODE_COLOR;
                            }),
                        update => update,
                        exit => exit.remove()
                    );

                node.call(drag);

                // Apply tooltip on nodes
                node.on("mouseover", function (event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(d.id)
                        .style("left", (event.pageX) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                    .on("mousemove", function (event) {
                        tooltip.style("left", (event.pageX) + "px")
                            .style("top", (event.pageY - 28) + "px");
                    })
                    .on("mouseout", function (d) {
                        tooltip.transition()
                            .duration(500)
                            .style("opacity", 0);
                    });

                // Apply links on nodes
                node.on("dblclick", function (event, d) {
                    console.log("Node: " + d.id);
                    console.log(d);
                    console.log("Source Path: " + d.sourcePath);
                    location.href = d.path;
                });

                // Process new links
                const oldLinksMap = new Map(link.data().map(d => [`${d.source.id},${d.target.id}`, d]));
                links = newLinks.map(d => Object.assign(oldLinksMap.get(`${d.source.id},${d.target.id}`) || {}, d));

                // Update links with new data
                link = link.data(links, d => `${d.source.id},${d.target.id}`)
                    .join(
                        enter => enter.append("line")
                            .attr("stroke-width", d => Math.sqrt(d.value)),
                        update => update,
                        exit => exit.remove()
                    );

                // Restart the simulation with new data
                simulation.nodes(nodes);
                simulation.force("link").links(links);
                simulation.alpha(1).restart();
            }
        });
    }

    // Find all tables that have a th with the class .graph and generate Force-Directed Graphs
    document.querySelectorAll("table").forEach((table, index) => {
        var graphHeader = table.querySelector("th.graph");
        if (graphHeader) {
            var tf = new TableFilter(table, {
                base_path: "../../../../01_attachements/modules/tablefilter/",
                highlight_keywords: true,
                col_2: "checklist",
                col_widths: ["350px", "350px", "100px"],
                col_types: ["string", "string", "number"],
                grid_layout: false,
                responsive: false,
                watermark: ["Filter table ...", "Filter table ..."],
                auto_filter: {
                    delay: 100 //milliseconds
                },
                filters_row_index: 1,
                state: false,
                rows_counter: true,
                status_bar: true,
                themes: [{
                    name: "transparent",
                }],
                btn_reset: {
                    tooltip: "Reset",
                    toolbar_position: "right",
                },
                toolbar: true,
                extensions: [{
                    name: "sort",
                },
                {
                    name: 'filtersVisibility',
                    description: 'Sichtbarkeit der Filter',
                    toolbar_position: 'right',
                }],
            });

            tf.init();
            var data = parseTable(table);
            var graphId = "graph" + index;
            var div = document.createElement("div");
            div.id = graphId;
            table.parentNode.insertBefore(div, table);
            var simulation = createForceDirectedGraph(data, "#" + graphId);

            // Listen for table filtering events
            tf.emitter.on(['after-filtering'], function () {
                filterTableAndGraph(tf, simulation, data);
            });
        }
    });
});
