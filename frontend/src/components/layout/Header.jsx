import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '@store/authStore'
import ChangePasswordModal from './ChangePasswordModal'

function HamburgerIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  )
}

function KeyIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4" />
    </svg>
  )
}

function LogoutIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  )
}

export default function Header({ onToggleSidebar }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const [passwordModalOpen, setPasswordModalOpen] = useState(false)
  const menuRef = useRef(null)

  const userLogin = user?.login || ''
  const userName = user?.nombre || ''
  const avatarLetters = userLogin.substring(0, 2).toUpperCase()

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleChangePassword = () => {
    setMenuOpen(false)
    setPasswordModalOpen(true)
  }

  const handleLogout = () => {
    setMenuOpen(false)
    logout()
    navigate('/login')
  }

  return (
    <>
      <header className="bg-[#1e3064] text-white h-16 flex items-center px-4 shadow-md z-20 shrink-0">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-md hover:bg-white/10 transition-colors"
          aria-label="Alternar menú lateral"
        >
          <HamburgerIcon />
        </button>

        <div className="ml-3">
          <p className="text-xs font-normal leading-tight opacity-90">
            Municipalidad Provincial de Piura
          </p>
          <p className="text-sm font-semibold leading-tight">
            Sistema de Gestión de Bienes de Ayuda Humanitaria
          </p>
        </div>

        <div className="ml-auto flex items-center gap-3 relative" ref={menuRef}>
          <span className="text-sm font-medium hidden sm:block">{userLogin}</span>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            className="w-10 h-10 rounded-full bg-[#1e3064] border-2 border-white flex items-center justify-center text-sm font-bold cursor-pointer hover:bg-white/10 transition-colors"
          >
            {avatarLetters}
          </button>

          {menuOpen && (
            <div className="absolute right-0 top-12 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-30">
              <div className="px-4 py-2 border-b border-gray-100">
                <p className="text-sm font-semibold text-gray-800">{userName}</p>
                <p className="text-xs text-gray-500">{userLogin}</p>
              </div>

              <button
                onClick={handleChangePassword}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <KeyIcon />
                Cambiar contraseña
              </button>

              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogoutIcon />
                Cerrar sesión
              </button>
            </div>
          )}
        </div>
      </header>

      <ChangePasswordModal
        isOpen={passwordModalOpen}
        onClose={() => setPasswordModalOpen(false)}
      />
    </>
  )
}
