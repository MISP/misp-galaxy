document$.subscribe(function () {

    const NODE_RADIUS = 8;
    // const NODE_COLOR = "#69b3a2";
    const Parent_Node_COLOR = "#ff0000";


    function applyTableFilter(tf) {
        var valuesToSelect = ['1', '2', '3'];
        tf.setFilterValue(4, valuesToSelect);
        tf.filter();
    }

    function parseFilteredTable(tf, allData) {
        var data = [];
        tf.getFilteredData().forEach((row, i) => {
            sourcePath = allData[row[0] - 2].sourcePath;
            targetPath = allData[row[0] - 2].targetPath;
            data.push({
                source: row[1][0],
                sourcePath: sourcePath,
                sourceGalaxy: row[1][1],
                target: row[1][2],
                targetPath: targetPath,
                targetGalaxy: row[1][3],
                level: row[1][4]
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
                var targetAnchor = cells[2].querySelector("a");
                var targetPath = targetAnchor ? targetAnchor.getAttribute("href") : null;
                data.push({
                    source: cells[0].textContent,
                    sourceGalaxy: cells[1].textContent,
                    target: cells[2].textContent,
                    targetGalaxy: cells[3].textContent,
                    sourcePath: sourcePath,
                    targetPath: targetPath,
                    level: cells[4].textContent
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
                path: nodePaths[id],
                galaxy: newData.find(d => d.source === id) ? newData.find(d => d.source === id).sourceGalaxy : newData.find(d => d.target === id).targetGalaxy
            }));

        var newLinks = newData.map(d => ({ source: d.source, target: d.target }));
        return { newNodes, newLinks };
    }

    function filterTableAndGraph(tf, simulation, data) {
        var filteredData = parseFilteredTable(tf, data);
        var { newNodes, newLinks } = processNewData(filteredData);

        simulation.update({ newNodes: newNodes, newLinks: newLinks });
    }

    function extractNodePaths(data) {
        return data.reduce((acc, d) => ({
            ...acc,
            [d.source]: d.sourcePath || null,
            [d.target]: d.targetPath || null,
        }), {});
    }

    function defineColorScale(galaxies) {
        const colorScheme = [
            '#E63946', // Red
            '#F1FAEE', // Off White
            '#A8DADC', // Light Blue
            '#457B9D', // Medium Blue
            '#1D3557', // Dark Blue
            '#F4A261', // Sandy Brown
            '#2A9D8F', // Teal
            '#E9C46A', // Saffron
            '#F77F00', // Orange
            '#D62828', // Dark Red
            '#023E8A', // Royal Blue
            '#0077B6', // Light Sea Blue
            '#0096C7', // Sky Blue
            '#00B4D8', // Bright Sky Blue
            '#48CAE4', // Light Blue
            '#90E0EF', // Powder Blue
            '#ADE8F4', // Pale Cerulean
            '#CAF0F8', // Blithe Blue
            '#FFBA08', // Selective Yellow
            '#FFD60A'  // Naples Yellow
        ];
        return d3.scaleOrdinal(colorScheme)
            .domain(galaxies);
    }

    function initializeNodeInteractions(node, link, tooltip, simulation, links, Parent_Node, NODE_RADIUS) {
        // Mouseover event handler
        node.on("mouseover", function (event, d) {
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(d.id)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
            node.style("opacity", 0.1);
            link.style("opacity", 0.1);
            d3.select(this)
                .attr("r", parseFloat(d3.select(this).attr("r")) + 5)
                .style("opacity", 1);
            d3.selectAll(".legend-text.galaxy-" + d.galaxy.replace(/\s+/g, '-').replace(/[\s.]/g, '-'))
                .style("font-weight", "bold")
                .style("font-size", "14px");
            link.filter(l => l.source.id === d.id || l.target.id === d.id)
                .attr("stroke-width", 3)
                .style("opacity", 1);
            node.filter(n => n.id === d.id || links.some(l => (l.source.id === d.id && l.target.id === n.id) || (l.target.id === d.id && l.source.id === n.id)))
                .style("opacity", 1);
        })
            .on("mousemove", function (event) {
                tooltip.style("left", (event.pageX) + "px")
                    .style("top", (event.pageY - 28) + "px");
            })
            .on("mouseout", function (event, d) {
                tooltip.transition()
                    .duration(500)
                    .style("opacity", 0);
                node.style("opacity", 1);
                link.style("opacity", 1);
                d3.select(this).attr("r", d => d.id === Parent_Node.id ? NODE_RADIUS + 5 : NODE_RADIUS);
                d3.selectAll(".legend-text.galaxy-" + d.galaxy.replace(/\s+/g, '-').replace(/[\s.]/g, '-'))
                    .style("font-weight", "normal")
                    .style("font-size", "12px");
                link.filter(l => l.source.id === d.id || l.target.id === d.id)
                    .attr("stroke-width", 1);
                node.filter(n => n.id === d.id || links.some(l => (l.source.id === d.id && l.target.id === n.id) || (l.target.id === d.id && l.source.id === n.id)));
            })
            .on("dblclick", function (event, d) {
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
            if (!event.active) simulation.alphaTarget(0);
        }
    }



    function createGalaxyColorLegend(svg, width, galaxies, colorScale, node, link, tooltip) {
        // Prepare legend data
        const legendData = galaxies.map(galaxy => ({
            name: galaxy,
            color: colorScale(galaxy)
        }));

        const maxCharLength = 10; // Maximum number of characters to display in legend

        // Create legend
        const legend = svg.append("g")
            .attr("class", "legend")
            .attr("transform", "translate(" + (width - 100) + ",20)"); // Adjust position as needed

        // Add legend title
        legend.append("text")
            .attr("x", 0)
            .attr("y", -10)
            .style("font-size", "13px")
            .style("text-anchor", "start")
            .style("fill", "grey")
            .text("Galaxy Colors");

        // Add colored rectangles and text labels for each galaxy
        const legendItem = legend.selectAll(".legend-item")
            .data(legendData)
            .enter().append("g")
            .attr("class", "legend-item")
            .attr("transform", (d, i) => `translate(0, ${i * 20})`);

        legendItem.append("rect")
            .attr("width", 12)
            .attr("height", 12)
            .style("fill", d => d.color)
            .on("mouseover", mouseoverEffect)
            .on("mouseout", mouseoutEffect);

        legendItem.append("text")
            .attr("x", 24)
            .attr("y", 9)
            .attr("dy", "0.35em")
            .style("text-anchor", "start")
            .style("fill", "grey")
            .style("font-size", "12px")
            .attr("class", d => "legend-text galaxy-" + d.name.replace(/\s+/g, '-').replace(/[\s.]/g, '-'))
            .text(d => d.name.length > maxCharLength ? d.name.substring(0, maxCharLength) + "..." : d.name)
            .on("mouseover", mouseoverEffect)
            .on("mouseout", mouseoutEffect);

        function mouseoverEffect(event, d) {
            // Dim the opacity of all nodes and links
            node.style("opacity", 0.1);
            link.style("opacity", 0.1);

            // Highlight elements associated with the hovered galaxy
            svg.selectAll(".galaxy-" + d.name.replace(/\s+/g, '-').replace(/[\s.]/g, '-'))
                .each(function () {
                    d3.select(this).style("opacity", 1); // Increase opacity for related elements
                });

            // Show tooltip
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            tooltip.html(d.name)
                .style("left", (event.pageX) + "px")
                .style("top", (event.pageY - 28) + "px");
        }

        function mouseoutEffect(event, d) {
            // Restore the opacity of nodes and links
            node.style("opacity", 1);
            link.style("opacity", 1);

            // Hide tooltip
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        }

    }


    function createForceDirectedGraph(data, elementId) {
        const nodePaths = extractNodePaths(data);

        // // Extract unique galaxy names from data
        const galaxies = Array.from(new Set(data.flatMap(d => [d.sourceGalaxy, d.targetGalaxy])));
        const colorScale = defineColorScale(data);

        var nodes = Array.from(new Set(data.flatMap(d => [d.source, d.target])))
            .map(id => ({
                id,
                path: nodePaths[id],
                galaxy: data.find(d => d.source === id) ? data.find(d => d.source === id).sourceGalaxy : data.find(d => d.target === id).targetGalaxy
            }));

        let header = document.querySelector('h1').textContent;
        const Parent_Node = nodes.find(node => node.id.includes(header));

        var links = data.map(d => ({ source: d.source, target: d.target }));

        var tooltip = d3.select("body").append("div")
            .attr("class", "tooltip") // Add relevant classes for styling
            .style("opacity", 0);

        // Set up the dimensions of the graph
        var width = document.querySelector('.md-content__inner').offsetWidth;
        var height = width;

        var svg = d3.select("div#container")
            .append("svg")
            .attr("preserveAspectRatio", "xMinYMin meet")
            .attr("viewBox", "0 0 " + width + " " + height)
            .classed("svg-content", true);

        // Create a force simulation
        linkDistance = Math.sqrt((width * height) / nodes.length);
        var simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(linkDistance))
            .force("charge", d3.forceManyBody().strength(-70))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .alphaDecay(0.05); // A lower value, adjust as needed

        // Create links
        var link = svg.append("g")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("stroke-width", 1);

        // Create nodes
        var node = svg.append("g")
            .attr("stroke", "#D3D3D3")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("r", function (d, i) {
                return d.id === Parent_Node.id ? NODE_RADIUS + 5 : NODE_RADIUS;
            })
            .attr("fill", function (d, i) {
                return d.id === Parent_Node.id ? Parent_Node_COLOR : colorScale(d.galaxy);
            })
            .attr("class", d => "node galaxy-" + d.galaxy.replace(/\s+/g, '-').replace(/[\s.]/g, '-'));

        initializeNodeInteractions(node, link, tooltip, simulation, links, Parent_Node, NODE_RADIUS);
        createGalaxyColorLegend(svg, width, galaxies, colorScale, node, link, tooltip);

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
                                return d.id === Parent_Node.id ? NODE_RADIUS + 5 : NODE_RADIUS;
                            })
                            .attr("fill", function (d, i) {
                                return d.id === Parent_Node.id ? Parent_Node_COLOR : colorScale(d.galaxy);
                            })
                            .attr("class", d => "node galaxy-" + d.galaxy.replace(/\s+/g, '-').replace(/[\s.]/g, '-')),
                        update => update,
                        exit => exit.remove()
                    );

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

                initializeNodeInteractions(node, link, tooltip, simulation, links, Parent_Node, NODE_RADIUS);
                createGalaxyColorLegend(svg, width, galaxies, colorScale, node, link, tooltip);

                // Restart the simulation with new data
                simulation.nodes(nodes);
                simulation.force("link").links(links);
                linkDistance = Math.sqrt((width * height) / nodes.length);
                simulation.force("link").distance(linkDistance);
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
                col_1: "checklist",
                col_3: "checklist",
                col_4: "checklist",
                col_types: ["string", "string", "string", "string", "number"],
                grid_layout: false,
                responsive: true,
                watermark: ["Filter table ...", "Filter table ...", "Filter table ...", "Filter table ..."],
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
            var allData = parseTable(table);
            if (allData.length > 1000) {
                applyTableFilter(tf);
                data = parseFilteredTable(tf, allData);
            } else {
                data = allData;
            }
            var graphId = "container";
            var div = document.createElement("div");
            // div.id = graphId;
            div.id = graphId;
            div.className = "svg-container";
            table.parentNode.insertBefore(div, table);
            var simulation = createForceDirectedGraph(data, "#" + graphId);

            // Listen for table filtering events
            tf.emitter.on(['after-filtering'], function () {
                filterTableAndGraph(tf, simulation, allData);
            });
        }
    });
});
