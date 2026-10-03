import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '@store/authStore'

const LoginForm = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [usernameError, setUsernameError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const { login, loading } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setUsernameError('')
    setPasswordError('')

    let hasError = false

    if (!username.trim()) {
      setUsernameError('El usuario es requerido')
      hasError = true
    }

    if (!password.trim()) {
      setPasswordError('La contraseña es requerida')
      hasError = true
    }

    if (hasError) return

    const result = await login(username, password)

    if (result.success) {
      navigate('/')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="mb-6 text-center">
        <h2 className="text-base font-semibold text-[#1e3064]">
          Inicia sesión con tu cuenta institucional
        </h2>
      </div>

      <div className="mb-5">
        <label className="block text-xs font-medium text-[#1e3064] mb-1" htmlFor="username">
          Usuario
        </label>
        <input
          id="username"
          type="text"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value)
            if (usernameError) setUsernameError('')
          }}
          className={`w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:border-transparent transition duration-200 ${
            usernameError
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-[#1e3064]'
          }`}
          placeholder="Ingresa tu usuario"
          disabled={loading}
          autoComplete="username"
        />
        {usernameError && (
          <p className="mt-1.5 text-xs text-red-600 flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {usernameError}
          </p>
        )}
      </div>

      <div className="mb-6">
        <label className="block text-xs font-medium text-[#1e3064] mb-1" htmlFor="password">
          Contraseña
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value)
            if (passwordError) setPasswordError('')
          }}
          className={`w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:border-transparent transition duration-200 ${
            passwordError
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-[#1e3064]'
          }`}
          placeholder="Ingresa tu contraseña"
          disabled={loading}
          autoComplete="current-password"
        />
        {passwordError && (
          <p className="mt-1.5 text-xs text-red-600 flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {passwordError}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-[#1e3064] text-white font-medium text-sm py-2.5 px-4 rounded-md hover:bg-[#2a4080] focus:outline-none focus:ring-2 focus:ring-[#1e3064] focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            Iniciando sesión...
          </span>
        ) : (
          'Iniciar sesión'
        )}
      </button>
    </form>
  )
}

export default LoginForm
