"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

async function api(path, options) {
  const response = await fetch(`/api/${path}`, { cache: "no-store", ...options });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body;
}

function formatTime(value) {
  if (!value) return "—";
  return new Date(value * 1000).toLocaleTimeString();
}

export default function Dashboard() {
  const [readings, setReadings] = useState([]);
  const [events, setEvents] = useState([]);
  const [online, setOnline] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [report, setReport] = useState(null);
  const [attack, setAttack] = useState("tampering");
  const [deviceId, setDeviceId] = useState("IOT_DEVICE_001");

  const refresh = useCallback(async () => {
    try {
      const [health, latest, security] = await Promise.all([
        api("health"), api("readings?limit=100"), api("events?limit=100"),
      ]);
      setOnline(Boolean(health.ok));
      setReadings(latest);
      setEvents(security);
      setMessage("");
    } catch (error) {
      setOnline(false);
      setMessage(error.message);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const devices = useMemo(() => new Set(readings.map((row) => row.device_id)).size, [readings]);
  const latest = readings[0];
  const attackCount = events.filter((row) => row.event_type?.startsWith("attack_") || row.event_type === "replay_detected").length;

  async function perform(path, payload, successText) {
    setBusy(true);
    setMessage("");
    try {
      const result = await api(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      setReport({ path, result });
      if (path === "attacks") {
        setMessage(`${result.attack}: ${result.actual_outcome}. Detected: ${result.detected}.`);
      } else if (path === "benchmark") {
        setMessage(`Benchmark finished: ${result.iterations} iterations, ${result.throughput_messages_per_second.toFixed(1)} messages/s.`);
      } else {
        setMessage(successText);
      }
      await refresh();
      return result;
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <a className="brand" href="#"><span className="brand-mark">DS</span><span>DES IoT <b>SECURITY</b></span></a>
        <div className="topbar-right"><span className="env-label">ACADEMIC DEMO</span><span className={`status ${online ? "online" : "offline"}`}><i />{online ? "BACKEND ONLINE" : "BACKEND OFFLINE"}</span></div>
      </header>

      <section className="hero">
        <div className="hero-copy"><div className="eyebrow"><span className="pulse" /> SECURE TELEMETRY PLATFORM</div>
          <h1>Device security<br /><em>at a glance.</em></h1>
          <p>Virtual sensors send authenticated, encrypted readings through the receiver pipeline. Inspect live records and trigger security checks.</p>
          <button className="button primary" disabled={busy} onClick={() => perform("simulate", { device_id: deviceId, device_name: "Virtual sensor" }, "Reading authenticated and stored.")}>{busy ? "Working…" : "＋ Generate secure reading"}</button>
        </div>
        <div className="hero-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="core"><span>DES</span><small>HMAC</small></div><div className="node node-a">TEMP</div><div className="node node-b">MQTT</div><div className="node node-c">AUTH</div><div className="node node-d">IoT</div></div>
      </section>

      <section className="metrics-grid">
        <article className="metric-card"><div className="metric-label">REGISTERED DEVICES</div><div className="metric-value">{devices.toString().padStart(2, "0")}</div><div className="metric-foot">Seen in authenticated readings</div></article>
        <article className="metric-card"><div className="metric-label">STORED READINGS</div><div className="metric-value">{readings.length.toString().padStart(2, "0")}</div><div className="metric-foot">Receiver accepted</div></article>
        <article className="metric-card"><div className="metric-label">SECURITY EVENTS</div><div className="metric-value">{events.length.toString().padStart(2, "0")}</div><div className="metric-foot">{attackCount} attacks or replay alerts</div></article>
        <article className="metric-card highlight"><div className="metric-label">LATEST TEMPERATURE</div><div className="metric-value">{latest?.temperature != null ? `${latest.temperature}°` : "—"}</div><div className="metric-foot">{latest ? `From ${latest.device_id}` : "No sensor data yet"}</div></article>
      </section>

      {message && <div className="notice" role="status">{message}</div>}

      <section className="content-grid">
        <article className="panel readings-panel"><div className="panel-heading"><div><div className="eyebrow">TELEMETRY FEED</div><h2>Recent readings</h2></div><button className="button subtle" onClick={refresh}>Refresh ↻</button></div>
          <div className="table-wrap"><table><thead><tr><th>DEVICE</th><th>TEMP</th><th>HUMIDITY</th><th>BATTERY</th><th>SEQ</th><th>TIME</th></tr></thead><tbody>
            {readings.slice(0, 8).map((row) => <tr key={`${row.device_id}-${row.sequence}`}><td><span className="device-dot" />{row.device_id}</td><td>{row.temperature}°C</td><td>{row.humidity}%</td><td><span className="battery"><i style={{ width: `${row.battery}%` }} /></span>{row.battery}%</td><td className="mono">{row.sequence}</td><td className="muted">{formatTime(row.timestamp)}</td></tr>)}
            {!readings.length && <tr><td className="empty" colSpan="6">No readings yet. Generate one to begin the demo.</td></tr>}
          </tbody></table></div>
        </article>

        <article className="panel attack-panel"><div className="eyebrow">SECURITY LAB</div><h2>Attack simulation</h2><p>Send a test packet through the backend receiver and inspect its response.</p>
          <label className="field-label" htmlFor="device">DEVICE ID</label><input id="device" value={deviceId} onChange={(event) => setDeviceId(event.target.value)} />
          <label className="field-label" htmlFor="attack">ATTACK TYPE</label><select id="attack" value={attack} onChange={(event) => setAttack(event.target.value)}><option value="tampering">Ciphertext tampering</option><option value="replay">Replay attack</option><option value="injection">Unauthorized injection</option><option value="modification">Metadata modification</option><option value="eavesdropping">Eavesdropping</option></select>
          <button className="button danger" disabled={busy} onClick={() => perform("attacks", { attack, device_id: deviceId, device_name: "Attack test" })}>Run security test <span>↗</span></button>
          {report?.path === "attacks" && <div className="report"><b>{report.result.attack.replaceAll("_", " ")}</b><span>{report.result.actual_outcome} · {report.result.detected ? "detected" : "not detected"}</span>{report.result.attack === "eavesdropping" && <pre>{JSON.stringify(report.result.payload, null, 2)}</pre>}</div>}
        </article>
      </section>

      <section className="bottom-grid">
        <article className="panel events-panel"><div className="panel-heading"><div><div className="eyebrow">AUDIT TRAIL</div><h2>Security events</h2></div><span className="count-pill">{events.length} events</span></div>
          <div className="event-list">{events.slice(0, 5).map((row) => <div className="event-row" key={row.id}><span className={`event-icon ${row.severity === "info" ? "safe" : "alert"}`}>{row.severity === "info" ? "✓" : "!"}</span><div><b>{row.event_type.replaceAll("_", " ")}</b><small>{row.device_id || "system"} · {row.description}</small></div><time>{formatTime(row.timestamp)}</time></div>)}{!events.length && <div className="empty events-empty">No security events recorded.</div>}</div>
        </article>
        <article className="panel benchmark-panel"><div className="eyebrow">PERFORMANCE</div><h2>Crypto benchmark</h2><p>Run a fresh measurement on the backend service.</p><div className="benchmark-number">100 <small>iterations</small></div><button className="button subtle full" disabled={busy} onClick={() => perform("benchmark", { iterations: 100, payload_bytes: 256 })}>Run 100-message benchmark</button><div className="security-note"><span>i</span> DES is obsolete; this is an academic simulation.</div>{report?.path === "benchmark" && <pre className="report-json">{JSON.stringify(report.result, null, 2)}</pre>}</article>
      </section>

      <footer><span>DES IoT SECURITY CONSOLE</span><span>DES-CBC · HMAC-SHA256 · MQTT QoS 1</span></footer>
    </main>
  );
}
