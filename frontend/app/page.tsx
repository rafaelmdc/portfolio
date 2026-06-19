import { getSiteBundle, getProjects } from "@/lib/api";
import type { HomeSection, HomeSectionType } from "@/lib/types";

// Rendered at request time against the backend Service (no API access needed at
// image-build time). The backend caches GitHub stats, so this stays cheap.
export const dynamic = "force-dynamic";

import Nav, { type NavLink } from "@/components/Nav";
import ScrollProgress from "@/components/ScrollProgress";
import Hero from "@/components/sections/Hero";
import About from "@/components/sections/About";
import Skills from "@/components/sections/Skills";
import Timeline from "@/components/sections/Timeline";
import Work from "@/components/sections/Work";
import Research from "@/components/sections/Research";
import Contact from "@/components/sections/Contact";
import Gallery from "@/components/sections/Gallery";
import Carousel from "@/components/sections/Carousel";

// Marker sections appear in the navbar (in order); gallery/carousel do not.
const NAV_TYPES: HomeSectionType[] = [
  "about",
  "skills",
  "timeline",
  "work",
  "research",
  "contact",
];
const NAV_LABEL: Record<string, string> = {
  about: "about",
  skills: "skills",
  timeline: "timeline",
  work: "work",
  research: "research",
  contact: "contact",
};

export default async function Home() {
  const [bundle, projects] = await Promise.all([getSiteBundle(), getProjects()]);

  // Fall back to a sensible default order if the CMS has no sections yet.
  const sections: HomeSection[] =
    bundle.sections && bundle.sections.length
      ? bundle.sections
      : (["about", "skills", "timeline", "work", "contact"] as HomeSectionType[]).map(
          (type) => ({ id: type, type, value: {} }),
        );

  // Assign §-numbers + build the navbar from nav-eligible sections in order.
  const num = new Map<string, number>();
  const links: NavLink[] = [];
  let n = 0;
  for (const s of sections) {
    if (NAV_TYPES.includes(s.type)) {
      n += 1;
      num.set(s.id, n);
      links.push({
        href: `#${s.type}`,
        n: `§${n}`,
        label: s.value.title || NAV_LABEL[s.type] || s.type,
      });
    }
  }

  function render(s: HomeSection) {
    const i = num.get(s.id) ?? 0;
    const title = s.value.title;
    switch (s.type) {
      case "about":
        return <About key={s.id} bundle={bundle} num={i} title={title} />;
      case "skills":
        return <Skills key={s.id} bundle={bundle} num={i} title={title} />;
      case "timeline":
        return <Timeline key={s.id} bundle={bundle} num={i} title={title} />;
      case "work":
        return <Work key={s.id} projects={projects} num={i} title={title} />;
      case "research":
        return <Research key={s.id} bundle={bundle} num={i} title={title} />;
      case "contact":
        return <Contact key={s.id} bundle={bundle} num={i} title={title} />;
      case "gallery":
        return <Gallery key={s.id} section={s} />;
      case "carousel":
        return <Carousel key={s.id} section={s} />;
      default:
        return null;
    }
  }

  return (
    <>
      <ScrollProgress />
      <Nav links={links} />
      {/* Exposes the section list to the global command palette (⌘K). */}
      <div id="__nav_sections" data-sections={JSON.stringify(links)} hidden />
      <main>
        <Hero bundle={bundle} />
        {sections.map(render)}
      </main>
    </>
  );
}
