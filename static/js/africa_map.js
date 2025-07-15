const width = 960, height = 600;

const svg = d3.select("#map")
  .append("svg")
  .attr("width", width)
  .attr("height", height);
  
const projection = d3.geoMercator()
  .center([20, 0])
  .scale(400)
  .translate([width / 2, height / 2]);

const path = d3.geoPath().projection(projection);

const tooltip = d3.select("body").append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);

let countryPaths, dataMap = {}, selectedFocus = "all", selectedClass = "all";

// Fetch data and geo
Promise.all([
  d3.json("/geo"),
  d3.json("/data")
]).then(([geoData, policyData]) => { 

  policyData.forEach(d => dataMap[d.country] = d);

  // Extract unique focus areas and policy classes
  const focusSet = new Set();
  const classSet = new Set();
  policyData.forEach(d => {
    d["Focus areas"].forEach(f => focusSet.add(f));
    d["Policy class"].forEach(c => classSet.add(c));
  });

  // Populate dropdowns
  focusSet.forEach(f => {
    d3.select("#focusFilter").append("option").text(f).attr("value", f);
  });
  classSet.forEach(c => {
    d3.select("#classFilter").append("option").text(c).attr("value", c);
  });

  // Draw countries
  countryPaths = svg.selectAll("path")
    .data(geoData.features)
    .enter().append("path")
    .attr("class", "country")
    .attr("fill", d => dataMap[d.properties.name] ? "#9fa8da" : "#e5e7eb")
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1)
    .attr("d", path)
    .on("mouseover", function(event, d) {
      const countryName = d.properties.name;
      const details = dataMap[countryName];
      if (!details) return;

      // --- Start Zoom on Hover Changes ---
      const originalTransform = d3.select(this).attr("transform") || "";

      d3.select(this)
        .attr("stroke", "#374151")
        .attr("stroke-width", 1.5)
        .each(function() { 
          const bbox = this.getBBox();
          const centroidX = bbox.x + bbox.width / 2;
          const centroidY = bbox.y + bbox.height / 2;
          const scaleFactor = 1.05;

          d3.select(this)
            .transition()
            .duration(100)
            .attr("transform", `translate(${centroidX * (1 - scaleFactor)}, ${centroidY * (1 - scaleFactor)}) scale(${scaleFactor})`)
            .attr("data-original-transform", originalTransform);
        });
      // --- End Zoom on Hover Changes ---


      const allFocus = [...new Set(details["Focus areas"])];
      const allClasses = [...new Set(details["Policy class"])];
      const allDocs = details["Government document"];

      const matchesFocus = (fa) => selectedFocus === "all" || fa === selectedFocus;
      const matchesClass = (pc) => selectedClass === "all" || pc === selectedClass;

      const matchedDocs = allDocs.filter((doc, i) =>
        matchesFocus(details["Focus areas"][i]) &&
        matchesClass(details["Policy class"][i])
      );

      const uniqueMatchedDocs = [...new Set(matchedDocs)];


      tooltip.transition().duration(200).style("opacity", 0.95);
      tooltip.html(`
        <strong>${countryName}</strong><br/>

        <b>Matched Focus Area:</b> ${
          selectedFocus === "all"
            ? "<i>All</i>"
            : allFocus.includes(selectedFocus)
              ? selectedFocus
              : "<i>None</i>"
        }<br/>

        <b>Matched Policy Class:</b> ${
          selectedClass === "all"
            ? "<i>All</i>"
            : allClasses.includes(selectedClass)
              ? selectedClass
              : "<i>None</i>"
        }<br/>

        <b>Matched Documents:</b> ${uniqueMatchedDocs.length}
        ${
          uniqueMatchedDocs.length > 0
            ? `<ul style="margin:4px 0 0 15px;">
                ${uniqueMatchedDocs.slice(0, 5).map(d => `<li>${d}</li>`).join("")}
                ${uniqueMatchedDocs.length > 5 ? "<li>...</li>" : ""}
              </ul>`
            : ""
        }

        <b>Total Documents:</b> ${allDocs.length}
      `)
      .style("left", (event.pageX + 10) + "px")
      .style("top", (event.pageY - 40) + "px");


    })
  .on("mouseout", function(event, d) {
    // --- Start Zoom on Hover Reset Changes ---
    const originalTransform = d3.select(this).attr("data-original-transform") || "";

    d3.select(this)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1)
      .transition()
      .duration(100)
      .attr("transform", originalTransform);
    // --- End Zoom on Hover Reset Changes ---

    tooltip.transition().duration(300).style("opacity", 0);
  })
  .on("click", (event, d) => {
    const countryName = d.properties.name;
    const details = dataMap[countryName];
    if (!details) {
      d3.select("#sidebar-title").text(`Documents for ${countryName} (No Data)`);
      d3.select("#document-list").html("<p>No policy data available for this country.</p>");
      d3.select("#doc-title").text("Select a document to see details");
      d3.select("#doc-charts").html("");
      // Also clear the policy class chart
      d3.select("#class-chart").selectAll("*").remove(); 
      return;
    }

    const allDocs = details["Government document"];
    const focusList = details["Focus areas"];
    const classList = details["Policy class"];

    const matchesFocus = (fa) => selectedFocus === "all" || fa === selectedFocus;
    const matchesClass = (pc) => selectedClass === "all" || pc === selectedClass;

    // Step 1: Filter matched documents based on filters
    const matchedDocs = allDocs.filter((doc, i) =>
        matchesFocus(focusList[i]) && matchesClass(classList[i])
    );

    // Step 2: Remove duplicates
    const uniqueDocs = [...new Set(matchedDocs)];

    // Step 3: Update sidebar
    d3.select("#sidebar-title").text(`Documents for ${countryName}`);
    const listContainer = d3.select("#document-list");
    listContainer.html("");

    if (uniqueDocs.length === 0) {
        listContainer.append("p").text("No matching documents.");
        d3.select("#doc-title").text("Select a document to see details");
        d3.select("#doc-charts").html("");
        // Also clear the policy class chart
        d3.select("#class-chart").selectAll("*").remove();
    } else {
        listContainer.append("p")
        .style("margin-bottom", "0.5rem")
        .style("font-weight", "bold")
        .text(`${uniqueDocs.length} unique matching document${uniqueDocs.length > 1 ? "s" : ""}:`);

        const ul = listContainer.append("ul");
        uniqueDocs.forEach(doc => {
        ul.append("li")
        .text(doc)
        .style("cursor", "pointer")
        // Pass selected filters to showDocDetails for filtering cards
        .on("click", () => showDocDetails(doc, details, selectedFocus, selectedClass)); 
        });

        // --- Aggregate data for renderPolicyClassChart based on matchedDocs ---
        const policyClassCounts = {};
        details["Government document"].forEach((doc, i) => {
            if (uniqueDocs.includes(doc)) { // Only count if this document is in the unique, filtered set
                const pc = details["Policy class"][i];
                if (pc) {
                    policyClassCounts[pc] = (policyClassCounts[pc] || 0) + 1;
                }
            }
        });
        
        renderPolicyClassChart(policyClassCounts); // Call the chart function with the aggregated data
    }
  });


  // --- Filter change logic ---
  d3.selectAll("#focusFilter, #classFilter").on("change", () => {
      selectedFocus = d3.select("#focusFilter").property("value");
      selectedClass = d3.select("#classFilter").property("value");
      updateMap();
  });

  updateMap(); // Initial map update after data load

}); // End of Promise.all().then() block


