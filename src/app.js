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
    ${c.nav.map((n, i) => `<a href="#${["bundlovi","koraci","pilot","kontakt"][i]}">${esc(n)}</a>`).join("")}
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
      <a class="btn btn-ghost" href="#bundlovi">${esc(c.ctaSub)}</a>
    </div>
    <div class="trust-row">
      <span class="trust-item">24/7 dostupnost</span>
      <span class="trust-item">Setup za 3–5 dana</span>
      <span class="trust-item">Bez ugovora na godinu</span>
      <span class="trust-item">Od 25 EUR/mj.</span>
    </div>
  </section>

  <!-- BUNDLES -->
  <section class="section reveal" id="bundlovi">
    <div class="section-label">Bundlovi</div>
    <h2>Izaberite paket za vaš biznis.</h2>
    <p class="section-intro">5 gotovih paketa — svaki sa specijalizovanim AI agentima. Od jednog agenta do kompletnog tima.</p>
    <div class="bundle-grid">
      ${c.bundles.map((b) => `
        <div class="bundle-card${b.featured ? " featured" : ""}">
          ${b.featured ? '<span class="bundle-popular">Najpopularniji</span>' : ""}
          <div class="bundle-header">
            <span class="bundle-icon">${b.icon}</span>
            <span class="bundle-tag">${esc(b.tag)}</span>
          </div>
          <h3>${esc(b.name)}</h3>
          <div class="bundle-price"><span class="price-num">${esc(b.price)}</span> <span class="price-period">${esc(b.period)}</span></div>
          <p class="bundle-target">${esc(b.target)}</p>
          <p class="bundle-desc">${esc(b.desc)}</p>
          <div class="bundle-agents">
            <span class="agents-label">Agenti:</span>
            <ul>${b.agents.map((a) => `<li>${esc(a)}</li>`).join("")}</ul>
          </div>
          <div class="bundle-channels">${esc(b.channels)}</div>
          <a class="btn btn-primary bundle-cta" href="#kontakt">${esc(c.cta)} →</a>
        </div>
      `).join("")}
    </div>
    <p class="bundle-note">+9 EUR/mj. za svaki dodatni kanal · Godišnji plan: 10 mjeseci plaćate, 12 koristite</p>
  </section>

  <!-- HOW IT WORKS -->
  <section class="section reveal" id="koraci">
    <div class="section-label">Kako radi</div>
    <h2>Od dogovora do agenta za 5 dana.</h2>
    <p class="section-intro" style="margin-bottom: 28px;">Bez IT projekata. Bez dugih implementacija.</p>
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
    <div class="faq-grid" style="margin-top:28px;">
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
        <label>Koji bundle vas zanima?
          <select name="segment" required>
            <option value="">Izaberi</option>
            <option value="solo">Solo Agent (25 EUR)</option>
            <option value="learning">Learning Buddy (29 EUR)</option>
            <option value="marketing">Social Marketing Team (39 EUR)</option>
            <option value="research">Research Bundle (49 EUR)</option>
            <option value="office">Office Bundle (79 EUR)</option>
            <option value="unsure">Nisam siguran/a</option>
          </select>
        </label>
        <label>Šta želite riješiti?<textarea name="message" rows="3" required placeholder="Kratki opis situacije..."></textarea></label>
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
          <p style="font-size:14px;">Možete nas kontaktirati i direktno via WhatsApp ili Messenger.</p>
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
        status.textContent = "Slanje nije uspelo. Pokušajte ponovo ili nas kontaktirajte direktno.";
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
