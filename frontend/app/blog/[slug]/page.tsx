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
  return {
    title: `${post.title} — Rafael Correia`,
    description: post.intro || undefined,
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