function updateMap() {
  countryPaths.attr("fill", d => {
    const details = dataMap[d.properties.name];
    if (!details) return "#e5e7eb";

    const matchesFocus = selectedFocus === "all" || details["Focus areas"].includes(selectedFocus);
    const matchesClass = selectedClass === "all" || details["Policy class"].includes(selectedClass);

    return (matchesFocus && matchesClass) ? "#F1B434" : "#f0f0f0";
  });
}

/**
 * Lists all unique actions or strategies associated with a specific document
 * for a given country.
 *  'action or strategy' is the exact field name in the JSON data.
 */
function getUniqueActionsForDocument(docTitle, countryDetails) {
  const uniqueActions = new Set();
  const allDocs = countryDetails["Government document"];
  const allActions = countryDetails["action or strategy"]; 

  if (!allActions || !Array.isArray(allActions) || !allDocs || !Array.isArray(allDocs)) {
      console.warn("getUniqueActionsForDocument: Required 'action or strategy' or 'Government document' field is missing or not an array for this country.");
      return [];
  }

  allDocs.forEach((doc, i) => {
    if (doc === docTitle && i < allActions.length && allActions[i] !== undefined && allActions[i] !== null) {
      uniqueActions.add(allActions[i]);
    }
  });
  
  return Array.from(uniqueActions);
}

