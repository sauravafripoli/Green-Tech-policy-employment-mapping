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
    "West Africa": ["Benin", "Burkina Faso", "Cabo Verde", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Côte d'Ivoire", "Liberia", "Mali", "Mauritania", "Niger", "Nigeria", "Senegal", "Sierra Leone", "Togo"],
    "Central Africa": ["Burundi", "Cameroon", "Central African Republic", "Chad", "Democratic Republic of Congo", "Republic of Congo", "Equatorial Guinea", "Gabon", "Sao Tome and Principe"],
    "East Africa": ["Comoros", "Djibouti", "Eritrea", "Ethiopia", "Kenya", "Madagascar", "Mauritius", "Rwanda", "Seychelles", "Somalia", "South Sudan", "Tanzania", "Uganda"],
    "Southern Africa": ["Angola", "Botswana", "Eswatini", "Lesotho", "Malawi", "Mozambique", "Namibia", "South Africa", "Zambia", "Zimbabwe"],
};


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
        .style("width", "240px") // Fixed width for cards
        .style("vertical-align", "top") // To align cards at the top in a flex container
        .style("font-family", "'Segoe UI', Roboto, sans-serif")
        .style("border-left", "5px solid #f1b434") // <<< FIXED COLOR TO #f1b434
        .style("box-sizing", "border-box") // Ensure padding/border included in width
        .style("flex-shrink", "0"); // Prevent cards from shrinking in a flex container
};


// Prepare Regional Data and GeoJSON 
function prepareRegionalData(allGeoData, allPolicyData) {
    // 1. Aggregate Policy Data
    Object.keys(regionDefinitions).forEach(regionName => {
        const countriesInRegion = regionDefinitions[regionName];
        const aggregatedRegionDetails = {
            "Government document": [],
            "Focus areas": new Set(),
            "Policy class": new Set(),
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
                countryDetails["Focus areas"].forEach(f => aggregatedRegionDetails["Focus areas"].add(f));
                countryDetails["Policy class"].forEach(c => aggregatedRegionDetails["Policy class"].add(c));
                countryDetails["action or strategy"].forEach(a => aggregatedRegionDetails["action or strategy"].add(a));
                
                if (countryDetails["Policy promotes youth employment"] === "Yes") aggregatedRegionDetails["Policy promotes youth employment"] = true;
                if (countryDetails["Policy promotes women employment"] === "Yes") aggregatedRegionDetails["Policy promotes women employment"] = true;
                if (countryDetails["policy promotes employment of people with disabilities"] === "Yes") aggregatedRegionDetails["policy promotes employment of people with disabilities"] = true;
                
                aggregatedRegionDetails["total_documents"] += countryDetails["Government document"].length;
                aggregatedRegionDetails["countries"].push(countryName);
            }
        });

        // Convert Sets back to Arrays and boolean flags to "Yes"/"No"
        aggregatedRegionDetails["Focus areas"] = Array.from(aggregatedRegionDetails["Focus areas"]);
        aggregatedRegionDetails["Policy class"] = Array.from(aggregatedRegionDetails["Policy class"]);
        aggregatedRegionDetails["action or strategy"] = Array.from(aggregatedRegionDetails["action or strategy"]);
        
        aggregatedRegionDetails["Policy promotes youth employment"] = aggregatedRegionDetails["Policy promotes youth employment"] ? "Yes" : "No";
        aggregatedRegionDetails["Policy promotes women employment"] = aggregatedRegionDetails["Policy promotes women employment"] ? "Yes" : "No";
        aggregatedRegionDetails["policy promotes employment of people with disabilities"] = aggregatedRegionDetails["policy promotes employment of people with disabilities"] ? "Yes" : "No";

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
        .attr("fill", d => dataMapToUse[d.properties.name] && dataMapToUse[d.properties.name]["Government document"].length > 0 ? "#9fa8da" : "#e5e7eb")
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
                details["Policy class"].forEach(pc => {
                    regionalPolicyClassCounts[pc] = (regionalPolicyClassCounts[pc] || 0) + 1;
                });
                d3.select("#doc-title").text(`Regional Breakdown for ${name}`);
                d3.select("#doc-charts").html(""); 

                const regionalFocusAreaCounts = {};
                details["Focus areas"].forEach(fa => {
                    regionalFocusAreaCounts[fa] = (regionalFocusAreaCounts[fa] || 0) + 1;
                });

                // --- Use createCardContainer for Top Focus Areas ---
                const focusAreaCard = createCardContainer(d3.select("#doc-charts"));
                focusAreaCard.append("h5")
                    .style("margin-top", "0").text("Top Focus Areas:"); 
                const focusAreaList = focusAreaCard.append("ul")
                    .style("list-style-type", "none")
                    .style("padding-left", "0")
                    .style("word-break", "break-word"); // Added for list items
                Object.entries(regionalFocusAreaCounts)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5)
                    .forEach(([area, count]) => {
                        focusAreaList.append("li").text(`${area} (${count} documents)`);
                    });

                // --- Use createCardContainer for Top Policy Classes ---
                const policyClassCard = createCardContainer(d3.select("#doc-charts"));
                policyClassCard.append("h5")
                    .style("margin-top", "0").text("Top Policy Classes:");
                const policyClassList = policyClassCard.append("ul")
                    .style("list-style-type", "none")
                    .style("padding-left", "0")
                    .style("word-break", "break-word"); // Added for list items
                
                Object.entries(regionalPolicyClassCounts)
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 5)
                    .forEach(([policyClass, count]) => {
                        policyClassList.append("li").text(`${policyClass} (${count} documents)`);
                    });
            }
        });
}


