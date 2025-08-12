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
let currentMapView = 'country'; // 'country' or 'region'
let regionGeoData = null; // Aggregated GeoJSON for regions
let regionDataMap = {};   // Aggregated policy data for regions

// --- Declare geoData and policyData globally ---
let geoData = null;
let policyData = null;

// --- IMPORTANT: DEFINING REGIONS HERE ---
const regionDefinitions = {
    "North Africa": ["Algeria", "Egypt", "Libya", "Morocco", "Sudan", "Tunisia", "Western Sahara"],
    "West Africa": ["Benin", "Burkina Faso", "Cape Verde", "The Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Côte d'Ivoire", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Senegal", "Sierra Leone", "Togo"],
    "Central Africa": ["Burundi", "Cameroon", "Central African Republic", "Chad", "Democratic Republic of Congo", "Republic of Congo", "Equatorial Guinea", "Gabon", "São Tomé & Príncipe"],
    "East Africa": ["Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Mauritius", "Rwanda", "Seychelles", "Somalia", "South Sudan", "Tanzania", "Uganda"],
    "Southern Africa": ["Angola", "Botswana", "Eswatini", "Lesotho", "Malawi", "Mozambique", "Namibia", "South Africa", "Zambia", "Zimbabwe"],
};

// --- NEW: Color Scale for Regions ---
let regionColorScale; // Declare globally

// --- HELPER FUNCTION for single-select filter matching ---
const filterMatches = (itemValue, selectedFilterValue) => {
    if (selectedFilterValue === "all") {
        return true;
    }
    if (Array.isArray(itemValue)) {
        return itemValue.includes(selectedFilterValue);
    }
    return itemValue === selectedFilterValue;
};


// --- GLOBAL HELPER FUNCTION: getBadge ---
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

// --- NEW GLOBAL HELPER FUNCTION: createCardContainer ---
const createCardContainer = (parentSelection) => {
    return parentSelection.append("div")
        .style("background", "#ffffff")
        .style("border-radius", "12px")
        .style("box-shadow", "0 1px 4px rgba(0,0,0,0.1)")
        .style("padding", "1rem 1.25rem")
        .style("vertical-align", "top")
        .style("font-family", "'Segoe UI', Roboto, sans-serif")
        .style("border-left", "5px solid #f1b434")
        .style("box-sizing", "border-box") // Ensure padding/border included in width
        .style("flex-grow", "1") // Allow items to grow to fill space if there aren't enough for a full row
        .style("flex-shrink", "1") // Allow items to shrink if necessary to prevent overflow
        .style("flex-basis", "calc(33.33% - 1rem)") // Aim for 3 per row, accounting for gap
        .style("max-width", "calc(33.33% - 1rem)")
        .style("height", "400px"); 
};

//// --- NEW GLOBAL HELPER FUNCTION: createBarChartContainer ---
const createBarChartContainer = (parentSelection, titleText) => {
    const container = parentSelection.append("div")
        .style("background", "#ffffff")
        .style("border-radius", "12px")
        .style("box-shadow", "0 1px 4px rgba(0,0,0,0.1)")
        .style("padding", "1rem 1.25rem")
        .style("min-width", "450px") // Adjusted for charts
        .style("vertical-align", "top")
        .style("font-family", "'Segoe UI', Roboto, sans-serif")
        .style("border-left", "5px solid #f1b434")
        .style("box-sizing", "border-box")
        .style("flex-shrink", "0")
        .style("margin-bottom", "1rem"); // Add some bottom margin between charts

    container.append("h5")
        .style("margin-top", "0")
        .text(titleText);

    return container;
};


// Prepare Regional Data and GeoJSON 
function prepareRegionalData(allGeoData, allPolicyData) {
    // 1. Aggregate Policy Data
    Object.keys(regionDefinitions).forEach(regionName => {
        const countriesInRegion = regionDefinitions[regionName];
        const aggregatedRegionDetails = {
            "Government document": [],
            "Focus areas Raw": [], // <<< NEW: Store raw list for actual counts
            "Policy class Raw": [], // <<< NEW: Store raw list for actual counts
            "Focus areas": new Set(), // Still keep for unique list (for filters, general display)
            "Policy class": new Set(), // Still keep for unique list (for filters, general display)
            "action or strategy": new Set(),
            "Policy promotes youth employment": false,
            "Policy promotes women employment": false,
            "policy promotes employment of people with disabilities": false,
            "total_documents": 0,
            "countries": []
        };

        countriesInRegion.forEach(countryName => {
            const countryDetails = dataMap[countryName];
            if (countryDetails) {
                aggregatedRegionDetails["Government document"].push(...countryDetails["Government document"]);
                
                // --- CRITICAL CHANGE FOR COUNTING FOCUS AREAS ---
                if (countryDetails["Focus areas"]) {
                    aggregatedRegionDetails["Focus areas Raw"].push(...countryDetails["Focus areas"]); // Add all occurrences
                    countryDetails["Focus areas"].forEach(f => aggregatedRegionDetails["Focus areas"].add(f)); // Add to Set for unique list
                }
                
                // --- CRITICAL CHANGE FOR COUNTING POLICY CLASS ---
                if (countryDetails["Policy class"]) {
                    aggregatedRegionDetails["Policy class Raw"].push(...countryDetails["Policy class"]); // Add all occurrences
                    countryDetails["Policy class"].forEach(c => aggregatedRegionDetails["Policy class"].add(c)); // Add to Set for unique list
                }

                countryDetails["action or strategy"].forEach(a => aggregatedRegionDetails["action or strategy"].add(a));
                
                if (countryDetails["Policy promotes youth employment"] === "Yes") aggregatedRegionDetails["Policy promotes youth employment"] = true;
                if (countryDetails["Policy promotes women employment"] === "Yes") aggregatedRegionDetails["Policy promotes women employment"] = true;
                if (countryDetails["policy promotes employment of people with disabilities"] === "Yes") aggregatedRegionDetails["policy promotes employment of people with disabilities"] = true;
                
                // --- Use the unique count of "Government document" for total_documents ---
                aggregatedRegionDetails["total_documents"] = [...new Set(aggregatedRegionDetails["Government document"])].length;
                aggregatedRegionDetails["countries"].push(countryName);
            }
        });

        // Convert Sets back to Arrays for the unique lists
        aggregatedRegionDetails["Focus areas"] = Array.from(aggregatedRegionDetails["Focus areas"]);
        aggregatedRegionDetails["Policy class"] = Array.from(aggregatedRegionDetails["Policy class"]);
        
        // Convert action or strategy Set to Array
        aggregatedRegionDetails["action or strategy"] = Array.from(aggregatedRegionDetails["action or strategy"]);
        
        // Convert boolean flags to "Yes"/"No" strings
        aggregatedRegionDetails["Policy promotes youth employment"] = aggregatedRegionDetails["Policy promotes youth employment"] ? "Yes" : "No";
        aggregatedRegionDetails["Policy promotes women employment"] = aggregatedRegionDetails["Policy promotes women employment"] ? "Yes" : "No";
        aggregatedRegionDetails["policy promotes employment of people with disabilities"] = aggregatedRegionDetails["policy promotes employment of employment of people with disabilities"] ? "Yes" : "No";

        regionDataMap[regionName] = aggregatedRegionDetails;
    });

    // 2. Aggregate GeoJSON 
    if (allGeoData.type === "FeatureCollection" && allGeoData.features && typeof topojson !== 'undefined' && typeof topojson.topology === 'function') {
        const mergedFeatures = [];
        Object.keys(regionDefinitions).forEach(regionName => {
            const countriesInRegion = regionDefinitions[regionName];
            
            const countryFeatures = allGeoData.features.filter(f =>
                countriesInRegion.includes(f.properties.name) && f.geometry
            );
            
            if (countryFeatures.length > 0) {
                try {
                    const tempTopology = topojson.topology({ 
                        collection: { type: "FeatureCollection", features: countryFeatures } 
                    }); 
                    
                    if (tempTopology.objects && tempTopology.objects.collection && tempTopology.objects.collection.geometries) {
                        const mergedGeometry = topojson.merge(tempTopology, tempTopology.objects.collection.geometries);

                        mergedFeatures.push({
                            type: "Feature",
                            geometry: mergedGeometry,
                            properties: { name: regionName }
                        });
                    } else {
                        console.warn(`WARNING: Topology for region ${regionName} (Countries: ${countriesInRegion.join(', ')}) did not produce expected 'objects.collection.geometries' structure. Topology output:`, tempTopology);
                    }
                } catch (e) {
                    console.error(`ERROR during topojson.topology/merge for region ${regionName} (Countries: ${countriesInRegion.join(', ')}):`, e);
                }
            } else {
                console.warn(`WARNING: No valid GeoJSON features found for region ${regionName} to merge.`);
            }
        });
        regionGeoData = { type: "FeatureCollection", features: mergedFeatures };

        // --- NEW: Initialize the regionColorScale after regionDataMap is populated ---
        const totalDocumentCounts = Object.values(regionDataMap)
            .map(d => d.total_documents)
            .filter(count => count > 0); // Only consider regions with documents for the scale

        if (totalDocumentCounts.length > 0) {
            const minDocs = d3.min(totalDocumentCounts);
            const maxDocs = d3.max(totalDocumentCounts);

            regionColorScale = d3.scaleQuantize()
                .domain([minDocs, maxDocs])
                .range(["#fef0d9", "#fdcd8f", "#fc8d59", "#e34a33", "#b30000"]); // Example color range (light to dark red/orange)
        } else {
            // Fallback if no regions have documents
            regionColorScale = d3.scaleQuantize().domain([0, 1]).range(["#e5e7eb"]);
        }

    } else {
        console.warn("GeoData is not a GeoJSON FeatureCollection or topojson.topology function is missing. Regional shapes cannot be merged. Display might be affected.");
        regionGeoData = { type: "FeatureCollection", features: [] }; 
    }
}


function drawMap() {
    svg.selectAll("path").remove();

    let dataToDraw;
    let dataMapToUse;

    if (currentMapView === 'country') {
        dataToDraw = geoData.features;
        dataMapToUse = dataMap;
        d3.select("#focusFilter").property("disabled", false);
        d3.select("#classFilter").property("disabled", false);
    } else { // 'region' view
        dataToDraw = regionGeoData.features;
        dataMapToUse = regionDataMap;
        d3.select("#focusFilter").property("disabled", true);
        d3.select("#classFilter").property("disabled", true);
        d3.select("#focusFilter").property("value", "all");
        d3.select("#classFilter").property("value", "all");
        selectedFocus = "all";
        selectedClass = "all";
    }

    countryPaths = svg.selectAll("path")
        .data(dataToDraw, d => d.properties.name)
        .enter().append("path")
        .attr("class", "map-entity")
        // Initial fill will be set by updateMap based on view
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1)
        .attr("d", path)
        .on("mouseover", function(event, d) {
            const name = d.properties.name;
            const details = dataMapToUse[name];
            if (!details) return;

            // Store original fill and apply hover fill
            d3.select(this).attr("data-original-fill", d3.select(this).attr("fill"));
            d3.select(this).attr("fill", "#89560a"); 

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
                      .attr("transform", `translate(${centroidX * (1 - scaleFactor)}, ${centroidY * (1 - scaleFactor)}) scale(${scaleFactor})`);
                });

            let tooltipHtml = `<strong>${name}</strong><br/>`;

            if (currentMapView === 'country') {
                const allFocus = [...new Set(details["Focus areas"])];
                const allClasses = [...new Set(details["Policy class"])];
                const allDocs = details["Government document"];

                const matchedDocsCount = allDocs.filter((doc, i) =>
                    filterMatches(details["Focus areas"][i], selectedFocus) &&
                    filterMatches(details["Policy class"][i], selectedClass)
                ).length;

                tooltipHtml += `
                    <b>Matched Focus Area:</b> ${selectedFocus === "all" ? "<i>All</i>" : (allFocus.includes(selectedFocus) ? selectedFocus : "<i>None</i>")}<br/>
                    <b>Matched Policy Class:</b> ${selectedClass === "all" ? "<i>All</i>" : (allClasses.includes(selectedClass) ? selectedClass : "<i>None</i>")}<br/>
                    <b>Matched Actions:</b> ${matchedDocsCount}
                    <br/>
                    <b>Total Documents:</b> ${[...new Set(allDocs)].length}
                `;
            } else { // currentMapView === 'region'
                const displayedCountries = details.countries.join(', ');
                const displayedTotalDocs = [...new Set(details["Government document"])].length;

                tooltipHtml += `
                    <b>Countries:</b> ${displayedCountries}<br/>
                    <b>Total Documents:</b> ${displayedTotalDocs}
                    <br/>
                    <b>Top Policy Classes:</b> ${details["Policy class"].slice(0, 3).join(", ") || "<i>None</i>"}<br/>
                    <b>Top Focus Areas:</b> ${details["Focus areas"].slice(0, 3).join(", ") || "<i>None</i>"}
                `;
            }

            tooltip.transition().duration(200).style("opacity", 0.95);
            tooltip.html(tooltipHtml)
            .style("left", (event.pageX + 10) + "px")
            .style("top", (event.pageY - 40) + "px");

        })
        .on("mouseout", function(event, d) {
            // Restore original fill
            d3.select(this).attr("fill", d3.select(this).attr("data-original-fill"));

            const originalTransform = d3.select(this).attr("data-original-transform") || "";
            d3.select(this)
              .attr("stroke", "#ffffff")
              .attr("stroke-width", 1)
              .transition()
              .duration(100)
              .attr("transform", originalTransform);
            tooltip.transition().duration(300).style("opacity", 0);
        })
        .on("click", (event, d) => {
            const name = d.properties.name;
            const details = dataMapToUse[name];

            resetSidebarAndDetails(); 

            if (!details || details["Government document"].length === 0) {
                d3.select("#sidebar-title").text(`No Data for ${name}`);
                d3.select("#document-list").html("<p>No policy data available.</p>");
                return;
            }

            if (currentMapView === 'country') {
                // --- COUNTRY VIEW CLICK LOGIC ---
                d3.select("#sidebar-title").text(`Documents for ${name}`);
                const allDocs = details["Government document"];
                const focusList = details["Focus areas"];
                const classList = details["Policy class"];

                const matchedDocs = allDocs.filter((doc, i) =>
                    filterMatches(focusList[i], selectedFocus) && 
                    filterMatches(classList[i], selectedClass)
                );
                const uniqueDocs = [...new Set(matchedDocs)];

                const listContainer = d3.select("#document-list");
                if (uniqueDocs.length === 0) {
                    listContainer.append("p").text("No matching documents.");
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
                        .on("click", () => showDocDetails(doc, details, selectedFocus, selectedClass)); 
                    });

                }
            } else { // currentMapView === 'region'
                // --- REGION VIEW CLICK LOGIC ---
                d3.select("#sidebar-title").text(`Insights for ${name}`);
                d3.select("#document-list").html(""); 

                const regionSummaryContainer = d3.select("#document-list"); 
                regionSummaryContainer.append("p").html(`<b>Total Documents in Region:</b> ${[...new Set(details["Government document"])].length}`);
                regionSummaryContainer.append("p").html(`<b>Countries in Region:</b> ${details.countries.join(', ')}`);

                const regionalPolicyClassCounts = {}; 
                // Using "Policy class Raw" for correct counts
                details["Policy class Raw"].forEach(pc => {
                    regionalPolicyClassCounts[pc] = (regionalPolicyClassCounts[pc] || 0) + 1;
                });
                d3.select("#doc-title").text(`Regional Breakdown for ${name}`);
                d3.select("#doc-charts").html(""); 

                // Set the display for the flex container
                d3.select("#doc-charts")
                    .style("display", "flex")
                    .style("flex-wrap", "wrap")
                    .style("gap", "1rem");

                const regionalFocusAreaCounts = {};
                // Using "Focus areas Raw" for correct counts
                details["Focus areas Raw"].forEach(fa => {
                    regionalFocusAreaCounts[fa] = (regionalFocusAreaCounts[fa] || 0) + 1;
                });
                
                // Prepare data for charts (top 10, sorted)
                const topFocusAreas = Object.entries(regionalFocusAreaCounts)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10)
                    .map(([area, count]) => ({ label: area, value: count })); // Map to {label, value} objects

                const topPolicyClasses = Object.entries(regionalPolicyClassCounts)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 10)
                    .map(([policyClass, count]) => ({ label: policyClass, value: count })); // Map to {label, value} objects
                
                // Render the bar charts
                renderBarChart(d3.select("#doc-charts"), topFocusAreas, "Top Focus Areas");
                renderBarChart(d3.select("#doc-charts"), topPolicyClasses, "Top Policy Classes");
            }
        });
}


