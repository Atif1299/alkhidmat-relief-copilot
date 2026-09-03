export function BrandMark({ className = "brand-mark" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      width="32"
      height="32"
      aria-hidden="true"
      focusable="false"
    >
      <rect
        x="3.5"
        y="11"
        width="17"
        height="16"
        rx="2.2"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.75"
      />
      <path
        d="M12 15.2h6.2M12 19h4.4M12 22.8h5.2"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path
        d="M23.2 6.4c-4.6.2-8.2 4-8.2 8.6 0 4.7 3.8 8.5 8.5 8.5 1.4 0 2.7-.3 3.8-.9-1.5 1.6-3.7 2.6-6.1 2.6-4.7 0-8.5-3.8-8.5-8.5 0-4.6 3.6-8.4 8.1-8.5.8 0 1.6.1 2.4.2z"
        fill="currentColor"
      />
    </svg>
  );
}
