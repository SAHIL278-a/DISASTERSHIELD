(() => {
  "use strict";

  // 1. Initialize the Leaflet map FIRST
  const map = L.map("map").setView([11.6643, 78.1460], 8);

  // 2. Add base map tiles
 const tileLayer = L.tileLayer(
  "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
  {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  }
);

tileLayer.addTo(map);

  // 3. Create a separate layer for alert markers
  const markers = L.layerGroup().addTo(map);

  // 4. Get HTML elements
  const statusEl = document.getElementById("status");
  const listEl = document.getElementById("alertList");
  const locationEl = document.getElementById("locationFilter");
  const typeEl = document.getElementById("typeFilter");
  const refreshBtn = document.getElementById("refreshBtn");
  const backBtn = document.getElementById("backBtn");

  // Stop safely if required HTML elements are missing
  if (
    !statusEl ||
    !listEl ||
    !locationEl ||
    !typeEl ||
    !refreshBtn ||
    !backBtn
  ) {
    console.error("DisasterShield: Required HTML elements are missing.");
    return;
  }

  // 5. State and cache
  let alerts = [];
  const geocodeCache = new Map();
  let busy = false;

  // 6. Safely escape text before inserting popup HTML
  function safe(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;"
    })[char]);
  }

  // 7. Detect disaster category from alert text
  function category(alert) {
    const text = `${alert.title || ""} ${alert.description || ""}`
      .toLowerCase();

    if (/flood|inundat|water level/.test(text)) return "Flood";
    if (/cyclone|cyclonic/.test(text)) return "Cyclone";
    if (/thunderstorm|lightning/.test(text)) return "Thunderstorm";
    if (/landslide/.test(text)) return "Landslide";
    if (/earthquake|seismic/.test(text)) return "Earthquake";
    if (/heatwave|heat wave|hot weather/.test(text)) return "Heat";
    if (/wind|gust/.test(text)) return "Wind";
    if (/rain|rainfall|precipitation/.test(text)) return "Rain";

    return "Other";
  }

  // 8. Estimate display severity from wording only
  function severity(alert) {
    const text = `${alert.title || ""} ${alert.description || ""}`
      .toLowerCase();

    if (
      /extremely severe|very severe|red alert|evacuat|life.?threatening|critical/.test(text)
    ) {
      return "CRITICAL";
    }

    if (
      /severe|orange alert|danger|flash flood|major flooding/.test(text)
    ) {
      return "HIGH";
    }

    if (
      /moderate|yellow alert|heavy rain|strong wind/.test(text)
    ) {
      return "MODERATE";
    }

    return "LOW";
  }

  const colors = {
    LOW: "#22c55e",
    MODERATE: "#eab308",
    HIGH: "#f97316",
    CRITICAL: "#ef4444"
  };

  // 9. Build searchable alert text
  function alertText(alert) {
    return [
      alert.location || "",
      alert.title || "",
      alert.description || ""
    ].join(" ");
  }

  // 10. Recognize known place names
  function place(alert) {
    const pattern =
      /\b(Salem|Namakkal|Erode|Coimbatore|Chennai|Madurai|Thanjavur|Tiruchirappalli|Tiruchy|Tamil Nadu|Kerala|Karnataka|Andhra Pradesh|Telangana|Maharashtra|Odisha|Gujarat|Assam|Bihar|West Bengal|Uttar Pradesh|Himachal Pradesh|Uttarakhand|Rajasthan|Delhi)\b/i;

    const match = alertText(alert).match(pattern);
    return match ? match[0] : "";
  }

  // 11. Look up coordinates using Nominatim
  async function geocode(placeName) {
    const key = placeName.toLowerCase();

    if (geocodeCache.has(key)) {
      return geocodeCache.get(key);
    }

    const url =
      "https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=" +
      encodeURIComponent(placeName + ", India");

    const response = await fetch(url, {
      headers: {
        Accept: "application/json"
      }
    });

    if (!response.ok) {
      throw new Error("Place lookup unavailable");
    }

    const rows = await response.json();

    const point = rows.length
      ? [Number(rows[0].lat), Number(rows[0].lon)]
      : null;

    geocodeCache.set(key, point);
    return point;
  }

  // 12. Apply location and category filters
  function filtered() {
    const location = locationEl.value.trim().toLowerCase();
    const type = typeEl.value;

    return alerts.filter(alert => {
      const matchesLocation =
        !location || alertText(alert).toLowerCase().includes(location);

      const matchesType =
        !type || category(alert) === type;

      return matchesLocation && matchesType;
    });
  }

  // 13. Add an alert marker
  function addMarker(alert, placeName, point) {
    const level = severity(alert);
    const color = colors[level];

    L.circleMarker(point, {
      radius: 8,
      weight: 2,
      color,
      fillColor: color,
      fillOpacity: 0.82
    })
      .addTo(markers)
      .bindPopup(
        `<strong>${safe(alert.title || "Official alert")}</strong>` +
        `<br>${safe(placeName)}` +
        `<br>${safe(category(alert))} · Display estimate: ${level}` +
        "<br><small>Place reference only; not a verified impact area or official severity.</small>"
      );
  }

  // 14. Render alert cards
  function render(items) {
    listEl.replaceChildren();

    if (!items.length) {
      const message = document.createElement("p");
      message.className = "small";
      message.textContent =
        "No alerts available or none match these filters.";

      listEl.appendChild(message);
      return;
    }

    items.forEach(alert => {
      const card = document.createElement("article");
      card.className = "alert-card";

      const type = category(alert);
      const level = severity(alert);

      const categoryPill = document.createElement("span");
      categoryPill.className = "pill";
      categoryPill.textContent = type;

      const severityPill = document.createElement("span");
      severityPill.className = "pill";
      severityPill.style.color = colors[level];
      severityPill.style.border = `1px solid ${colors[level]}`;
      severityPill.textContent = `${level} · display estimate`;

      const heading = document.createElement("h3");
      heading.textContent = alert.title || "Disaster alert";

      const description = document.createElement("p");
      description.textContent =
        (alert.description || "No description supplied.").slice(0, 420);

      const published = document.createElement("p");
      published.textContent =
        alert.published || "Publication time not provided";

      card.append(
        categoryPill,
        document.createTextNode(" "),
        severityPill,
        heading,
        description,
        published
      );

      // Add the original alert link when valid
      if (
        typeof alert.link === "string" &&
        /^https?:\/\//i.test(alert.link)
      ) {
        try {
          const linkUrl = new URL(alert.link);

          if (["http:", "https:"].includes(linkUrl.protocol)) {
            const paragraph = document.createElement("p");
            const link = document.createElement("a");

            link.href = linkUrl.href;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = "Open original alert ↗";

            paragraph.appendChild(link);
            card.appendChild(paragraph);
          }
        } catch (_) {
          // Ignore malformed links
        }
      }

      // Show location button
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "Show location";
      button.style.marginTop = "8px";

      button.addEventListener("click", async () => {
        const placeName = place(alert);

        if (!placeName) {
          statusEl.textContent =
            "No recognized place found. No location was guessed.";
          return;
        }

        button.disabled = true;
        statusEl.textContent = `Looking up ${placeName}…`;

        try {
          const point = await geocode(placeName);

          if (!point) {
            statusEl.textContent =
              `Could not locate ${placeName}.`;
            return;
          }

          addMarker(alert, placeName, point);
          map.setView(point, 9);

          statusEl.textContent =
            `Showing ${placeName}. This is a place reference, not a verified impact boundary.`;
        } catch (error) {
          statusEl.textContent =
            error.message || "Place lookup failed.";
        } finally {
          button.disabled = false;
        }
      });

      card.appendChild(button);
      listEl.appendChild(card);
    });
  }

  // 15. Automatically map up to five recognized place references
  async function autoMark(items) {
    let count = 0;
    const seen = new Set();

    for (const alert of items) {
      if (count >= 5) break;

      const placeName = place(alert);
      if (!placeName) continue;

      const key = `${placeName.toLowerCase()}|${alert.title || ""}`;

      if (seen.has(key)) continue;
      seen.add(key);

      try {
        const point = await geocode(placeName);

        if (point) {
          addMarker(alert, placeName, point);
          count++;
        }
      } catch (error) {
        console.warn("Place lookup failed:", error);
        break;
      }

      // Keep requests spaced out
      await new Promise(resolve => setTimeout(resolve, 1100));
    }

    return count;
  }

  // 16. Apply filters and redraw markers
  function apply() {
    markers.clearLayers();

    const items = filtered();
    render(items);

    statusEl.textContent =
      `${items.length} alert(s) match filters. Locations are place references, not verified impact boundaries.`;
  }

  // 17. Fetch alerts from the Flask backend
  async function load() {
    if (busy) return;

    busy = true;
    refreshBtn.disabled = true;
    statusEl.textContent = "Fetching disaster alerts…";

    try {
      const response = await fetch("/api/live-alerts", {
        cache: "no-store"
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Alert feed unavailable");
      }

      alerts = Array.isArray(data.alerts) ? data.alerts : [];

      markers.clearLayers();
      render(filtered());

      if (!alerts.length) {
        statusEl.textContent = data.live_data
          ? "No alerts were returned by the source."
          : "Live alert feed is unavailable or not confirmed live.";

        return;
      }

      statusEl.textContent = "Recognizing place names…";

      const count = await autoMark(filtered());

      statusEl.textContent = data.live_data
        ? `Loaded ${alerts.length} alert(s); mapped ${count} recognized place reference(s).`
        : "Alert data is not confirmed live. Check the backend source status.";

    } catch (error) {
      console.error("DisasterShield alert loading failed:", error);

      statusEl.textContent = "Could not load alerts. Check the Flask backend.";

      listEl.replaceChildren();

      const message = document.createElement("p");
      message.className = "small";
      message.textContent = error.message || "Request failed";

      listEl.appendChild(message);
    } finally {
      busy = false;
      refreshBtn.disabled = false;
    }
  }

  // 18. Connect filters and buttons
  locationEl.addEventListener("input", apply);
  typeEl.addEventListener("change", apply);
  refreshBtn.addEventListener("click", load);

  backBtn.addEventListener("click", () => {
    window.location.href = "/";
  });

  // 19. Start the application
  load();
})();