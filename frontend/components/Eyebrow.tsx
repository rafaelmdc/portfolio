export default function Eyebrow({
  children,
  centered = false,
}: {
  children: React.ReactNode;
  centered?: boolean;
}) {
  return (
    <div
      className={`mb-[18px] flex items-center gap-[10px] font-mono text-[12px] tracking-[0.06em] text-primary ${
        centered ? "justify-center" : ""
      }`}
    >
      {children}
      <span className="h-px flex-1 bg-border" />
    </div>
  );
}
