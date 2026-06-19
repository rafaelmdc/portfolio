import { getPreview, getSiteBundle, getProjects } from "@/lib/api";
import type { SiteBundle, HomeSection, BlogDetail, ProjectDetail } from "@/lib/types";
import HomeView from "@/components/views/HomeView";
import BlogPostView from "@/components/views/BlogPostView";
import ProjectView from "@/components/views/ProjectView";

// Drafts change on every edit and the token is per-preview, so never cache.
export const dynamic = "force-dynamic";

function Notice({ message }: { message: string }) {
  return (
    <main className="mx-auto flex min-h-screen max-w-2xl flex-col items-center justify-center gap-3 px-7 text-center">
      <p className="font-mono text-[13px] text-muted">CMS preview</p>
      <h1 className="font-display text-[24px] font-medium">{message}</h1>
      <p className="text-[14px] text-muted">
        Open this from the “Preview” button in the Wagtail editor.
      </p>
    </main>
  );
}

export default async function PreviewPage({
  searchParams,
}: {
  searchParams: Promise<{ content_type?: string; token?: string }>;
}) {
  const { content_type, token } = await searchParams;
  if (!content_type || !token) {
    return <Notice message="Missing preview parameters." />;
  }

  const draft = await getPreview(content_type, token);
  if (!draft) {
    return <Notice message="This preview link has expired." />;
  }

  switch (content_type.toLowerCase()) {
    case "cms.homepage": {
      // The home page is built from the site bundle (snippet data); only the
      // draft's sections/order/titles differ, so overlay them onto live data.
      const [bundle, projects] = await Promise.all([getSiteBundle(), getProjects()]);
      const merged: SiteBundle = {
        ...bundle,
        sections: (draft.sections as HomeSection[]) ?? bundle.sections,
      };
      return <HomeView bundle={merged} projects={projects} />;
    }
    case "cms.blogpage":
      return <BlogPostView post={draft as unknown as BlogDetail} />;
    case "cms.portfolioprojectpage":
      return <ProjectView project={draft as unknown as ProjectDetail} />;
    default:
      return <Notice message="This page type can’t be previewed." />;
  }
}
