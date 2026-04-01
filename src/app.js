import { markets } from "./content.js";

function esc(str) {
  return String(str || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function liItems(items) {
  return items.map((i) => `<li>${esc(i)}</li>`).join("");
}

function markup(c) {
  return `
<nav class="nav">
  <div class="nav-brand">
    <span class="dot"></span>
    OpenClaw Balkan
  </div>
  <div class="nav-links">
    ${c.nav.map((n, i) => `<a href="#${["usecases","paketi","pilot","kontakt"][i]}">${esc(n)}</a>`).join("")}
  </div>
  <a class="nav-switch" href="${c.switchTo.href}">${esc(c.switchTo.label)}</a>
</nav>

<main class="page">

  <!-- HERO -->
  <section class="hero reveal">
    <div class="badge"><span class="dot"></span>${esc(c.badge)}</div>
    <h1>${esc(c.title[0])}<br><em>${esc(c.title[1])}</em></h1>
    <p class="hero-sub">${esc(c.sub)}</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="#kontakt">${esc(c.cta)} →</a>
      <a class="btn btn-ghost" href="#paketi">${esc(c.ctaSub)}</a>
    </div>
    <div class="kpi-row">
      ${c.kpis.map(([v, t]) => `
        <div class="kpi">
          <strong>${esc(v)}</strong>
          <span>${esc(t)}</span>
        </div>
      `).join("")}
    </div>
  </section>

  <!-- USE CASES -->
  <section class="section reveal" id="usecases">
    <div class="section-label">Use Cases</div>
    <h2>Šta agent stvarno radi.</h2>
    <p class="section-intro">Konkretni primjeri iz svakodnevnog poslovanja — ne teorija.</p>
    <div class="usecase-grid">
      ${c.usecases.map((u) => `
        <div class="usecase-card">
          <span class="usecase-icon">${u.icon}</span>
          <h3>${esc(u.title)}</h3>
          <div class="scenario">${esc(u.scenario)}</div>
          <p>${esc(u.desc)}</p>
          <div class="result">${esc(u.result)}</div>
        </div>
      `).join("")}
    </div>
  </section>

  <!-- HOW IT WORKS -->
  <section class="section reveal">
    <div class="section-label">Kako funkcioniše</div>
    <h2>Od dogovora do agenta za 5 dana.</h2>
    <p class="section-intro" style="margin-bottom: 28px;">Bez IT projekata, bez dugih implementacija.</p>
    <div class="steps">
      ${c.steps.map((s) => `
        <div class="step">
          <div class="step-num">Korak ${s.num}</div>
          <h3>${esc(s.title)}</h3>
          <p>${esc(s.desc)}</p>
        </div>
      `).join("")}
    </div>
  </section>

  <!-- PACKAGES -->
  <section class="section reveal" id="paketi">
    <div class="section-label">Paketi</div>
    <h2>Dvije opcije. Jasne cijene.</h2>
    <p class="section-intro" style="margin-bottom: 28px;">Počinjemo konzervativno — širimo se kad vidite vrijednost.</p>
    <div class="pkg-grid">
      <div class="pkg-card">
        <span class="pkg-tag">${esc(c.packageA.tag)}</span>
        <h3>${esc(c.packageA.name)}</h3>
        <p class="pkg-desc">${esc(c.packageA.desc)}</p>
        <ul>${liItems(c.packageA.items)}</ul>
        <div class="pkg-price">${esc(c.packageA.price)}</div>
        <div class="pkg-setup">${esc(c.packageA.setup)}</div>
        <a class="btn btn-ghost" href="#kontakt" style="width:100%; justify-content:center;">Zatraži demo</a>
      </div>
      <div class="pkg-card featured">
        <span class="pkg-tag">${esc(c.packageB.tag)}</span>
        <h3>${esc(c.packageB.name)}</h3>
        <p class="pkg-desc">${esc(c.packageB.desc)}</p>
        <ul>${liItems(c.packageB.items)}</ul>
        <div class="pkg-price">${esc(c.packageB.price)}</div>
        <div class="pkg-setup">${esc(c.packageB.setup)}</div>
        <a class="btn btn-primary" href="#kontakt" style="width:100%; justify-content:center;">Zatraži demo →</a>
      </div>
    </div>
  </section>

  <!-- PILOT -->
  <section class="section reveal" id="pilot">
    <div class="pilot-panel">
      <div class="section-label" style="margin-bottom:16px;">${esc(c.badge)} · Pilot Program</div>
      <h2>${esc(c.pilotTitle)}</h2>
      <p>${esc(c.pilotDesc)}</p>
      <div class="pilot-items">
        ${c.pilotItems.map((i) => `<span class="pilot-item">${esc(i)}</span>`).join("")}
      </div>
      <a class="btn btn-primary" href="#kontakt" style="font-size:16px; height:52px; padding:0 28px;">${esc(c.cta)} →</a>
    </div>
  </section>

  <!-- FAQ -->
  <section class="section reveal">
    <div class="section-label">FAQ</div>
    <h2>Osnovna pitanja.</h2>
    <div class="grid-2" style="margin-top:28px;">
      ${c.faq.map(([q, a]) => `
        <div class="card">
          <h3 style="font-size:16px; margin-bottom:8px;">${esc(q)}</h3>
          <p>${esc(a)}</p>
        </div>
      `).join("")}
    </div>
  </section>

  <!-- CONTACT -->
  <section class="section reveal" id="kontakt">
    <div class="section-label">Kontakt</div>
    <h2>Zatraži demo ili pilot procjenu.</h2>
    <p class="section-intro" style="margin-bottom:32px;">${esc(c.contactBlurb)}</p>
    <div class="contact-grid">
      <form class="lead-form" id="lead-form" novalidate>
        <label>Ime i prezime<input name="name" type="text" required placeholder="npr. Ana Kovačević" /></label>
        <label>Firma<input name="company" type="text" required placeholder="naziv firme" /></label>
        <label>Email<input name="email" type="email" required placeholder="vas@email.ba" /></label>
        <label>Telefon / WhatsApp<input name="phone" type="text" placeholder="+387 61 ..." /></label>
        <div class="hp-field" aria-hidden="true">
          <label>Website<input name="website" type="text" tabindex="-1" autocomplete="off" /></label>
        </div>
        <label>Tip biznisa
          <select name="segment" required>
            <option value="">Izaberi</option>
            <option value="beauty">Beauty / frizer</option>
            <option value="restaurant">Restoran / kafić</option>
            <option value="office">Ordinacija / kancelarija</option>
            <option value="other">Drugo</option>
          </select>
        </label>
        <label>Šta želiš riješiti?<textarea name="message" rows="4" required placeholder="Kratki opis situacije..."></textarea></label>
        <button class="btn btn-primary" type="submit" style="width:100%; height:48px; font-size:15px; justify-content:center;">Pošalji upit →</button>
        <p class="form-status" id="form-status" aria-live="polite"></p>
      </form>
      <div class="contact-side">
        <div class="contact-card">
          <h3>Šta ide dalje</h3>
          <ul>${liItems(c.nextSteps)}</ul>
        </div>
        <div class="contact-card" style="background: rgba(62,207,142,0.04); border-color: rgba(62,207,142,0.2);">
          <h3 style="font-size:14px; color: var(--muted); margin-bottom:10px;">Direktno</h3>
          <p style="font-size:14px;">Možeš nas kontaktirati i direktno via WhatsApp ili Messenger. Isti odgovor, isti tim.</p>
        </div>
      </div>
    </div>
  </section>

  <footer>
    <span>${esc(c.footerNote)}</span>
    <a class="nav-switch" href="${c.switchTo.href}" style="font-size:13px;">${esc(c.switchTo.label)}</a>
  </footer>

</main>
`;
}

function enhancePage() {
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const id = link.getAttribute("href");
      const target = id ? document.querySelector(id) : null;
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08 }
  );
  document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

  const form = document.getElementById("lead-form");
  const status = document.getElementById("form-status");
  if (!form || !status) return;

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!(form instanceof HTMLFormElement)) return;

    const data = Object.fromEntries(new FormData(form).entries());
    const required = ["name", "company", "email", "segment", "message"];
    if (required.some((f) => !String(data[f] || "").trim())) {
      status.textContent = "Popuni obavezna polja.";
      status.className = "form-status error";
      return;
    }

    status.textContent = "Slanje u toku...";
    status.className = "form-status";

    fetch("/api/leads", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...data,
        page: location.pathname,
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.error || "Submit failed");
        }

        form.reset();
        status.textContent = "✓ Upit sačuvan. Javimo se uskoro.";
        status.className = "form-status success";
      })
      .catch(() => {
        status.textContent = "Slanje nije uspelo. Proveri da li radi produkcijski server.";
        status.className = "form-status error";
      });
  });
}

export function renderSite(market) {
  const c = markets[market];
  if (!c) throw new Error(`Unknown market: ${market}`);
  document.documentElement.lang = c.lang;
  document.title = `OpenClaw Balkan · ${c.locale}`;
  document.getElementById("app").innerHTML = markup(c);
  enhancePage();
}
