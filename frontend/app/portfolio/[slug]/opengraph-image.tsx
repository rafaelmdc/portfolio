import { ImageResponse } from "next/og";
import { getProject } from "@/lib/api";
import { OG_SIZE, OG_CONTENT_TYPE, CardFrame, getOgFonts, clip } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const revalidate = 3600;
export const alt = "Project — Rafael Correia";

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const project = await getProject(slug);
  const fonts = await getOgFonts();
  return new ImageResponse(
    (
      <CardFrame
        eyebrow={project?.tech_list?.[0] || "Project"}
        title={clip(project?.title || "Rafael Correia", 70)}
        subtitle={clip(project?.result_metric || project?.subtitle || "", 120)}
      />
    ),
    { ...size, fonts },
  );
}