/**
 * Populates or updates the filter dropdowns based on the currently
 * selected filters (excluding the filter being updated).
 * @param {string} changedFilterId The ID of the filter that just changed (e.g., 'focusFilter'),
 * or null if initializing all filters.
 */
function updateFilterOptions(changedFilterId = null) {
    // Get current selections (before any changes are applied for this update cycle)
    const currentFocus = d3.select("#focusFilter").property("value");
    const currentClass = d3.select("#classFilter").property("value");

    let availableFocusAreas = new Set();
    let availablePolicyClasses = new Set();

    // Iterate through all policy data entries to find relevant options
    policyData.forEach(d => {
        // A country's data is relevant if its documents match the *other* filter's selection
        // For focus, check against currentClass. For class, check against currentFocus.

        if (d["Government document"] && Array.isArray(d["Government document"])) {
            d["Government document"].forEach((doc, i) => {
                const docFocus = d["Focus areas"] ? d["Focus areas"][i] : null;
                const docClass = d["Policy class"] ? d["Policy class"][i] : null;

                // Check if this specific document entry matches the other filter's selection
                const isFocusRelevant = (changedFilterId === 'focusFilter' || currentClass === 'all' || (docClass && filterMatches(docClass, currentClass)));
                const isClassRelevant = (changedFilterId === 'classFilter' || currentFocus === 'all' || (docFocus && filterMatches(docFocus, currentFocus)));

                if (isFocusRelevant && docFocus) {
                    if (Array.isArray(docFocus)) {
                        docFocus.forEach(f => availableFocusAreas.add(f));
                    } else {
                        availableFocusAreas.add(docFocus);
                    }
                }
                if (isClassRelevant && docClass) {
                     if (Array.isArray(docClass)) {
                        docClass.forEach(c => availablePolicyClasses.add(c));
                    } else {
                        availablePolicyClasses.add(docClass);
                    }
                }
            });
        }
    });

    // Populate Focus Areas filter
    const focusSelect = d3.select("#focusFilter");
    focusSelect.selectAll("option").remove(); // Clear existing options
    focusSelect.append("option").text("All").attr("value", "all");
    Array.from(availableFocusAreas).sort().forEach(f => {
        focusSelect.append("option").text(f).attr("value", f);
    });
    // Restore previous selection if it's still available, otherwise default to 'all'
    focusSelect.property("value", Array.from(availableFocusAreas).includes(currentFocus) ? currentFocus : "all");


    // Populate Policy Class filter
    const classSelect = d3.select("#classFilter");
    classSelect.selectAll("option").remove(); // Clear existing options
    classSelect.append("option").text("All").attr("value", "all");
    Array.from(availablePolicyClasses).sort().forEach(c => {
        classSelect.append("option").text(c).attr("value", c);
    });
    // Restore previous selection if it's still available, otherwise default to 'all'
    classSelect.property("value", Array.from(availablePolicyClasses).includes(currentClass) ? currentClass : "all");
}


