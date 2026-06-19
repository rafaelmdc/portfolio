import { getSiteBundle, getProjects } from "@/lib/api";
import HomeView from "@/components/views/HomeView";

// Rendered at request time against the backend Service (no API access needed at
// image-build time). The backend caches GitHub stats, so this stays cheap.
export const dynamic = "force-dynamic";

export default async function Home() {
  const [bundle, projects] = await Promise.all([getSiteBundle(), getProjects()]);
  return <HomeView bundle={bundle} projects={projects} />;
}
