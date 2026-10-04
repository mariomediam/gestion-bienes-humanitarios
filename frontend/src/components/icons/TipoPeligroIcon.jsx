export default function TipoPeligroIcon({ className = 'w-7 h-7' }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8" />
      <path d="M12 4a8 8 0 0 1 8 8h-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  )
}