// Fetch data and geo
Promise.all([
  d3.json("data/africa.geojson"),
  d3.json("data/africa_policy_data.json")
]).then(([fetchedGeoData, fetchedPolicyData]) => { 
  geoData = fetchedGeoData;
  policyData = fetchedPolicyData;

  policyData.forEach(d => dataMap[d.country] = d);

  // Initial population of filters (before any changes)
  updateFilterOptions(null); // Call with null to indicate initial load

  // Prepare regional data after country data is loaded
  prepareRegionalData(geoData, policyData);

  // --- Map View Switcher Logic ---
  d3.select("#view-country").on("click", function() {
      currentMapView = 'country';
      d3.selectAll("#map-view-switcher button").classed("active-view-btn", false);
      d3.select(this).classed("active-view-btn", true);
      resetSidebarAndDetails(); 
      drawMap(); 
      updateMap(); 
      updateFilterOptions(null); // Re-populate filters for country view
  });

  d3.select("#view-region").on("click", function() {
      currentMapView = 'region';
      d3.selectAll("#map-view-switcher button").classed("active-view-btn", false);
      d3.select(this).classed("active-view-btn", true);
      resetSidebarAndDetails(); 
      drawMap(); 
      updateMap(); 
      // Filters are disabled for region view, so no need to update options
  });

  // --- Filter change logic ---
  d3.select("#focusFilter").on("change", () => {
      selectedFocus = d3.select("#focusFilter").property("value"); 
      resetSidebarAndDetails(); 
      updateFilterOptions('focusFilter'); // Pass the ID of the changed filter
      updateMap(); 
  });
  d3.select("#classFilter").on("change", () => {
      selectedClass = d3.select("#classFilter").property("value");
      resetSidebarAndDetails(); 
      updateFilterOptions('classFilter'); // Pass the ID of the changed filter
      updateMap(); 
  });


  // Initial draw and update
  drawMap(); 
  updateMap(); 

}); 


