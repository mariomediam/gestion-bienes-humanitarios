import LoginForm from '@features/auth/components/LoginForm'

const LoginPage = () => {
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="flex items-center gap-3 px-6 py-2">
        <img
          src="/images/escudo_muni.webp"
          alt="Escudo de la Municipalidad Provincial de Piura"
          className="h-8 w-auto"
        />
        <p className="text-xs font-semibold text-[#1e3064] leading-tight">
          Municipalidad Provincial de Piura
        </p>

      </header>
      <hr className="w-full border-gray-300" />
      <div className="flex-1 flex items-center justify-center px-4 py-6">
        <div className="w-full max-w-md">
          <div className="text-center mb-4 ">
            {/* <div className="inline-flex items-center justify-center w-14 h-14 bg-[#1e3064] rounded-xl mb-4"> */}
            <img
              src="/images/emblema.webp"
              alt="Sistema de Gestión de Bienes de Ayuda Humanitaria"
              className="h-32 w-auto inline-flex items-center justify-center"
            />
            {/* </div> */}
            <h1 className="font-bold text-[#1e3064]">Sistema de Gestión de Bienes de Ayuda Humanitaria</h1>
            {/* <p className="text-gray-500 text-sm mt-1">Sistema de Gestión de Bienes de Ayuda Humanitaria</p> */}
          </div>

          <LoginForm />
        </div>
      </div>
    </div>
  )
}

export default LoginPage
