import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getProject } from "@/lib/api";
import ProjectView from "@/components/views/ProjectView";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const project = await getProject(slug);
  if (!project) return {};
  const images = project.cover_image ? [project.cover_image.url] : undefined;
  return {
    title: `${project.title} — Rafael Correia`,
    description: project.subtitle || undefined,
    openGraph: {
      type: "article",
      title: project.title,
      description: project.subtitle || undefined,
      url: `/portfolio/${slug}`,
      images,
    },
    twitter: { card: "summary_large_image", images },
  };
}

export default async function ProjectPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const project = await getProject(slug);
  if (!project) notFound();

  return <ProjectView project={project} />;
}