// --- Reset Sidebar and Details Panel ---
function resetSidebarAndDetails() {
    d3.select("#sidebar-title").text(currentMapView === 'country' ? `Click a country` : `Click a region`);
    d3.select("#document-list").html("");
    d3.select("#doc-title").text("Select a document to see details");
    d3.select("#doc-charts").html("");
    d3.select("#class-chart").selectAll("*").remove(); 
    d3.select("#focus-chart").selectAll("*").remove(); 
}


// --- updateMap function to adapt to currentMapView ---
function updateMap() {
  let dataMapToUse = (currentMapView === 'country') ? dataMap : regionDataMap;
  let dataToDraw = (currentMapView === 'country') ? geoData.features : regionGeoData.features;

  svg.selectAll(".map-entity") 
    .data(dataToDraw, d => d.properties.name)
    .attr("fill", d => {
        const details = dataMapToUse[d.properties.name];
        // FIX 1: Check Government Document length for data presence
        if (!details || details["total_documents"] === 0) return "#e5e7eb"; // Gray for no data

        if (currentMapView === 'country') {
            // FIX 2: Iterate over Government Document to find matching documents
            const hasMatchingDocument = details["Government document"].some((doc, i) => {
                // Ensure the index 'i' is valid for associated arrays
                if (details["Focus areas"] && i < details["Focus areas"].length && 
                    details["Policy class"] && i < details["Policy class"].length) {
                    return filterMatches(details["Focus areas"][i], selectedFocus) &&
                           filterMatches(details["Policy class"][i], selectedClass);
                }
                return false; // If index is out of bounds for related arrays, no match
            });
            return hasMatchingDocument ? "#F1B434" : "#f0f0f0"; 
        } else {
            // --- NEW: Use regionColorScale for regions ---
            return regionColorScale(details.total_documents);
        }
    });
}

