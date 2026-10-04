export default function PersonasIcon({ className = 'w-7 h-7' }) {
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
      <circle cx="9" cy="8" r="3" />
      <path d="M3.5 19a5.5 5.5 0 0 1 11 0" />
      <circle cx="17" cy="9" r="2.25" />
      <path d="M16.2 14.2a4.5 4.5 0 0 1 4.3 4.8" />
    </svg>
  )
}
