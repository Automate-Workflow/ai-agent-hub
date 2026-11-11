(function () {
  "use strict";

  const PALETTE_GROUPS = {
    concepts: { color: "#B91C1C", label: "Concept (CP)" },
    agent_types: { color: "#7F1D1D", label: "Agent Type (AT)" },
    patterns: { color: "#DC2626", label: "Pattern (PT)" },
    protocols_standards: { color: "#991B1B", label: "Protocol (PS)" },
    frameworks_tools: { color: "#EA580C", label: "Framework / Tool (FW)" },
    risks_security: { color: "#111827", label: "Risk (RS)" },
    evaluation: { color: "#2563EB", label: "Evaluation (EV)" },
    use_cases: { color: "#059669", label: "Use Case (UC)" },
    learning_paths: { color: "#7C3AED", label: "Learning Path (LP)" },
    resources: { color: "#4B5563", label: "Resource (RES)" },
  };

  const PROGRESS_KEY = "ai_agent_hub_lp_progress_v1";
  const THEME_KEY = "ai_agent_hub_theme_v1";

  const state = {
    summary: null,
    index: [],
    graph: null,
    datasets: {},
    byId: new Map(),
    srcById: new Map(),
    adjOut: new Map(),
    adjIn: new Map(),
    aliases: [],
    selectedId: null,
    activeTrack: "Foundations",
    progress: {},
    graphView: {
      nodes: [],
      edges: [],
      scale: 1,
      tx: 0,
      ty: 0,
      draggingNode: null,
      panning: false,
      lastX: 0,
      lastY: 0,
      hoveredNode: null,
    },
  };

  function el(id) {
    return document.getElementById(id);
  }

  function escHtml(text) {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function loadProgress() {
    try {
      const raw = localStorage.getItem(PROGRESS_KEY);
      state.progress = raw ? JSON.parse(raw) : {};
    } catch (_e) {
      state.progress = {};
    }
  }

  function saveProgress() {
    try {
      localStorage.setItem(PROGRESS_KEY, JSON.stringify(state.progress));
    } catch (_e) {
      // Ignore storage quota / disabled storage cleanly
    }
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const btn = el("theme-toggle");
    if (btn) {
      btn.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    }
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_e) {
      // Ignore
    }
    if (state.graphView.nodes.length) {
      drawGraph();
    }
  }

  function initTheme() {
    let saved = "light";
    try {
      saved = localStorage.getItem(THEME_KEY) || "light";
    } catch (_e) {
      saved = "light";
    }
    applyTheme(saved);
    el("theme-toggle").addEventListener("click", function () {
      const cur = document.documentElement.getAttribute("data-theme") || "light";
      applyTheme(cur === "dark" ? "light" : "dark");
    });
  }

  async function loadAllData() {
    if (window.AI_AGENT_HUB_DATA && window.AI_AGENT_HUB_DATA.summary) {
      return window.AI_AGENT_HUB_DATA;
    }
    const dsNames = [
      "sources", "concepts", "agent_types", "patterns", "protocols_standards",
      "frameworks_tools", "use_cases", "risks_security", "evaluation",
      "learning_paths", "resources", "relationships", "glossary_aliases",
    ];
    const [summary, index, graph, ...dsLists] = await Promise.all([
      fetch("data/summary.json").then((r) => r.json()),
      fetch("data/index.json").then((r) => r.json()),
      fetch("data/graph.json").then((r) => r.json()),
      ...dsNames.map((n) => fetch("data/" + n + ".json").then((r) => r.json())),
    ]);
    const datasets = {};
    dsNames.forEach((n, i) => { datasets[n] = dsLists[i]; });
    return { summary, index, graph, datasets };
  }

  function indexData(payload) {
    state.summary = payload.summary;
    state.index = payload.index || [];
    state.graph = payload.graph || { nodes: [], edges: [] };
    state.datasets = payload.datasets || {};
    state.aliases = state.datasets.glossary_aliases || [];

    (state.datasets.sources || []).forEach((s) => state.srcById.set(s.id, s));

    Object.entries(state.datasets).forEach(([dsName, rows]) => {
      if (dsName === "sources" || dsName === "relationships" || dsName === "glossary_aliases") return;
      (rows || []).forEach((r) => {
        if (r.id) {
          state.byId.set(r.id, { dataset: dsName, row: r });
        }
      });
    });

    (state.datasets.relationships || []).forEach((e) => {
      if (!state.adjOut.has(e.from_id)) state.adjOut.set(e.from_id, []);
      if (!state.adjIn.has(e.to_id)) state.adjIn.set(e.to_id, []);
      state.adjOut.get(e.from_id).push(e);
      state.adjIn.get(e.to_id).push(e);
    });
  }

  function switchTab(tabName) {
    document.querySelectorAll(".tab-btn").forEach((b) => {
      const active = b.dataset.tab === tabName;
      b.classList.toggle("active", active);
      b.setAttribute("aria-selected", active ? "true" : "false");
    });
    document.querySelectorAll(".tab-panel").forEach((p) => {
      const active = p.id === "tab-" + tabName;
      p.classList.toggle("active", active);
      p.hidden = !active;
    });
    if (tabName === "graph") {
      renderGraphFromControls();
    }
  }

  function renderOverview() {
    const s = state.summary;
    const kpiGrid = el("overview-kpis");
    const bars = el("dataset-bars");
    const dsEntries = Object.entries(s.datasets || {});

    const cards = [
      { num: s.total_rows, label: "Total Curated Rows", sub: "Across 13 relational datasets", tab: "catalog" },
      { num: s.datasets.concepts.rows, label: "Core Concepts", sub: "CP-001 to CP-136", ds: "concepts" },
      { num: s.datasets.agent_types.rows, label: "Agent Types", sub: "3 classification views", ds: "agent_types" },
      { num: s.datasets.patterns.rows, label: "Design Patterns", sub: "Workflow to multi-agent", ds: "patterns" },
      { num: s.datasets.relationships.rows, label: "Graph Edges", sub: "10 typed predicates", tab: "graph" },
      { num: s.datasets.sources.rows, label: "Verified Sources", sub: "Primary & secondary", tab: "sources" },
      { num: s.datasets.resources.rows, label: "Resources", sub: "Docs, papers, courses, videos", ds: "resources" },
      { num: s.datasets.learning_paths.rows, label: "Curriculum Steps", sub: "5 role tracks", tab: "learning" },
    ];

    kpiGrid.innerHTML = cards.map((c) => `
      <div class="kpi-card" data-jump-ds="${escHtml(c.ds || "")}" data-jump-tab="${escHtml(c.tab || "")}">
        <div class="kpi-num">${escHtml(c.num)}</div>
        <div class="kpi-label">${escHtml(c.label)}</div>
        <div class="kpi-sub">${escHtml(c.sub)}</div>
      </div>
    `).join("");

    kpiGrid.querySelectorAll(".kpi-card").forEach((card) => {
      card.addEventListener("click", () => {
        if (card.dataset.jumpDs) {
          el("filter-dataset").value = card.dataset.jumpDs;
          populateCategoryOptions();
          renderCatalog();
          switchTab("catalog");
        } else if (card.dataset.jumpTab) {
          switchTab(card.dataset.jumpTab);
        }
      });
    });

    const maxRows = Math.max(...dsEntries.map(([, d]) => d.rows), 1);
    bars.innerHTML = dsEntries.map(([name, d]) => {
      const pct = Math.min(100, Math.round((d.rows / maxRows) * 100));
      const tgt = d.max_target ? `${d.min_target}-${d.max_target}` : `${d.min_target}+`;
      return `
        <div class="bar-row">
          <div class="bar-row-head">
            <span><strong>${escHtml(name)}</strong></span>
            <span>${d.rows} / ${escHtml(tgt)}</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
        </div>
      `;
    }).join("");
  }

  function populateDatasetOptions() {
    const sel = el("filter-dataset");
    const present = Array.from(new Set(state.index.map((x) => x.dataset))).sort();
    present.forEach((ds) => {
      const opt = document.createElement("option");
      opt.value = ds;
      opt.textContent = ds;
      sel.appendChild(opt);
    });
  }

  function populateCategoryOptions() {
    const dsFilter = el("filter-dataset").value;
    const catSel = el("filter-category");
    const prev = catSel.value;
    const cats = Array.from(new Set(
      state.index
        .filter((x) => dsFilter === "all" || x.dataset === dsFilter)
        .map((x) => x.category)
        .filter(Boolean)
    )).sort();
    catSel.innerHTML = '<option value="all">All Categories</option>' +
      cats.map((c) => `<option value="${escHtml(c)}">${escHtml(c)}</option>`).join("");
    if (cats.includes(prev)) catSel.value = prev;
  }

  function renderCatalog() {
    const q = el("global-search").value.trim().toLowerCase();
    const dsF = el("filter-dataset").value;
    const catF = el("filter-category").value;
    const diffF = el("filter-difficulty").value;
    const confF = el("filter-confidence").value;
    const statF = el("filter-status").value;

    const aliasBanner = el("alias-banner");
    const aliasMatches = q.length >= 2
      ? state.aliases.filter((a) => a.alias.toLowerCase().includes(q)).slice(0, 6)
      : [];
    if (aliasMatches.length) {
      aliasBanner.hidden = false;
      aliasBanner.innerHTML = "<strong>Glossary aliases matching query:</strong> " +
        aliasMatches.map((a) => `<button class="quick-chip" data-inspect="${escHtml(a.canonical_id)}">${escHtml(a.alias)} &rarr; ${escHtml(a.canonical_id)}</button>`).join(" ");
      aliasBanner.querySelectorAll("[data-inspect]").forEach((b) => {
        b.addEventListener("click", () => inspectEntity(b.dataset.inspect));
      });
    } else {
      aliasBanner.hidden = true;
    }

    const aliasTargetIds = new Set(aliasMatches.map((a) => a.canonical_id));
    const hits = state.index.filter((item) => {
      if (dsF !== "all" && item.dataset !== dsF) return false;
      if (catF !== "all" && item.category !== catF) return false;
      if (diffF !== "all" && item.difficulty !== diffF) return false;
      if (confF !== "all" && item.confidence !== confF) return false;
      if (statF !== "all" && item.status !== statF) return false;
      if (!q) return true;
      return (
        item.id.toLowerCase().includes(q) ||
        item.title.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.summary.toLowerCase().includes(q) ||
        aliasTargetIds.has(item.id)
      );
    });

    el("catalog-count").textContent = `${hits.length} item${hits.length === 1 ? "" : "s"}`;
    const grid = el("catalog-grid");
    const shown = hits.slice(0, 120);
    grid.innerHTML = shown.map((item) => `
      <article class="entity-card ${state.selectedId === item.id ? "selected" : ""}" data-id="${escHtml(item.id)}" tabindex="0">
        <div class="card-top">
          <span class="pill pill-red">${escHtml(item.id)}</span>
          <span class="pill pill-soft">${escHtml(item.dataset)}</span>
        </div>
        <h3 class="card-title">${escHtml(item.title)}</h3>
        <p class="card-summary">${escHtml(item.summary)}</p>
        <div class="card-meta">
          ${item.category ? `<span class="pill pill-neutral">${escHtml(item.category)}</span>` : ""}
          ${item.difficulty ? `<span class="pill pill-neutral">${escHtml(item.difficulty)}</span>` : ""}
          ${item.confidence ? `<span class="pill pill-neutral">${escHtml(item.confidence)}</span>` : ""}
        </div>
      </article>
    `).join("") + (hits.length > 120 ? `<div class="callout-soft">Showing top 120 of ${hits.length} matches. Narrow filters or refine search to inspect more items.</div>` : "");

    grid.querySelectorAll(".entity-card").forEach((card) => {
      card.addEventListener("click", () => inspectEntity(card.dataset.id));
      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          inspectEntity(card.dataset.id);
        }
      });
    });
  }

  function inspectEntity(id) {
    const rec = state.byId.get(id);
    if (!rec) return;
    state.selectedId = id;
    const drawer = el("detail-drawer");
    drawer.hidden = false;

    const r = rec.row;
    const title = r.term || r.name || r.use_case || r.risk || r.title || id;
    el("drawer-id").textContent = id;
    el("drawer-dataset").textContent = rec.dataset;
    el("drawer-title").textContent = title;

    const badges = [];
    ["category", "view", "kind", "industry", "path_name", "difficulty", "level", "confidence", "status", "verified_date"].forEach((k) => {
      if (r[k]) badges.push(`<span class="pill pill-neutral">${escHtml(k)}: ${escHtml(r[k])}</span>`);
    });
    el("drawer-badges").innerHTML = badges.join("");

    const skip = new Set(["id", "term", "name", "use_case", "risk", "title", "source_ids"]);
    let bodyHtml = "";
    Object.entries(r).forEach(([k, v]) => {
      if (skip.has(k) || !v) return;
      if (k === "url" || k === "spec_url" || k === "repo_or_docs_url") {
        bodyHtml += `<div class="drawer-field"><div class="drawer-field-label">${escHtml(k)}</div><div class="drawer-field-val"><a class="src-link" href="${escHtml(v)}" target="_blank" rel="noopener noreferrer">${escHtml(v)}</a></div></div>`;
      } else if (k.endsWith("_ids") || k === "parent_id") {
        const chips = v.split("|").filter(Boolean).map((tid) => {
          const target = state.byId.get(tid);
          const tlbl = target ? (target.row.term || target.row.name || target.row.title || target.row.risk || tid) : tid;
          return `<button class="quick-chip" data-inspect="${escHtml(tid)}">${escHtml(tid)}: ${escHtml(tlbl.slice(0, 36))}</button>`;
        }).join(" ");
        bodyHtml += `<div class="drawer-field"><div class="drawer-field-label">${escHtml(k)}</div><div class="step-chips">${chips}</div></div>`;
      } else {
        bodyHtml += `<div class="drawer-field"><div class="drawer-field-label">${escHtml(k)}</div><div class="drawer-field-val">${escHtml(v)}</div></div>`;
      }
    });

    const outEdges = state.adjOut.get(id) || [];
    const inEdges = state.adjIn.get(id) || [];
    if (outEdges.length || inEdges.length) {
      bodyHtml += `<div class="drawer-edges"><h4 class="drawer-section-title">Knowledge Graph Neighbors (${outEdges.length + inEdges.length})</h4>`;
      outEdges.forEach((e) => {
        const tgt = state.byId.get(e.to_id);
        const tlbl = tgt ? (tgt.row.term || tgt.row.name || tgt.row.risk || tgt.row.title || e.to_id) : e.to_id;
        bodyHtml += `<button class="edge-chip" data-inspect="${escHtml(e.to_id)}"><strong>${escHtml(e.relation)} &rarr;</strong> ${escHtml(e.to_id)} (${escHtml(tlbl)})</button>`;
      });
      inEdges.forEach((e) => {
        const src = state.byId.get(e.from_id);
        const slbl = src ? (src.row.term || src.row.name || src.row.risk || src.row.title || e.from_id) : e.from_id;
        bodyHtml += `<button class="edge-chip" data-inspect="${escHtml(e.from_id)}"><strong>&larr; ${escHtml(e.relation)}</strong> from ${escHtml(e.from_id)} (${escHtml(slbl)})</button>`;
      });
      bodyHtml += `</div>`;
    }

    const srcIds = (r.source_ids || "").split("|").filter(Boolean);
    if (srcIds.length) {
      bodyHtml += `<div class="drawer-sources"><h4 class="drawer-section-title">Cited Sources (${srcIds.length})</h4>`;
      srcIds.forEach((sid) => {
        const sr = state.srcById.get(sid);
        if (sr) {
          bodyHtml += `<a class="src-link" href="${escHtml(sr.url)}" target="_blank" rel="noopener noreferrer"><strong>${escHtml(sid)}</strong> [${escHtml(sr.reliability)}]: ${escHtml(sr.title)} (${escHtml(sr.publisher)})</a>`;
        } else {
          bodyHtml += `<div class="drawer-field-val">${escHtml(sid)}</div>`;
        }
      });
      bodyHtml += `</div>`;
    }

    el("drawer-body").innerHTML = bodyHtml;
    el("drawer-body").querySelectorAll("[data-inspect]").forEach((btn) => {
      btn.addEventListener("click", () => inspectEntity(btn.dataset.inspect));
    });
    el("drawer-graph-btn").onclick = () => {
      el("graph-focus").value = id;
      el("graph-depth").value = "1";
      switchTab("graph");
    };

    document.querySelectorAll(".entity-card").forEach((c) => {
      c.classList.toggle("selected", c.dataset.id === id);
    });
  }

  function renderLearningPaths() {
    const steps = state.datasets.learning_paths || [];
    const tracks = ["Foundations", "Builder", "Architect", "Security and Governance", "Team Lead"];
    const pillsEl = el("track-pills");
    pillsEl.innerHTML = tracks.map((t) => `
      <button class="track-pill ${state.activeTrack === t ? "active" : ""}" data-track="${escHtml(t)}">${escHtml(t)}</button>
    `).join("");

    pillsEl.querySelectorAll(".track-pill").forEach((b) => {
      b.addEventListener("click", () => {
        state.activeTrack = b.dataset.track;
        renderLearningPaths();
      });
    });

    const trackSteps = steps
      .filter((s) => s.path_name === state.activeTrack)
      .sort((a, b) => Number(a.step) - Number(b.step));

    const doneCount = trackSteps.filter((s) => !!state.progress[s.id]).length;
    const totalHours = trackSteps.reduce((acc, s) => acc + parseFloat(s.estimated_hours || "0"), 0);
    el("progress-label").textContent = `${state.activeTrack}: ${doneCount} / ${trackSteps.length} steps (~${totalHours.toFixed(0)}h total est.)`;
    el("progress-bar-fill").style.width = trackSteps.length ? `${Math.round((doneCount / trackSteps.length) * 100)}%` : "0%";

    const list = el("learning-steps");
    list.innerHTML = trackSteps.map((st) => {
      const checked = !!state.progress[st.id];
      const cpChips = (st.concept_ids || "").split("|").filter(Boolean).map((cid) =>
        `<button class="quick-chip" data-inspect="${escHtml(cid)}">${escHtml(cid)}</button>`
      ).join("");
      const resChips = (st.resource_ids || "").split("|").filter(Boolean).map((rid) => {
        const resRec = state.byId.get(rid);
        const rtitle = resRec ? resRec.row.title : rid;
        const rurl = resRec ? resRec.row.url : "#";
        return `<a class="pill pill-soft" href="${escHtml(rurl)}" target="_blank" rel="noopener noreferrer">${escHtml(rid)}: ${escHtml(rtitle.slice(0, 32))}</a>`;
      }).join("");

      return `
        <div class="step-card ${checked ? "completed" : ""}">
          <input class="step-check" type="checkbox" data-lp="${escHtml(st.id)}" ${checked ? "checked" : ""} aria-label="Mark step ${escHtml(st.step)} completed" />
          <div class="step-body">
            <div><span class="pill pill-red">Step ${escHtml(st.step)}</span> <span class="pill pill-neutral">${escHtml(st.id)}</span> <span class="pill pill-neutral">~${escHtml(st.estimated_hours)}h est.</span></div>
            <h3 class="step-title">${escHtml(st.title)}</h3>
            <p class="step-desc"><strong>Objective:</strong> ${escHtml(st.objective)}<br/><strong>Outcome:</strong> ${escHtml(st.outcome)}</p>
            <div class="step-chips">${cpChips} ${resChips}</div>
          </div>
        </div>
      `;
    }).join("");

    list.querySelectorAll(".step-check").forEach((chk) => {
      chk.addEventListener("change", () => {
        if (chk.checked) {
          state.progress[chk.dataset.lp] = true;
        } else {
          delete state.progress[chk.dataset.lp];
        }
        saveProgress();
        renderLearningPaths();
      });
    });
    list.querySelectorAll("[data-inspect]").forEach((b) => {
      b.addEventListener("click", () => inspectEntity(b.dataset.inspect));
    });
  }

  function populateSourceFilters() {
    const types = Array.from(new Set((state.datasets.sources || []).map((s) => s.source_type))).sort();
    const sel = el("source-type-filter");
    types.forEach((t) => {
      const opt = document.createElement("option");
      opt.value = t;
      opt.textContent = t;
      sel.appendChild(opt);
    });
  }

  function renderSources() {
    const q = el("global-search").value.trim().toLowerCase();
    const typeF = el("source-type-filter").value;
    const relF = el("source-rel-filter").value;
    const rows = (state.datasets.sources || []).filter((s) => {
      if (typeF !== "all" && s.source_type !== typeF) return false;
      if (relF !== "all" && s.reliability !== relF) return false;
      if (!q) return true;
      return (
        s.id.toLowerCase().includes(q) ||
        s.title.toLowerCase().includes(q) ||
        s.publisher.toLowerCase().includes(q) ||
        s.notes.toLowerCase().includes(q)
      );
    });
    el("sources-count").textContent = `${rows.length} sources`;
    el("sources-tbody").innerHTML = rows.map((s) => `
      <tr>
        <td><code>${escHtml(s.id)}</code></td>
        <td><a href="${escHtml(s.url)}" target="_blank" rel="noopener noreferrer">${escHtml(s.title)}</a><br/><span style="color:var(--muted);font-size:0.78rem">${escHtml(s.publisher)} &middot; ${escHtml(s.author)}</span></td>
        <td><span class="pill pill-neutral">${escHtml(s.source_type)}</span></td>
        <td><span class="pill ${s.reliability === "primary" ? "pill-red" : "pill-soft"}">${escHtml(s.reliability)}</span></td>
        <td>${escHtml(s.published_date || "-")}</td>
        <td>${escHtml(s.notes)}</td>
      </tr>
    `).join("");
  }

  // --- INTERACTIVE CANVAS GRAPH ---
  function renderGraphLegend() {
    el("graph-legend").innerHTML = Object.entries(PALETTE_GROUPS)
      .slice(0, 8)
      .map(([, v]) => `<span class="legend-item"><span class="legend-dot" style="background:${v.color}"></span>${escHtml(v.label)}</span>`)
      .join("");
  }

  function renderGraphFromControls() {
    const focusId = el("graph-focus").value.trim().toUpperCase() || "CP-001";
    const depthMode = el("graph-depth").value;
    const relFilter = el("graph-relation").value;

    const allNodesMap = new Map((state.graph.nodes || []).map((n) => [n.id, n]));
    const filteredEdges = (state.graph.edges || []).filter((e) =>
      e.endpoints_present && (relFilter === "all" || e.relation === relFilter)
    );

    const activeIds = new Set();
    if (depthMode === "hubs") {
      const deg = new Map();
      filteredEdges.forEach((e) => {
        deg.set(e.source, (deg.get(e.source) || 0) + 1);
        deg.set(e.target, (deg.get(e.target) || 0) + 1);
      });
      Array.from(deg.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 48)
        .forEach(([id]) => activeIds.add(id));
    } else {
      const seed = allNodesMap.has(focusId) ? focusId : "CP-001";
      activeIds.add(seed);
      const hops = depthMode === "2" ? 2 : 1;
      for (let h = 0; h < hops; h++) {
        const frontier = new Set(activeIds);
        filteredEdges.forEach((e) => {
          if (frontier.has(e.source)) activeIds.add(e.target);
          if (frontier.has(e.target)) activeIds.add(e.source);
          if (activeIds.size > 90) return;
        });
      }
    }

    const edges = filteredEdges.filter((e) => activeIds.has(e.source) && activeIds.has(e.target)).slice(0, 220);
    const canvas = el("graph-canvas");
    const w = canvas.clientWidth || 900;
    const h = canvas.clientHeight || 620;

    const nodes = Array.from(activeIds).map((id, idx) => {
      const base = allNodesMap.get(id) || { id, label: id, dataset: "concepts" };
      const angle = (idx / Math.max(activeIds.size, 1)) * Math.PI * 2;
      const rad = id === focusId ? 0 : Math.min(w, h) * 0.32;
      return {
        ...base,
        x: w / 2 + Math.cos(angle) * rad,
        y: h / 2 + Math.sin(angle) * rad,
        vx: 0,
        vy: 0,
        isFocus: id === focusId,
      };
    });

    // Quick deterministic force-layout relaxation steps
    const nodeById = new Map(nodes.map((n) => [n.id, n]));
    for (let iter = 0; iter < 110; iter++) {
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          let dx = b.x - a.x, dy = b.y - a.y;
          const d2 = dx * dx + dy * dy + 0.1;
          if (d2 < 32000) {
            const f = 1400 / d2;
            a.vx -= dx * f; a.vy -= dy * f;
            b.vx += dx * f; b.vy += dy * f;
          }
        }
      }
      edges.forEach((e) => {
        const a = nodeById.get(e.source), b = nodeById.get(e.target);
        if (!a || !b) return;
        const dx = b.x - a.x, dy = b.y - a.y;
        const d = Math.hypot(dx, dy) || 1;
        const targetLen = 135;
        const f = (d - targetLen) * 0.04;
        a.vx += (dx / d) * f; a.vy += (dy / d) * f;
        b.vx -= (dx / d) * f; b.vy -= (dy / d) * f;
      });
      nodes.forEach((n) => {
        n.vx += (w / 2 - n.x) * 0.008;
        n.vy += (h / 2 - n.y) * 0.008;
        n.x += Math.max(-18, Math.min(18, n.vx * 0.55));
        n.y += Math.max(-18, Math.min(18, n.vy * 0.55));
        n.vx *= 0.65;
        n.vy *= 0.65;
      });
    }

    state.graphView.nodes = nodes;
    state.graphView.edges = edges;
    state.graphView.scale = 1;
    state.graphView.tx = 0;
    state.graphView.ty = 0;
    el("graph-stats").textContent = `${nodes.length} nodes · ${edges.length} edges`;
    drawGraph();
  }

  function drawGraph() {
    const canvas = el("graph-canvas");
    if (!canvas) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 900;
    const h = canvas.clientHeight || 620;
    if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
      canvas.width = w * dpr;
      canvas.height = h * dpr;
    }
    const ctx = canvas.getContext("2d");
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);

    ctx.save();
    ctx.translate(state.graphView.tx, state.graphView.ty);
    ctx.scale(state.graphView.scale, state.graphView.scale);

    const nodeById = new Map(state.graphView.nodes.map((n) => [n.id, n]));
    ctx.lineWidth = 1.3;
    ctx.strokeStyle = isDark ? "rgba(248, 113, 113, 0.35)" : "rgba(185, 28, 28, 0.28)";
    state.graphView.edges.forEach((e) => {
      const a = nodeById.get(e.source), b = nodeById.get(e.target);
      if (!a || !b) return;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.lineTo(b.x, b.y);
      ctx.stroke();

      // Tiny directional arrowhead
      const ang = Math.atan2(b.y - a.y, b.x - a.x);
      const tx = b.x - Math.cos(ang) * 14;
      const ty = b.y - Math.sin(ang) * 14;
      ctx.beginPath();
      ctx.moveTo(tx, ty);
      ctx.lineTo(tx - 6 * Math.cos(ang - 0.4), ty - 6 * Math.sin(ang - 0.4));
      ctx.lineTo(tx - 6 * Math.cos(ang + 0.4), ty - 6 * Math.sin(ang + 0.4));
      ctx.closePath();
      ctx.fillStyle = isDark ? "#F87171" : "#B91C1C";
      ctx.fill();
    });

    state.graphView.nodes.forEach((n) => {
      const col = (PALETTE_GROUPS[n.dataset] && PALETTE_GROUPS[n.dataset].color) || "#B91C1C";
      const r = n.isFocus ? 14 : (n.id === state.selectedId ? 12 : 9);
      ctx.beginPath();
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      ctx.fillStyle = col;
      ctx.fill();
      ctx.lineWidth = n.isFocus || n.id === state.selectedId ? 3 : 1.5;
      ctx.strokeStyle = isDark ? "#F9FAFB" : "#FFFFFF";
      ctx.stroke();

      ctx.font = (n.isFocus ? "700 12px " : "600 10.5px ") + '"Segoe UI", Roboto, sans-serif';
      ctx.textAlign = "center";
      ctx.fillStyle = isDark ? "#F9FAFB" : "#111827";
      ctx.fillText(n.id, n.x, n.y + r + 13);
    });

    ctx.restore();
  }

  function screenToWorld(cx, cy) {
    return {
      x: (cx - state.graphView.tx) / state.graphView.scale,
      y: (cy - state.graphView.ty) / state.graphView.scale,
    };
  }

  function findNodeAt(wx, wy) {
    return state.graphView.nodes.find((n) => Math.hypot(n.x - wx, n.y - wy) <= 15);
  }

  function bindGraphInteractions() {
    const canvas = el("graph-canvas");
    const tooltip = el("graph-tooltip");

    canvas.addEventListener("mousedown", (e) => {
      const rect = canvas.getBoundingClientRect();
      const pt = screenToWorld(e.clientX - rect.left, e.clientY - rect.top);
      const hit = findNodeAt(pt.x, pt.y);
      state.graphView.lastX = e.clientX;
      state.graphView.lastY = e.clientY;
      if (hit) {
        state.graphView.draggingNode = hit;
        inspectEntity(hit.id);
        drawGraph();
      } else {
        state.graphView.panning = true;
      }
    });

    window.addEventListener("mousemove", (e) => {
      if (state.graphView.draggingNode) {
        const dx = (e.clientX - state.graphView.lastX) / state.graphView.scale;
        const dy = (e.clientY - state.graphView.lastY) / state.graphView.scale;
        state.graphView.draggingNode.x += dx;
        state.graphView.draggingNode.y += dy;
        state.graphView.lastX = e.clientX;
        state.graphView.lastY = e.clientY;
        drawGraph();
      } else if (state.graphView.panning) {
        state.graphView.tx += e.clientX - state.graphView.lastX;
        state.graphView.ty += e.clientY - state.graphView.lastY;
        state.graphView.lastX = e.clientX;
        state.graphView.lastY = e.clientY;
        drawGraph();
      } else if (e.target === canvas) {
        const rect = canvas.getBoundingClientRect();
        const pt = screenToWorld(e.clientX - rect.left, e.clientY - rect.top);
        const hit = findNodeAt(pt.x, pt.y);
        if (hit) {
          tooltip.hidden = false;
          tooltip.style.left = (e.clientX - rect.left + 14) + "px";
          tooltip.style.top = (e.clientY - rect.top + 14) + "px";
          tooltip.textContent = `${hit.id}: ${hit.label} (${hit.dataset})`;
        } else {
          tooltip.hidden = true;
        }
      }
    });

    window.addEventListener("mouseup", () => {
      state.graphView.draggingNode = null;
      state.graphView.panning = false;
    });

    canvas.addEventListener("wheel", (e) => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.12 : 0.89;
      const rect = canvas.getBoundingClientRect();
      const cx = e.clientX - rect.left;
      const cy = e.clientY - rect.top;
      const nextScale = Math.max(0.35, Math.min(3.5, state.graphView.scale * factor));
      state.graphView.tx = cx - ((cx - state.graphView.tx) / state.graphView.scale) * nextScale;
      state.graphView.ty = cy - ((cy - state.graphView.ty) / state.graphView.scale) * nextScale;
      state.graphView.scale = nextScale;
      drawGraph();
    }, { passive: false });

    el("graph-apply").addEventListener("click", renderGraphFromControls);
    el("graph-depth").addEventListener("change", renderGraphFromControls);
    el("graph-relation").addEventListener("change", renderGraphFromControls);
    el("graph-reset-zoom").addEventListener("click", () => {
      state.graphView.scale = 1;
      state.graphView.tx = 0;
      state.graphView.ty = 0;
      drawGraph();
    });
  }

  async function boot() {
    initTheme();
    loadProgress();

    try {
      const payload = await loadAllData();
      indexData(payload);
    } catch (err) {
      const box = el("load-error");
      box.hidden = false;
      box.textContent = "Unable to load explorer data. Run `python scripts/build_site_data.py` first, then refresh this page.";
      console.error(err);
      return;
    }

    renderOverview();
    populateDatasetOptions();
    populateCategoryOptions();
    renderCatalog();
    renderLearningPaths();
    populateSourceFilters();
    renderSources();
    renderGraphLegend();
    bindGraphInteractions();

    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => switchTab(btn.dataset.tab));
    });
    document.querySelectorAll("[data-jump-tab]").forEach((btn) => {
      btn.addEventListener("click", () => switchTab(btn.dataset.jumpTab));
    });
    document.querySelectorAll("[data-inspect]").forEach((btn) => {
      btn.addEventListener("click", () => inspectEntity(btn.dataset.inspect));
    });

    el("drawer-close").addEventListener("click", () => {
      el("detail-drawer").hidden = true;
      state.selectedId = null;
      document.querySelectorAll(".entity-card.selected").forEach((c) => c.classList.remove("selected"));
    });

    el("global-search").addEventListener("input", () => {
      const activeTab = document.querySelector(".tab-btn.active").dataset.tab;
      renderCatalog();
      renderSources();
      if (activeTab === "overview" && el("global-search").value.trim().length > 0) {
        switchTab("catalog");
      }
    });

    window.addEventListener("keydown", (e) => {
      if (e.key === "/" && document.activeElement !== el("global-search") && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) {
        e.preventDefault();
        el("global-search").focus();
      }
    });

    el("filter-dataset").addEventListener("change", () => { populateCategoryOptions(); renderCatalog(); });
    el("filter-category").addEventListener("change", renderCatalog);
    el("filter-difficulty").addEventListener("change", renderCatalog);
    el("filter-confidence").addEventListener("change", renderCatalog);
    el("filter-status").addEventListener("change", renderCatalog);
    el("source-type-filter").addEventListener("change", renderSources);
    el("source-rel-filter").addEventListener("change", renderSources);

    el("reset-progress").addEventListener("click", () => {
      const trackSteps = (state.datasets.learning_paths || []).filter((s) => s.path_name === state.activeTrack);
      trackSteps.forEach((s) => { delete state.progress[s.id]; });
      saveProgress();
      renderLearningPaths();
    });
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
