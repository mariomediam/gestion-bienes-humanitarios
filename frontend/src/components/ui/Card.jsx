export default function Card({ title, value, icon: Icon, children, className = '' }) {
  const showValue = value !== undefined && value !== null

  return (
    <section className={`bg-white rounded-xl border border-gray-200 p-5 ${className}`}>
      {Icon && <Icon className="w-7 h-7 text-gray-900" />}
      {showValue && (
        <p className="mt-6 text-3xl font-semibold tracking-tight text-gray-900">{value}</p>
      )}
      <h2 className={`text-sm text-gray-500 ${showValue ? 'mt-1' : Icon ? 'mt-4' : ''}`}>{title}</h2>
      {children}
    </section>
  )
}
