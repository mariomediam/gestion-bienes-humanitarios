import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import useAuthStore from '@store/authStore'

function PageIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  )
}

function FolderIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
    </svg>
  )
}

function ChevronIcon({ isOpen }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-90' : ''}`}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="9 18 15 12 9 6" />
    </svg>
  )
}

function buildMenuTree(menus) {
  const topLevel = []
  const childrenMap = {}

  menus.forEach((item) => {
    const parentKey = String(item.MenPadre)
    if (parentKey === 'NULL' || parentKey === 'null' || !item.MenPadre) {
      topLevel.push({ ...item, children: [] })
    } else {
      if (!childrenMap[parentKey]) {
        childrenMap[parentKey] = []
      }
      childrenMap[parentKey].push(item)
    }
  })

  topLevel.forEach((parent) => {
    const key = String(parent.MenCodi)
    parent.children = childrenMap[key] || []
  })

  return topLevel
}

function MenuItemPage({ item }) {
  return (
    <NavLink
      to={item.MenProg}
      className={({ isActive }) =>
        `flex items-center gap-3 px-5 py-3 text-sm font-medium transition-colors ${
          isActive
            ? 'text-[#1e3064] bg-blue-50 border-r-3 border-[#1e3064]'
            : 'text-gray-600 hover:text-[#1e3064] hover:bg-gray-50'
        }`
      }
    >
      <PageIcon />
      {item.MenDesc}
    </NavLink>
  )
}

function MenuItemFolder({ item }) {
  const { pathname } = useLocation()
  const hasActiveChild = item.children.some((child) => pathname === child.MenProg)
  const [open, setOpen] = useState(hasActiveChild)

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 px-5 py-3 text-sm font-medium text-gray-600 hover:text-[#1e3064] hover:bg-gray-50 transition-colors"
      >
        <FolderIcon />
        <span className="flex-1 text-left">{item.MenDesc}</span>
        <ChevronIcon isOpen={open} />
      </button>

      {open && (
        <div className="ml-4">
          {item.children.map((child) => (
            <NavLink
              key={child.MenCodi}
              to={child.MenProg}
              className={({ isActive }) =>
                `flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'text-[#1e3064] bg-blue-50 font-medium'
                    : 'text-gray-500 hover:text-[#1e3064] hover:bg-gray-50'
                }`
              }
            >
              <PageIcon />
              {child.MenDesc}
            </NavLink>
          ))}
        </div>
      )}
    </div>
  )
}

export default function Sidebar({ isOpen }) {
  const { menus } = useAuthStore()
  const menuTree = buildMenuTree(menus)

  return (
    <aside
      className={`bg-white border-r border-gray-200 shrink-0 transition-all duration-300 overflow-hidden ${
        isOpen ? 'w-56' : 'w-0'
      }`}
    >
      <nav className="flex flex-col py-4 w-56">
        {menuTree.map((item) =>
          item.MenTipo === 'M' ? (
            <MenuItemFolder key={item.MenCodi} item={item} />
          ) : (
            <MenuItemPage key={item.MenCodi} item={item} />
          )
        )}
      </nav>
    </aside>
  )
}
