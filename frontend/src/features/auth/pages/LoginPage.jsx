import LoginForm from '@features/auth/components/LoginForm'

const LoginPage = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-[#1e3064] rounded-xl mb-4">
            <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[#1e3064]">Sistema de Gestión de Bienes de Ayuda Humanitaria</h1>
          {/* <p className="text-gray-500 text-sm mt-1">Sistema de Gestión de Bienes de Ayuda Humanitaria</p> */}
        </div>

        <LoginForm />
      </div>
    </div>
  )
}

export default LoginPage
