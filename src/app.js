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
      <a class="btn btn-primary" href="#bundlovi">${esc(c.ctaSub)} →</a>
      <a class="btn btn-ghost" href="#kontakt">${esc(c.cta)}</a>
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
          <button class="btn btn-primary bundle-cta" data-bundle="${esc(b.bundleKey)}" data-name="${esc(b.name)}" data-price="${esc(b.price)}">Naruči ${esc(b.name)} →</button>
        </div>
      `).join("")}
    </div>
    <p class="bundle-note">+9 EUR/mj. za svaki dodatni kanal · Godišnji plan: 10 mjeseci plaćate, 12 koristite</p>
  </section>

  <!-- HOW IT WORKS -->
  <section class="section reveal" id="koraci">
    <div class="section-label">Kako radi</div>
    <h2>Od narudžbe do agenta za 5 dana.</h2>
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
      <a class="btn btn-primary" href="#bundlovi" style="font-size:16px; height:52px; padding:0 28px;">Pogledaj bundlove →</a>
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

  <!-- CONTACT (simple, no form — orders handle it now) -->
  <section class="section reveal" id="kontakt">
    <div class="section-label">Kontakt</div>
    <h2>Imate pitanje?</h2>
    <p class="section-intro" style="margin-bottom:32px;">Za narudžbe kliknite "Naruči" na bundlu iznad. Za ostala pitanja:</p>
    <div class="contact-options">
      <div class="contact-card">
        <h3>Email</h3>
        <p style="font-size:15px;">info@openclawbalkan.ba</p>
      </div>
      <div class="contact-card">
        <h3>WhatsApp</h3>
        <p style="font-size:15px;">+387 61 xxx xxx</p>
      </div>
      <div class="contact-card">
        <h3>Viber</h3>
        <p style="font-size:15px;">+387 61 xxx xxx</p>
      </div>
    </div>
  </section>

  <footer>
    <span>${esc(c.footerNote)}</span>
    <a class="nav-switch" href="${c.switchTo.href}" style="font-size:13px;">${esc(c.switchTo.label)}</a>
  </footer>

</main>

<!-- ORDER MODAL -->
<div class="modal-overlay" id="order-modal" hidden>
  <div class="modal">
    <button class="modal-close" id="modal-close" aria-label="Zatvori">&times;</button>
    <div class="modal-badge" id="modal-badge"></div>
    <h2 id="modal-title"></h2>
    <p class="modal-price" id="modal-price"></p>
    <div class="modal-agents" id="modal-agents" hidden></div>
    <form class="order-form" id="order-form">
      <input type="hidden" name="bundle" id="order-bundle" />
      <label>Ime i prezime<input name="name" type="text" required minlength="2" pattern="[^0-9]+" placeholder="npr. Ana Kovačević" /></label>
      <label>Firma<input name="company" type="text" required minlength="2" placeholder="naziv firme" /></label>
      <label>Email<input name="email" type="email" required pattern="[^\\s@]+@[^\\s@]+\\.[^\\s@]+" placeholder="vas@email.ba" /></label>
      <label>Telefon / WhatsApp<input name="phone" type="tel" required pattern="[\\+\\d\\s\\-\\(\\)]{8,}" placeholder="+387 61 ..." /></label>
      <div class="hp-field" aria-hidden="true">
        <label>Website<input name="website" type="text" tabindex="-1" autocomplete="off" /></label>
      </div>
      <label>Tip biznisa
        <select name="businessType">
          <option value="">Izaberi (opciono)</option>
          <option value="salon">Salon / frizerski</option>
          <option value="restaurant">Restoran / kafić</option>
          <option value="office">Ordinacija / kancelarija</option>
          <option value="education">Škola / edukacija</option>
          <option value="freelancer">Freelancer</option>
          <option value="other">Drugo</option>
        </select>
      </label>
      <label>Željeni kanal za komunikaciju
        <select name="preferredChannel" required>
          <option value="whatsapp">WhatsApp</option>
          <option value="viber">Viber</option>
          <option value="email">Email</option>
        </select>
      </label>
      <label>Napomena (opciono)<textarea name="message" rows="2" placeholder="Bilo šta što nam može pomoći u setupu..."></textarea></label>
      <button class="btn btn-primary" type="submit" style="width:100%; height:52px; font-size:16px; justify-content:center;">Naruči →</button>
      <p class="form-status" id="order-status" aria-live="polite"></p>
    </form>
    <div class="order-success" id="order-success" hidden>
      <div class="success-icon">✓</div>
      <h3>Narudžba primljena!</h3>
      <p class="order-ref" id="order-ref-display"></p>
      <p>Naš onboarding agent će vas kontaktirati u roku od 24 sata preko vašeg odabranog kanala da dogovorimo setup.</p>
      <button class="btn btn-ghost" id="modal-done" style="width:100%; justify-content:center; margin-top:16px;">Zatvori</button>
    </div>
  </div>
</div>
`;
}

