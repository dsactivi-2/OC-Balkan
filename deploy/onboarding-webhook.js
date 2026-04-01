/**
 * OpenClaw Balkan — Onboarding Webhook Server
 *
 * Empfaengt HTTP-Webhooks von n8n und startet Deployments.
 * Port: 3099 (konfigurierbar via PORT env var)
 *
 * Endpunkte:
 *   POST /deploy   — Neue Kundeninstanz deployen
 *   POST /status   — Status einer Instanz abfragen
 *   POST /remove   — Instanz entfernen
 *
 * Authentifizierung: Bearer-Token via WEBHOOK_AUTH_TOKEN env var
 */

'use strict';

const http = require('http');
const { execFile, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// =============================================================================
// Konfiguration (nur aus Umgebungsvariablen)
// =============================================================================

const CONFIG = {
  port: parseInt(process.env.PORT || '3099', 10),
  host: process.env.HOST || '127.0.0.1',
  // Auth-Token MUSS als Umgebungsvariable gesetzt sein
  authToken: process.env.WEBHOOK_AUTH_TOKEN || '',
  deployScript: path.resolve(__dirname, 'deploy-customer.sh'),
  logDir: path.resolve(__dirname, 'logs'),
  // Max gleichzeitige Deployments
  maxConcurrent: parseInt(process.env.MAX_CONCURRENT || '3', 10),
};

// Laufende Deployments verfolgen
const activeDeployments = new Map();

// =============================================================================
// Logging
// =============================================================================

const logFile = path.join(CONFIG.logDir, `webhook-${datestamp()}.log`);

function datestamp() {
  return new Date().toISOString().slice(0, 10).replace(/-/g, '');
}

function log(level, message, meta = {}) {
  const ts = new Date().toISOString();
  const line = JSON.stringify({ ts, level, message, ...meta });
  process.stdout.write(line + '\n');
  try {
    fs.mkdirSync(CONFIG.logDir, { recursive: true });
    fs.appendFileSync(logFile, line + '\n');
  } catch (_) {
    // Logging-Fehler nicht crashen lassen
  }
}

const logger = {
  info:  (msg, meta) => log('INFO',  msg, meta),
  warn:  (msg, meta) => log('WARN',  msg, meta),
  error: (msg, meta) => log('ERROR', msg, meta),
};

// =============================================================================
// Hilfsfunktionen
// =============================================================================

/** Body eines Requests lesen und als JSON parsen */
function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      // Max 64KB Body
      if (body.length > 65536) {
        req.destroy();
        reject(new Error('Request body zu gross'));
      }
    });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (e) {
        reject(new Error('Ungueltiges JSON'));
      }
    });
    req.on('error', reject);
  });
}

/** HTTP-Antwort senden */
function respond(res, statusCode, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

/** Bearer-Token aus Authorization-Header extrahieren */
function extractToken(req) {
  const header = req.headers['authorization'] || '';
  if (header.startsWith('Bearer ')) return header.slice(7).trim();
  return '';
}

/** Authentifizierung pruefen */
function authenticate(req) {
  if (!CONFIG.authToken) {
    logger.warn('WEBHOOK_AUTH_TOKEN nicht gesetzt — alle Anfragen erlaubt (NICHT fuer Produktion!)');
    return true;
  }
  return extractToken(req) === CONFIG.authToken;
}

/** Eingabe-Validierung fuer Deploy-Request */
function validateDeployPayload(body) {
  const errors = [];
  const validBundles = [
    'social-marketing-team',
    'office-bundle',
    'research-bundle',
    'learning-buddy',
    'solo-agent',
  ];

  if (!body.customer_id || !/^[a-zA-Z0-9_-]{3,50}$/.test(body.customer_id)) {
    errors.push('customer_id fehlt oder ungueltig (3-50 Zeichen, alphanumerisch + _-)');
  }
  if (!body.bundle || !validBundles.includes(body.bundle)) {
    errors.push(`bundle ungueltig. Valide: ${validBundles.join(', ')}`);
  }
  if (!body.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email)) {
    errors.push('email fehlt oder ungueltig');
  }
  if (!body.name || body.name.trim().length < 2) {
    errors.push('name fehlt oder zu kurz');
  }
  return errors;
}

