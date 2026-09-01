"use client";

export type SopHit = {
  title?: string;
  category?: string;
  excerpt?: string;
  score?: number;
  source_file?: string;
  retrieval_mode?: string;
};

function stripMarkdown(text: string): string {
  return text
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/^#+\s*/gm, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function SopCitations({ hits }: { hits?: SopHit[] | null }) {
  if (!hits?.length) {
    return <p className="muted">No SOP citations for this case.</p>;
  }
  return (
    <ul className="citations">
      {hits.map((hit, i) => (
        <li key={`${hit.title}-${i}`}>
          <strong>{hit.title}</strong>
          {hit.excerpt && <p>{stripMarkdown(hit.excerpt)}</p>}
        </li>
      ))}
    </ul>
  );
}