function enhancePage() {
  // Smooth scrolling
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      const id = link.getAttribute("href");
      const target = id ? document.querySelector(id) : null;
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  // Reveal animations
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

  // ── Order Modal ─────────────────────────────────────────────
  const modal = document.getElementById("order-modal");
  const modalClose = document.getElementById("modal-close");
  const modalDone = document.getElementById("modal-done");
  const modalBadge = document.getElementById("modal-badge");
  const modalTitle = document.getElementById("modal-title");
  const modalPrice = document.getElementById("modal-price");
  const orderForm = document.getElementById("order-form");
  const orderBundle = document.getElementById("order-bundle");
  const orderStatus = document.getElementById("order-status");
  const orderSuccess = document.getElementById("order-success");
  const orderRefDisplay = document.getElementById("order-ref-display");

  if (!modal || !orderForm) return;

  function openModal(bundleKey, bundleName, bundlePrice) {
    orderBundle.value = bundleKey;
    modalBadge.textContent = bundlePrice + " EUR / mj.";
    modalTitle.textContent = bundleName;
    modalPrice.textContent = `Naručujete: ${bundleName}`;

    // Show agents included in this bundle
    const agentsList = document.getElementById("modal-agents");
    if (agentsList) {
      const bundleCard = document.querySelector(`.bundle-cta[data-bundle="${bundleKey}"]`);
      if (bundleCard) {
        const card = bundleCard.closest(".bundle-card");
        const agents = card ? card.querySelectorAll(".bundle-agents li") : [];
        if (agents.length > 0) {
          agentsList.innerHTML = `<span class="modal-agents-label">Uključeni agenti:</span> ` +
            Array.from(agents).map((a) => `<span class="modal-agent-tag">${a.textContent}</span>`).join("");
          agentsList.hidden = false;
        } else {
          agentsList.hidden = true;
        }
      }
    }

    orderForm.style.display = "";
    orderSuccess.hidden = true;
    orderStatus.textContent = "";
    modal.hidden = false;
    document.body.style.overflow = "hidden";
  }

  function closeModal() {
    modal.hidden = true;
    document.body.style.overflow = "";
    orderForm.reset();
  }

  // Bundle card buttons
  document.querySelectorAll(".bundle-cta[data-bundle]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      openModal(btn.dataset.bundle, btn.dataset.name, btn.dataset.price);
    });
  });

  modalClose.addEventListener("click", closeModal);
  if (modalDone) modalDone.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.hidden) closeModal();
  });

  // Order form submit
  orderForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!(orderForm instanceof HTMLFormElement)) return;

    const data = Object.fromEntries(new FormData(orderForm).entries());

    // Required fields check
    const required = ["name", "company", "email", "phone", "bundle"];
    if (required.some((f) => !String(data[f] || "").trim())) {
      orderStatus.textContent = "Popunite obavezna polja.";
      orderStatus.className = "form-status error";
      return;
    }

    // Name: min 2 chars, no numbers
    const name = String(data.name).trim();
    if (name.length < 2 || /\d/.test(name)) {
      orderStatus.textContent = "Unesite ispravno ime i prezime.";
      orderStatus.className = "form-status error";
      return;
    }

    // Company: min 2 chars
    if (String(data.company).trim().length < 2) {
      orderStatus.textContent = "Unesite naziv firme (min. 2 znaka).";
      orderStatus.className = "form-status error";
      return;
    }

    // Email: must contain @ and a dot after @
    const email = String(data.email).trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      orderStatus.textContent = "Unesite ispravnu email adresu (npr. ime@firma.ba).";
      orderStatus.className = "form-status error";
      return;
    }

    // Phone: must be digits, spaces, +, -, (, ) — min 8 digits
    const phone = String(data.phone).trim();
    const phoneDigits = phone.replace(/\D/g, "");
    if (phoneDigits.length < 8 || /[a-zA-Z]/.test(phone)) {
      orderStatus.textContent = "Unesite ispravan broj telefona (min. 8 cifara, npr. +387 61 123 456).";
      orderStatus.className = "form-status error";
      return;
    }

    orderStatus.textContent = "Šaljem narudžbu...";
    orderStatus.className = "form-status";

    const submitBtn = orderForm.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.disabled = true;

    fetch("/api/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...data,
        market: document.documentElement.lang === "sr" ? "rs" : "ba",
        page: location.pathname,
      }),
    })
      .then(async (response) => {
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.error || "Order failed");
        }
        return response.json();
      })
      .then((result) => {
        orderForm.style.display = "none";
        orderRefDisplay.textContent = `Referenca: ${result.orderRef}`;
        orderSuccess.hidden = false;
      })
      .catch((err) => {
        orderStatus.textContent = err.message || "Greška pri slanju. Pokušajte ponovo.";
        orderStatus.className = "form-status error";
        if (submitBtn) submitBtn.disabled = false;
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