// --- showDocDetails function ---
function showDocDetails(docTitle, details, currentSelectedFocus, currentSelectedClass) {
  d3.select("#doc-title").text(docTitle);

  const allGovDocs = details["Government document"];
  const allFocusAreas = details["Focus areas"];
  const allPolicyClasses = details["Policy class"];

  // Find all original indices where this specific document appears
  const rawIndices = allGovDocs
    .map((doc, i) => doc === docTitle ? i : -1)
    .filter(i => i !== -1);

  // Filter these indices based on the active global filters (currentSelectedFocus, currentSelectedClass)
  const filteredIndices = rawIndices.filter(i => {
    const focusMatch = currentSelectedFocus === "all" || allFocusAreas[i] === currentSelectedFocus;
    const classMatch = currentSelectedClass === "all" || allPolicyClasses[i] === currentSelectedClass;
    return focusMatch && classMatch;
  });

  // Group rows by policy class (only for the filtered indices)
  const classGroups = {};
  filteredIndices.forEach(i => { 
    const cls = allPolicyClasses[i];
    if (!classGroups[cls]) {
      classGroups[cls] = {
        youth: [],
        women: [],
        disability: [],
        actions: new Set()
      };
    }

    classGroups[cls].youth.push(details["Policy promotes youth employment"][i]);
    classGroups[cls].women.push(details["Policy promotes women employment"][i]);
    classGroups[cls].disability.push(details["policy promotes employment of people with disabilities"][i]);

    const actionOrStrategyData = details["action or strategy"];
    if (actionOrStrategyData && Array.isArray(actionOrStrategyData) && actionOrStrategyData[i] !== undefined && actionOrStrategyData[i] !== null) {
        classGroups[cls].actions.add(actionOrStrategyData[i]);
    }
  });

  // Clear previous output
  const chartArea = d3.select("#doc-charts");
  chartArea.html("");

  // Flex container
  chartArea
    .style("display", "flex")
    .style("flex-wrap", "wrap")
    .style("align-items", "flex-start")
    .style("gap", "1rem")
    .style("margin-top", "1rem");

  // Utility for badge markup
  const getBadge = (label, hasYes) => {
    return `<span style="
      background: ${hasYes ? '#dcfce7' : '#fee2e2'};
      color: ${hasYes ? '#15803d' : '#b91c1c'};
      font-weight: 500;
      padding: 4px 10px;
      border-radius: 16px;
      margin: 4px 6px 0 0;
      display: inline-block;
      font-size: 0.85rem;
      box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05);
    ">${label}: ${hasYes ? '✔️' : '❌'}</span>`;
  };

  const hasYes = arr => arr.some(v => v === "Yes");

  // Render each policy class block
  Object.entries(classGroups).forEach(([policyClass, flags]) => {
    const container = chartArea.append("div")
      .style("background", "#ffffff")
      .style("border-radius", "12px")
      .style("box-shadow", "0 1px 4px rgba(0,0,0,0.1)")
      .style("padding", "1rem 1.25rem")
      .style("margin", "1rem 1rem 1rem 0")
      .style("display", "inline-block")
      .style("width", "240px")
      .style("vertical-align", "top")
      .style("font-family", "'Segoe UI', Roboto, sans-serif")
      .style("border-left", "5px solid #f1b434"); // Consistent accent color

    container.append("h4")
      .style("margin", "0 0 0.75rem 0")
      .style("font-size", "1.05rem")
      .style("color", "#1f2937")
      .style("font-weight", "600")
      .text(policyClass);

    container.html(container.html() + `
      ${getBadge("Youth", hasYes(flags.youth))}
      ${getBadge("Women", hasYes(flags.women))}
      ${getBadge("Disability", hasYes(flags.disability))}
    `);

    // --- Display unique actions/strategies for this policy class group ---
    if (flags.actions.size > 0) {
    container.append("div")
        .style("margin-top", "1rem")
        .style("font-weight", "600")
        .style("color", "#475569")
        .text("Actions/Strategies:");
    const actionsList = container.append("ul")
        .style("list-style", "decimal")
        .style("margin", "0.5rem 0 0 15px")
        .style("padding-left", "25px") // Added padding for numbers
        .style("max-height", "120px")
        .style("overflow-y", "auto"); 
    Array.from(flags.actions).forEach(action => {
        actionsList.append("li")
            .style("font-size", "0.9rem")
            .style("color", "#475569")
            .text(action);
      });
    }
  });
}


function renderPolicyClassChart(data) {
  const svg = d3.select("#class-chart");
  svg.selectAll("*").remove();

  const width = +svg.attr("width");
  const height = +svg.attr("height");
  const radius = Math.min(width, height) / 2;

  const pie = d3.pie().value(d => d[1]);
  const arc = d3.arc().innerRadius(40).outerRadius(radius - 10);

  const color = d3.scaleOrdinal(d3.schemeSet2);

  const g = svg.append("g")
    .attr("transform", `translate(${width/2}, ${height/2})`);

  const arcs = g.selectAll("path")
    .data(pie(Object.entries(data)))
    .enter().append("path")
    .attr("d", arc)
    .attr("fill", (d, i) => color(i))
    .append("title")
    .text(d => `${d.data[0]}: ${d.data[1]}`);
}

function renderSocialTags(youth, women, disability) {
  const container = d3.select("#social-tags");
  container.html("");

  const getStatus = flags => flags.includes("Yes") ? "✅" : "❌";

  container.append("span").text(`Youth Employment: ${getStatus(youth)}`);
  container.append("span").text(`Women Employment: ${getStatus(women)}`);
  container.append("span").text(`Disability Inclusion: ${getStatus(disability)}`);
}