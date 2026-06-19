import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { getBlogPost } from "@/lib/api";
import BlogPostView from "@/components/views/BlogPostView";

export const dynamic = "force-dynamic";

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const post = await getBlogPost(slug);
  if (!post) return {};
  const images = post.hero_image ? [post.hero_image.url] : undefined;
  return {
    title: `${post.title} — Rafael Correia`,
    description: post.intro || undefined,
    openGraph: {
      type: "article",
      title: post.title,
      description: post.intro || undefined,
      url: `/blog/${slug}`,
      images,
    },
    twitter: { card: "summary_large_image", images },
  };
}

export default async function BlogPost({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const post = await getBlogPost(slug);
  if (!post) notFound();

  return <BlogPostView post={post} />;
}
