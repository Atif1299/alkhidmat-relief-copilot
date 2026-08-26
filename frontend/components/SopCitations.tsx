"use client";

export type SopHit = {
  title?: string;
  category?: string;
  excerpt?: string;
  score?: number;
  source_file?: string;
};

export function SopCitations({ hits }: { hits?: SopHit[] | null }) {
  if (!hits?.length) {
    return <p className="muted">No SOP citations for this case.</p>;
  }
  return (
    <ul className="citations">
      {hits.map((hit, i) => (
        <li key={`${hit.title}-${i}`}>
          <strong>{hit.title}</strong>
          <span className="muted"> · {hit.category}</span>
          <p>{hit.excerpt}</p>
        </li>
      ))}
    </ul>
  );
}
