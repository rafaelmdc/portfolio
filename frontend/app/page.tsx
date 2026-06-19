import { getSiteBundle, getProjects } from "@/lib/api";
import Nav from "@/components/Nav";
import ScrollProgress from "@/components/ScrollProgress";
import Hero from "@/components/sections/Hero";
import About from "@/components/sections/About";
import Skills from "@/components/sections/Skills";
import Timeline from "@/components/sections/Timeline";
import Work from "@/components/sections/Work";
import Research from "@/components/sections/Research";
import Contact from "@/components/sections/Contact";

export default async function Home() {
  const [bundle, projects] = await Promise.all([getSiteBundle(), getProjects()]);

  return (
    <>
      <ScrollProgress />
      <Nav hasResearch={bundle.has_research} />
      <main>
        <Hero bundle={bundle} />
        <About bundle={bundle} />
        <Skills bundle={bundle} />
        <Timeline bundle={bundle} />
        <Work projects={projects} />
        <Research bundle={bundle} />
        <Contact bundle={bundle} />
      </main>
    </>
  );
}
