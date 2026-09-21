// 프로젝트 목록: 항목을 추가하려면 이 배열에 객체 하나만 더하면 됩니다.
// 링크는 실제 GitHub/배포 주소가 정해지면 교체하세요.
const PROJECTS = [
  {
    title: "뱀 게임 (Python)",
    desc: "사람과 AI 뱀이 사과를 두고 경쟁하는 tkinter 게임. AI는 BFS 길찾기로 사과를 찾습니다.",
    tech: ["Python", "tkinter", "BFS"],
    links: [{ label: "소스 보기", href: "../snake.py" }],
  },
  {
    title: "테트리스 (HTML5)",
    desc: "Canvas 기반 브라우저 테트리스. 고스트 블록, 하드 드롭, 레벨 시스템을 지원합니다.",
    tech: ["HTML5", "CSS3", "JavaScript"],
    links: [{ label: "데모 실행", href: "../Game01/tetris.html" }],
  },
];

document.documentElement.classList.add("js");

// 프로젝트 카드 렌더링 (textContent 사용으로 안전하게 생성)
function renderProjects() {
  const grid = document.getElementById("projectGrid");
  PROJECTS.forEach(p => {
    const card = document.createElement("article");
    card.className = "card";

    const h3 = document.createElement("h3");
    h3.textContent = p.title;
    const desc = document.createElement("p");
    desc.textContent = p.desc;

    const chips = document.createElement("ul");
    chips.className = "chips";
    p.tech.forEach(t => {
      const li = document.createElement("li");
      li.textContent = t;
      chips.appendChild(li);
    });

    const links = document.createElement("div");
    links.className = "card-links";
    p.links.forEach(l => {
      const a = document.createElement("a");
      a.href = l.href;
      a.textContent = l.label + " →";
      a.target = "_blank";
      a.rel = "noopener";
      links.appendChild(a);
    });

    card.append(h3, desc, chips, links);
    grid.appendChild(card);
  });
}

// 테마 전환 (저장된 값 > 시스템 설정)
function initTheme() {
  const root = document.documentElement;
  const btn = document.getElementById("themeBtn");
  const isDark = () =>
    root.dataset.theme
      ? root.dataset.theme === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;

  btn.addEventListener("click", () => {
    const next = isDark() ? "light" : "dark";
    root.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
  });
}

// 스크롤 시 섹션 등장 + 현재 섹션 메뉴 강조
function initScroll() {
  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add("visible");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add("visible"));
  }

  const links = document.querySelectorAll(".menu a");
  const sections = [...links].map(a => document.querySelector(a.getAttribute("href")));
  if ("IntersectionObserver" in window) {
    const spy = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        links.forEach(a => a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id));
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    sections.forEach(s => s && spy.observe(s));
  }
}

// 이메일 복사
function initCopy() {
  const btn = document.getElementById("copyBtn");
  const toast = document.getElementById("toast");
  const email = document.getElementById("mailLink").textContent.trim();
  let timer;

  const show = msg => {
    toast.textContent = msg;
    clearTimeout(timer);
    timer = setTimeout(() => (toast.textContent = ""), 2500);
  };

  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(email);
      show("이메일 주소를 복사했습니다.");
    } catch (e) {
      // 클립보드 API를 쓸 수 없는 환경(file:// 등) 대비
      const ta = document.createElement("textarea");
      ta.value = email;
      document.body.appendChild(ta);
      ta.select();
      const ok = document.execCommand("copy");
      ta.remove();
      show(ok ? "이메일 주소를 복사했습니다." : "복사에 실패했습니다. 직접 선택해 복사해 주세요.");
    }
  });
}

renderProjects();
initTheme();
initScroll();
initCopy();