// Fetch data and geo
Promise.all([
  d3.json("/geo"),
  d3.json("/data")
]).then(([fetchedGeoData, fetchedPolicyData]) => { 
  geoData = fetchedGeoData;
  policyData = fetchedPolicyData;

  policyData.forEach(d => dataMap[d.country] = d);

  const focusSet = new Set();
  const classSet = new Set();
  policyData.forEach(d => {
    if (d["Focus areas"]) d["Focus areas"].forEach(f => focusSet.add(f));
    if (d["Policy class"]) d["Policy class"].forEach(c => classSet.add(c));
  });

  d3.select("#focusFilter").append("option").text("All").attr("value", "all");
  Array.from(focusSet).sort().forEach(f => {
    d3.select("#focusFilter").append("option").text(f).attr("value", f);
  });
  
  d3.select("#classFilter").append("option").text("All").attr("value", "all");
   Array.from(classSet).sort().forEach(c => {
    d3.select("#classFilter").append("option").text(c).attr("value", c);
  });

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
  });

  d3.select("#view-region").on("click", function() {
      currentMapView = 'region';
      d3.selectAll("#map-view-switcher button").classed("active-view-btn", false);
      d3.select(this).classed("active-view-btn", true);
      resetSidebarAndDetails(); 
      drawMap(); 
      updateMap(); 
  });

  // --- Filter change logic ---
  d3.selectAll("#focusFilter, #classFilter").on("change", () => {
      selectedFocus = d3.select("#focusFilter").property("value"); 
      selectedClass = d3.select("#classFilter").property("value");
      resetSidebarAndDetails(); 
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
        if (!details || details["Government document"].length === 0) return "#e5e7eb";

        if (currentMapView === 'country') {
            // FIX 2: Iterate over Government Document to find matching documents
            const hasMatchingDocument = details["Government document"].some((doc, i) => {
                // Ensure the index 'i' is valid for associated arrays
                if (i < details["Focus areas"].length && i < details["Policy class"].length) {
                    return filterMatches(details["Focus areas"][i], selectedFocus) &&
                           filterMatches(details["Policy class"][i], selectedClass);
                }
                return false; // If index is out of bounds for related arrays, no match
            });
            return hasMatchingDocument ? "#F1B434" : "#f0f0f0"; 
        } else {
            return "#F1B434"; // Regions with data are always colored orange (as per previous consensus)
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