/**
 * Lists all unique actions or strategies associated with a specific document
 * for a given country.
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

// --- showDocDetails function (for individual documents in Country View) ---
function showDocDetails(docTitle, details, currentSelectedFocus, currentSelectedClass) {
  d3.select("#doc-title").text(docTitle);

  d3.select("#class-chart").selectAll("*").remove(); 
  d3.select("#focus-chart").selectAll("*").remove(); 

  const allGovDocs = details["Government document"];
  const allFocusAreas = details["Focus areas"];
  const allPolicyClasses = details["Policy class"];

  const rawIndices = allGovDocs
    .map((doc, i) => doc === docTitle ? i : -1)
    .filter(i => i !== -1);

  const filteredIndices = rawIndices.filter(i => {
    const focusMatch = filterMatches(allFocusAreas[i], currentSelectedFocus);
    const classMatch = filterMatches(allPolicyClasses[i], currentSelectedClass);
    return focusMatch && classMatch;
  });

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

  const chartArea = d3.select("#doc-charts");
  chartArea.html("");

  chartArea
    .style("display", "flex")
    .style("flex-wrap", "wrap")
    .style("align-items", "flex-start")
    .style("gap", "1rem")
    .style("margin-top", "1rem");

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

  Object.entries(classGroups).forEach(([policyClass, flags]) => {
    const container = createCardContainer(chartArea); // Use the helper for consistency
    // Removed: container.style("margin", "1rem 1rem 1rem 0"); // Handled by parent gap

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

    if (flags.actions.size > 0) {
    container.append("div")
        .style("margin-top", "1rem")
        .style("font-weight", "600")
        .style("color", "#475569")
        .text("Actions/Strategies:");
    const actionsList = container.append("ul")
        .style("list-style", "decimal")
        .style("margin", "0.5rem 0 0 15px")
        .style("padding-left", "25px")
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


function renderSocialTags(youth, women, disability) {
  const container = d3.select("#social-tags");
  container.html("");

  const getStatus = flags => flags.includes("Yes") ? "✅" : "❌";

  container.append("span").text(`Youth Employment: ${getStatus(youth)}`);
  container.append("span").text(`Women Employment: ${getStatus(women)}`);
  container.append("span").text(`Disability Inclusion: ${getStatus(disability)}`);
}

// --- NEW FUNCTION: renderBarChart ---
function renderBarChart(parentSelection, data, titleText) {
    // ADJUSTED MARGINS
    const margin = { top: 20, right: 30, bottom: 150, left: 100 }; // <--- Increased bottom margin (was 100)
    const width = 500 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const containerDiv = createBarChartContainer(parentSelection, titleText);

    const svgChart = containerDiv.append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // X scale (for categories/labels)
    const x = d3.scaleBand()
        .domain(data.map(d => d.label))
        .range([0, width])
        .padding(0.1);

    // Y scale (for values/counts)
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)]).nice()
        .range([height, 0]);

    // Draw bars
    svgChart.selectAll(".bar")
      .data(data)
      .enter().append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d.label))
        .attr("y", d => y(d.value))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d.value))
        .attr("fill", "#F1B434"); // Orange color

    // Add X-axis
    svgChart.append("g")
        .attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll("text")
        // ADJUSTED ROTATION AND POSITIONING FOR X-AXIS LABELS
        .attr("transform", "rotate(-60)") // <--- Increased rotation angle (was -45)
        .style("text-anchor", "end")
        .style("font-size", "0.9em") // <--- Slightly reduced font size for more space (was 0.95em)
        .style("font-weight", "bold")
        .attr("dx", "-.8em")
        .attr("dy", ".15em"); // Keep these, they usually work well with text-anchor: end

    // Add Y-axis
    svgChart.append("g")
        .attr("class", "y-axis")
        .call(d3.axisLeft(y).ticks(5)) // Adjust ticks as needed
        .selectAll("text")
        .style("font-size", "0.95em");

    // Add Y-axis label
    svgChart.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left + 20)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .style("font-size", "0.95em")
        .style("font-weight", "bold")
        .text("Number of Mentions");

    // Add value labels on top of bars
    svgChart.selectAll(".bar-label")
      .data(data)
      .enter().append("text")
        .attr("class", "bar-label")
        .attr("x", d => x(d.label) + x.bandwidth() / 2)
        .attr("y", d => y(d.value) - 5)
        .attr("text-anchor", "middle")
        .style("font-size", "0.95em") // Keep this font size as it's for the value
        .style("fill", "#475569")
        .text(d => d.value);
}