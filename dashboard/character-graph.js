/* dashboard/character-graph.js — Force-directed character graph */

(function () {
  "use strict";

  const DATA_PATH = "data/character_graph.json";

  const svg = document.getElementById("graph");
  const panel = document.getElementById("info-panel");
  const controls = {
    stiffness: document.getElementById("stiffness"),
    repulsion: document.getElementById("repulsion"),
    friction: document.getElementById("friction"),
  };

  let data = null;
  let nodes = [];
  let edges = [];
  let draggedNode = null;
  let pinMode = false;
  let running = true;

  function loadData() {
    return fetch(DATA_PATH, { cache: "no-store" })
      .then((r) => r.json())
      .then((d) => {
        data = d;
        buildGraph();
        animate();
      });
  }

  function buildGraph() {
    svg.innerHTML = "";
    const rect = svg.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    nodes = data.characters.map((c, i) => ({
      id: c.id,
      name: c.name,
      arc: c.arc,
      wiki: c.wiki,
      x: width / 2 + Math.cos((i / data.characters.length) * Math.PI * 2) * 240,
      y: height / 2 + Math.sin((i / data.characters.length) * Math.PI * 2) * 180,
      vx: 0, vy: 0,
      radius: 12 + (c.name.length > 8 ? c.name.length / 2 : 6),
    }));

    const idMap = new Map(nodes.map((n) => [n.id, n]));
    edges = data.edges
      .filter((e) => idMap.has(e.source) && idMap.has(e.target))
      .map((e) => ({
        source: idMap.get(e.source),
        target: idMap.get(e.target),
        label: e.label,
        weight: e.weight || 1,
      }));

    edges.forEach((e) => {
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("class", "edge weight-" + e.weight);
      line.dataset.source = e.source.id;
      line.dataset.target = e.target.id;
      svg.appendChild(line);
      e.line = line;
    });

    nodes.forEach((n) => {
      const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
      g.setAttribute("class", "node arc-" + n.arc);
      g.dataset.id = n.id;

      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", 0);
      circle.setAttribute("cy", 0);
      circle.setAttribute("r", n.radius);
      circle.setAttribute("fill", "#06090f");
      g.appendChild(circle);

      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("y", -n.radius - 4);
      label.setAttribute("class", "node-label");
      label.textContent = n.name;
      g.appendChild(label);

      g.addEventListener("mousedown", (e) => startDrag(e, n));
      g.addEventListener("click", (e) => showInfo(e, n));

      svg.appendChild(g);
      n.el = g;
      n.circle = circle;
    });
  }

  function startDrag(e, n) {
    e.preventDefault();
    draggedNode = n;
  }
  function showInfo(e, n) {
    panel.innerHTML = `
      <span class="close">×</span>
      <h3>${n.name}</h3>
      <div class="label">Role</div>
      <div>${n.arc}</div>
      <div class="label" style="margin-top:6px">Connected to</div>
      <div>${edges.filter(e => e.source === n || e.target === n).map(e => {
        const o = (e.source === n ? e.target : e.source);
        return `· ${o.name} <span style="color:#6a7888">(${e.label})</span>`;
      }).join('<br>')}</div>
      <div class="label" style="margin-top:6px">Wiki</div>
      <div><a href="../../../Fiction/wiki/${n.wiki}" target="_blank" rel="noopener" style="color:#66ffcc">${n.wiki}</a></div>
    `;
    panel.classList.add("show");
    panel.querySelector(".close").addEventListener("click", () => panel.classList.remove("show"));
    e.stopPropagation();
  }

  document.addEventListener("mousemove", (e) => {
    if (!draggedNode) return;
    const rect = svg.getBoundingClientRect();
    draggedNode.x = (e.clientX - rect.left) * (parseFloat(svg.getAttribute("width") || rect.width) / rect.width);
    draggedNode.y = (e.clientY - rect.top) * (parseFloat(svg.getAttribute("height") || rect.height) / rect.height);
    draggedNode.vx = 0;
    draggedNode.vy = 0;
  });
  document.addEventListener("mouseup", () => { draggedNode = null; });

  function step() {
    if (!running) return;
    const stiffness = parseFloat(controls.stiffness.value);
    const repulsion = parseFloat(controls.repulsion.value);
    const friction = parseFloat(controls.friction.value);
    const W = svg.getBoundingClientRect().width;
    const H = svg.getBoundingClientRect().height;

    for (let i = 0; i < nodes.length; i++) {
      const a = nodes[i];
      a.vx = (a.vx || 0) * friction;
      a.vy = (a.vy || 0) * friction;
      for (let j = i + 1; j < nodes.length; j++) {
        const b = nodes[j];
        const dx = b.x - a.x, dy = b.y - a.y;
        const d2 = dx * dx + dy * dy;
        if (d2 < 100) continue;
        const d = Math.sqrt(d2);
        const f = repulsion / d2;
        const fx = (dx / d) * f;
        const fy = (dy / d) * f;
        a.vx -= fx; a.vy -= fy;
        b.vx += fx; b.vy += fy;
      }
    }

    for (const e of edges) {
      const s = e.source, t = e.target;
      const dx = t.x - s.x, dy = t.y - s.y;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d < 50) continue;
      const target = 160;
      const stretch = d - target;
      const f = stretch * stiffness;
      const fx = (dx / d) * f;
      const fy = (dy / d) * f;
      s.vx += fx; s.vy += fy;
      t.vx -= fx; t.vy -= fy;
    }

    const cx = W / 2;
    const cy = H / 2;
    nodes.forEach((n) => {
      n.vx += (cx - n.x) * 0.001;
      n.vy += (cy - n.y) * 0.001;
      n.x += n.vx || 0;
      n.y += n.vy || 0;
      n.x = Math.max(20, Math.min(W - 20, n.x));
      n.y = Math.max(20, Math.min(H - 20, n.y));
    });

    updatePositions();
  }

  function updatePositions() {
    nodes.forEach((n) => {
      n.el.setAttribute("transform", `translate(${n.x},${n.y})`);
    });
    edges.forEach((e) => {
      e.line.setAttribute("x1", e.source.x);
      e.line.setAttribute("y1", e.source.y);
      e.line.setAttribute("x2", e.target.x);
      e.line.setAttribute("y2", e.target.y);
    });
  }

  function animate() {
    function loop() {
      step();
      requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);
  }

  document.getElementById("restart-btn").addEventListener("click", () => {
    buildGraph();
  });

  document.getElementById("pin-btn").addEventListener("click", (e) => {
    pinMode = !pinMode;
    e.target.textContent = pinMode ? "Unpin positions" : "Pin positions";
  });

  loadData();
})();
