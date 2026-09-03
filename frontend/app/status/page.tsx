import { StatusLookup } from "./StatusLookup";

export default function StatusPage({
  searchParams,
}: {
  searchParams?: { ticket?: string | string[] };
}) {
  const raw = searchParams?.ticket;
  const ticket = (Array.isArray(raw) ? raw[0] : raw) || "";
  return <StatusLookup initialTicket={ticket} />;
}
