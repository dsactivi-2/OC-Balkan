export const markets = {
  ba: {
    lang: "bs",
    locale: "Bosna i Hercegovina",
    flag: "🇧🇦",
    switchTo: { href: "/rs.html", label: "Srbija 🇷🇸" },
    nav: ["Use Cases", "Paketi", "Pilot", "Kontakt"],
    badge: "AI Agenti · BiH",
    title: ["Manje izgubljenih upita.", "Brži odgovori."],
    titleAccent: "Manje izgubljenih upita.",
    sub: "OpenClaw Balkan postavlja AI agente za lokalne firme u Bosni i Hercegovini — poruke, rezervacije i upiti na autopilotu.",
    cta: "Zatraži demo",
    ctaSub: "Pogledaj pakete",
    kpis: [
      ["24/7", "dostupnost"],
      ["3", "kanala (WA, Messenger, Viber)"],
      ["14 dana", "pilot iteracija"],
    ],

    usecases: [
      {
        icon: "✂️",
        title: "Frizerski salon",
        scenario: "30+ rezervacija tjedno via WhatsApp",
        desc: "Agent prima rezervacije, šalje potvrde i podsjetnike — tim ne mora odgovarati na svaku poruku.",
        result: "−80% manualnih poruka · 0 izgubljenih termina",
      },
      {
        icon: "🍽️",
        title: "Restoran / kafić",
        scenario: "Rezervacije stolova + pitanja o meniju",
        desc: "Agent odgovara na pitanja o radno vijeme, meniju i raspoloživosti stola — bez prekidanja kuhinje ili šanka.",
        result: "Odgovor u sekundi · više rezervacija",
      },
      {
        icon: "🏢",
        title: "Ordinacija / kancelarija",
        scenario: "Kvalifikacija upita, termini, prosljeđivanje",
        desc: "Agent prima upit, pita osnovna pitanja i prosljeđuje timu samo one koji trebaju odgovor čovjeka.",
        result: "Manje telefonskih prekida · uredni inbox",
      },
    ],

    steps: [
      {
        num: "01",
        title: "Setup za 3-5 dana",
        desc: "Konfigurišemo agenta na vašim kanalima — bez razvoja, bez IT tima sa vaše strane.",
      },
      {
        num: "02",
        title: "14 dana pilot",
        desc: "Pratimo stvarne upite, fino podešavamo odgovore i provjeravamo da li agent radi kako treba.",
      },
      {
        num: "03",
        title: "Naplata tek kad radi",
        desc: "Pilot je jasno ograničen. Ne plaćate dok ne vidite da agent donosi vrijednost.",
      },
    ],

    packageA: {
      name: "Local Inbox",
      tag: "Za start",
      desc: "Za frizerske salone, beauty studije, restorane i manje uslužne biznise.",
      items: [
        "1 kanal (WhatsApp ili Messenger)",
        "FAQ odgovori na vaš jezik",
        "Prijem rezervacija i upita",
        "Eskalacija ka timu kad treba",
      ],
      price: "19–39 EUR / mj.",
      setup: "Postavka: 99–199 EUR",
    },
    packageB: {
      name: "Business Front Desk",
      tag: "Za timove",
      desc: "Za ordinacije, kancelarije, agencije i B2B firme sa više komunikacijskih kanala.",
      items: [
        "2 kanala (WhatsApp + Messenger ili Viber)",
        "FAQ + kvalifikacija upita",
        "Prosljeđivanje u inbox ili CRM",
        "Mjesečni pregled rezultata",
      ],
      price: "39–69 EUR / mj.",
      setup: "Postavka: 149–299 EUR",
    },

    pilotTitle: "Tražimo prve pilot-klijente.",
    pilotDesc: "Ograničen broj mjesta. Postavljamo uz vas, ne umjesto vas.",
    pilotItems: ["Postavljanje uz vaš tim", "14 dana fokusirane iteracije", "Jasan pilot scope", "Povoljniji ulaz uz feedback"],

    faq: [
      ["Da li radi na bosanskom?", "Da. Agent je konfigurisan sa BKS slojem i lokalnim formulacijama za BiH."],
      ["Da li mi treba sajt?", "Ne. Za većinu firmi su dovoljni WhatsApp, Messenger ili Viber."],
      ["Je li ovo zamjena za zaposlenog?", "Ne. Preuzima prvi sloj komunikacije i smanjuje opterećenje tima."],
      ["Kako se plaća?", "Jednostavan model — faktura i dogovoreni setup, bez skrivenih troškova."],
    ],

    contactBlurb: "Pošalji osnovne podatke i javimo se sa kratkom procjenom da li je pilot fit.",
    nextSteps: [
      "Kratka procjena (fit ili ne)",
      "Prijedlog paketa bez prodajnog pritiska",
      "Jasan sljedeći korak",
    ],
    footerNote: "Radna prodajna stranica za validaciju ponude. OpenClaw Balkan · BiH",
  },

  rs: {
    lang: "sr",
    locale: "Srbija",
    flag: "🇷🇸",
    switchTo: { href: "/ba.html", label: "BiH 🇧🇦" },
    nav: ["Use Cases", "Paketi", "Pilot", "Kontakt"],
    badge: "AI Agenti · Srbija",
    title: ["Manje izgubljenih upita.", "Brži odgovori."],
    titleAccent: "Manje izgubljenih upita.",
    sub: "OpenClaw Balkan postavlja AI agente za lokalne firme u Srbiji — poruke, rezervacije i upiti na autopilotu.",
    cta: "Zatraži demo",
    ctaSub: "Pogledaj pakete",
    kpis: [
      ["24/7", "dostupnost"],
      ["3", "kanala (WA, Messenger, Viber)"],
      ["14 dana", "pilot iteracija"],
    ],

    usecases: [
      {
        icon: "✂️",
        title: "Frizerski salon",
        scenario: "30+ rezervacija nedeljno via WhatsApp",
        desc: "Agent prima rezervacije, šalje potvrde i podsetrike — tim ne mora da odgovara na svaku poruku.",
        result: "−80% manualnih poruka · 0 izgubljenih termina",
      },
      {
        icon: "🍽️",
        title: "Restoran / kafić",
        scenario: "Rezervacije stolova + pitanja o meniju",
        desc: "Agent odgovara na pitanja o radnom vremenu, meniju i raspoloživosti stola — bez prekidanja kuhinje.",
        result: "Odgovor za sekundu · više rezervacija",
      },
      {
        icon: "🏢",
        title: "Ordinacija / kancelarija",
        scenario: "Kvalifikacija upita, termini, prosleđivanje",
        desc: "Agent prima upit, pita osnovna pitanja i prosleđuje timu samo one koji zahtevaju odgovor čoveka.",
        result: "Manje telefonskih prekida · uredan inbox",
      },
    ],

    steps: [
      {
        num: "01",
        title: "Setup za 3-5 dana",
        desc: "Konfigurišemo agenta na vašim kanalima — bez razvoja, bez IT tima sa vaše strane.",
      },
      {
        num: "02",
        title: "14 dana pilot",
        desc: "Pratimo stvarne upite, fino podešavamo odgovore i proveravamo da li agent radi kako treba.",
      },
      {
        num: "03",
        title: "Naplata tek kad radi",
        desc: "Pilot je jasno ograničen. Ne plaćate dok ne vidite da agent donosi vrednost.",
      },
    ],

    packageA: {
      name: "Local Inbox",
      tag: "Za start",
      desc: "Za frizerske salone, beauty studije, restorane i manje uslužne biznise.",
      items: [
        "1 kanal (WhatsApp ili Messenger)",
        "FAQ odgovori na srpskom",
        "Prijem rezervacija i upita",
        "Eskalacija ka timu kad treba",
      ],
      price: "25–45 EUR / mes.",
      setup: "Postavka: 99–199 EUR",
    },
    packageB: {
      name: "Business Front Desk",
      tag: "Za timove",
      desc: "Za ordinacije, kancelarije, agencije i B2B firme sa više komunikacionih kanala.",
      items: [
        "2 kanala (WhatsApp + Messenger ili Viber)",
        "FAQ + kvalifikacija upita",
        "Prosleđivanje u inbox ili CRM",
        "Mesečni pregled rezultata",
      ],
      price: "49–79 EUR / mes.",
      setup: "Postavka: 149–299 EUR",
    },

    pilotTitle: "Tražimo prve pilot-klijente.",
    pilotDesc: "Ograničen broj mesta. Postavljamo uz vas, ne umesto vas.",
    pilotItems: ["Postavljanje uz vaš tim", "14 dana fokusirane iteracije", "Jasan pilot scope", "Povoljniji ulaz uz feedback"],

    faq: [
      ["Da li radi na srpskom?", "Da. Agent je konfigurisan sa lokalnim formulacijama za srpsko tržište."],
      ["Da li mi treba sajt?", "Ne. Za većinu firmi su dovoljni WhatsApp, Messenger ili Viber."],
      ["Je li ovo zamena za zaposlenog?", "Ne. Preuzima prvi sloj komunikacije i smanjuje opterećenje tima."],
      ["Kako se plaća?", "Jednostavan model — faktura i dogovoreni setup, bez skrivenih troškova."],
    ],

    contactBlurb: "Pošalji osnovne podatke i javimo se sa kratkom procenom da li je pilot fit.",
    nextSteps: [
      "Kratka procena (fit ili ne)",
      "Predlog paketa bez prodajnog pritiska",
      "Jasan sledeći korak",
    ],
    footerNote: "Radna prodajna stranica za validaciju ponude. OpenClaw Balkan · Srbija",
  },
};
