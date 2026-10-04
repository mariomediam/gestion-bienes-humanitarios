export default function Card({ title, value, icon: Icon, iconClassName = 'bg-gray-100 text-gray-700', children, className = '' }) {
  const showValue = value !== undefined && value !== null

  return (
    <section className={`bg-white rounded-xl border border-gray-200 p-5 ${className}`}>
      {Icon && (
        <span className={`inline-flex items-center justify-center w-11 h-11 rounded-full ${iconClassName}`}>
          <Icon className="w-5 h-5" />
        </span>
      )}
      {showValue && (
        <p className="mt-6 text-3xl font-semibold tracking-tight text-gray-900">{value}</p>
      )}
      <h2 className={`text-sm text-gray-500 ${showValue ? 'mt-1' : Icon ? 'mt-4' : ''}`}>{title}</h2>
      {children}
    </section>
  )
}
