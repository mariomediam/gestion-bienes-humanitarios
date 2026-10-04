export default function ClearIcon({ className = 'w-7 h-7' }) {
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
      <path d="m7 21-4.3-4.3c-.9-.9-.9-2.5 0-3.4l9.6-9.6c.9-.9 2.5-.9 3.4 0l5.6 5.6c.9.9.9 2.5 0 3.4L13 21" />
      <path d="M22 21H7" />
      <path d="m5 11 9 9" />
    </svg>
  )
}
