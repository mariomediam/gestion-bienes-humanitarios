export default function Card({ title, value, children, className = '' }) {
  const showValue = value !== undefined && value !== null

  return (
    <section className={`bg-white rounded-lg border border-gray-200 p-5 ${className}`}>
      <h2 className="text-sm font-medium text-gray-500">{title}</h2>
      {showValue && (
        <p className="mt-2 text-3xl font-semibold text-[#1e3064]">{value}</p>
      )}
      {children}
    </section>
  )
}