// =============================================================================
// Handler: POST /deploy
// =============================================================================

async function handleDeploy(req, res) {
  let body;
  try {
    body = await readBody(req);
  } catch (e) {
    return respond(res, 400, { error: e.message });
  }

  const errors = validateDeployPayload(body);
  if (errors.length > 0) {
    return respond(res, 422, { error: 'Validierungsfehler', details: errors });
  }

  const { customer_id, bundle, email, name, dry_run = false, skip_ssl = false } = body;

  // Doppeltes Deployment verhindern
  if (activeDeployments.has(customer_id)) {
    return respond(res, 409, {
      error: 'Deployment fuer diese customer_id laeuft bereits',
      customer_id,
    });
  }

  // Max-Concurrent pruefen
  if (activeDeployments.size >= CONFIG.maxConcurrent) {
    return respond(res, 429, {
      error: `Maximale gleichzeitige Deployments (${CONFIG.maxConcurrent}) erreicht`,
    });
  }

  logger.info('Deployment gestartet', { customer_id, bundle });

  // Sofort antworten — Deployment laeuft asynchron
  respond(res, 202, {
    status: 'accepted',
    customer_id,
    message: 'Deployment gestartet. Status via POST /status abrufbar.',
  });

  // Deploy-Script asynchron ausfuehren
  const args = [
    '--customer-id', customer_id,
    '--bundle',      bundle,
    '--email',       email,
    '--name',        name,
  ];
  if (dry_run)   args.push('--dry-run');
  if (skip_ssl)  args.push('--skip-ssl');

  const deployInfo = { customer_id, bundle, started: new Date().toISOString(), pid: null };
  activeDeployments.set(customer_id, deployInfo);

  const proc = spawn('bash', [CONFIG.deployScript, ...args], {
    env: {
      ...process.env,  // LITELLM_MASTER_KEY wird von aussen vererbt
    },
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  deployInfo.pid = proc.pid;
  let stdout = '';
  let stderr = '';

  proc.stdout.on('data', d => { stdout += d; });
  proc.stderr.on('data', d => { stderr += d; });

  proc.on('close', code => {
    activeDeployments.delete(customer_id);
    if (code === 0) {
      logger.info('Deployment erfolgreich', { customer_id, bundle });
    } else {
      logger.error('Deployment fehlgeschlagen', { customer_id, code, stderr: stderr.slice(-500) });
    }
  });

  proc.on('error', err => {
    activeDeployments.delete(customer_id);
    logger.error('Deployment-Prozess Fehler', { customer_id, error: err.message });
  });
}

// =============================================================================
// Handler: POST /status
// =============================================================================

async function handleStatus(req, res) {
  let body;
  try {
    body = await readBody(req);
  } catch (e) {
    return respond(res, 400, { error: e.message });
  }

  const { customer_id } = body;
  if (!customer_id) {
    return respond(res, 422, { error: 'customer_id fehlt' });
  }

  // Laufendes Deployment
  if (activeDeployments.has(customer_id)) {
    const info = activeDeployments.get(customer_id);
    return respond(res, 200, {
      customer_id,
      status: 'deploying',
      started: info.started,
      pid: info.pid,
    });
  }

  // Container-Status via Docker auf rocky2 abfragen
  execFile('ssh', ['rocky2',
    `docker inspect --format='{{.State.Status}}:{{.State.Health.Status}}' 'openclaw_${customer_id}' 2>/dev/null || echo 'not_found:'`
  ], { timeout: 10000 }, (err, stdout) => {
    if (err) {
      return respond(res, 500, { error: 'SSH-Abfrage fehlgeschlagen', detail: err.message });
    }

    const [state, health] = stdout.trim().split(':');

    if (state === 'not_found') {
      return respond(res, 404, { customer_id, status: 'not_deployed' });
    }

    respond(res, 200, {
      customer_id,
      status: 'deployed',
      container_state: state,
      health: health || 'unknown',
    });
  });
}

// =============================================================================
// Handler: POST /remove
// =============================================================================

async function handleRemove(req, res) {
  let body;
  try {
    body = await readBody(req);
  } catch (e) {
    return respond(res, 400, { error: e.message });
  }

  const { customer_id, confirm } = body;
  if (!customer_id) {
    return respond(res, 422, { error: 'customer_id fehlt' });
  }
  if (confirm !== 'DELETE') {
    return respond(res, 422, {
      error: 'Sicherheitsbestaetigung fehlt. Sende confirm: "DELETE"',
    });
  }

  logger.warn('Instanz-Entfernung angefragt', { customer_id });

  // Docker-Container + Volumes stoppen und entfernen (auf rocky2)
  const cmds = [
    `cd /opt/openclaw-balkan/kunden/${customer_id} && docker compose down -v 2>/dev/null || true`,
    `docker network rm net_${customer_id} 2>/dev/null || true`,
    `docker volume rm vol_${customer_id}_data vol_${customer_id}_pg 2>/dev/null || true`,
    `rm -rf /opt/openclaw-balkan/kunden/${customer_id}`,
    `sudo rm -f /etc/nginx/conf.d/${customer_id}.conf`,
    `sudo nginx -s reload`,
  ].join(' && ');

  respond(res, 202, {
    status: 'accepted',
    customer_id,
    message: 'Instanz wird entfernt.',
  });

  execFile('ssh', ['rocky2', cmds], { timeout: 60000 }, (err, stdout, stderr) => {
    if (err) {
      logger.error('Entfernung fehlgeschlagen', { customer_id, error: err.message, stderr });
    } else {
      logger.info('Instanz entfernt', { customer_id });
    }
  });
}

// =============================================================================
// HTTP-Server
// =============================================================================

const ROUTES = {
  'POST /deploy':  handleDeploy,
  'POST /status':  handleStatus,
  'POST /remove':  handleRemove,
};

const server = http.createServer(async (req, res) => {
  const route = `${req.method} ${req.url.split('?')[0]}`;

  // Authentifizierung
  if (!authenticate(req)) {
    logger.warn('Unberechtigter Zugriffsversuch', { ip: req.socket.remoteAddress, route });
    return respond(res, 401, { error: 'Nicht autorisiert' });
  }

  // Routing
  const handler = ROUTES[route];
  if (!handler) {
    return respond(res, 404, { error: `Route nicht gefunden: ${route}` });
  }

  try {
    await handler(req, res);
  } catch (err) {
    logger.error('Unerwarteter Fehler', { route, error: err.message, stack: err.stack });
    if (!res.headersSent) {
      respond(res, 500, { error: 'Interner Serverfehler' });
    }
  }
});

server.on('error', err => {
  logger.error('Server-Fehler', { error: err.message });
  process.exit(1);
});

// Graceful Shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM empfangen — Server wird beendet');
  server.close(() => process.exit(0));
});
process.on('SIGINT', () => {
  logger.info('SIGINT empfangen');
  server.close(() => process.exit(0));
});

// Startup-Validierung
if (!CONFIG.authToken) {
  logger.warn('ACHTUNG: WEBHOOK_AUTH_TOKEN nicht gesetzt — Server ist ungeschuetzt!');
}
if (!fs.existsSync(CONFIG.deployScript)) {
  logger.error('deploy-customer.sh nicht gefunden', { path: CONFIG.deployScript });
  process.exit(1);
}

fs.mkdirSync(CONFIG.logDir, { recursive: true });

server.listen(CONFIG.port, CONFIG.host, () => {
  logger.info('Webhook-Server gestartet', {
    host: CONFIG.host,
    port: CONFIG.port,
    auth: CONFIG.authToken ? 'aktiv' : 'DEAKTIVIERT',
  });
});
