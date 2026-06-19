import { ImageResponse } from "next/og";
import { getBlogPost } from "@/lib/api";
import { OG_SIZE, OG_CONTENT_TYPE, CardFrame, getOgFonts, clip } from "@/lib/og";

export const size = OG_SIZE;
export const contentType = OG_CONTENT_TYPE;
export const revalidate = 3600;
export const alt = "Blog post — Rafael Correia";

export default async function Image({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getBlogPost(slug);
  const fonts = await getOgFonts();
  return new ImageResponse(
    (
      <CardFrame
        eyebrow={post?.tag_names?.[0] || "Blog"}
        title={clip(post?.title || "Rafael Correia", 70)}
        subtitle={clip(post?.intro || "", 120)}
      />
    ),
    { ...size, fonts },
  );
}
