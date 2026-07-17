// hooks  imports
import { useState } from "react";
import { useNavigate } from "react-router-dom"

// components imports
import AlertMessages from "../ui/AlertMessages";

// interface and types imports
import type { LoginData } from "../../interfaces/users";
import type { Messages } from "../../interfaces/alerts";

export default function Login(){

    // navigation
    const navigation = useNavigate();
    
    const apiBase = import.meta.env.VITE_API_URL;

    const [message, setMessage] = useState<Messages | null>(null);

    const [userData, setUserData] = useState<LoginData>({
        username: '',
        password: '',
    });

    const formChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUserData({
            ...userData,
            [e.target.name]: e.target.value,
        })
    };

    const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
        e.preventDefault()
        
        try {
            const response = await fetch(`${apiBase}/api/users/login/`, {
                method: 'POST',
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(userData)
            });

            const data = await response.json();

            if (!response.ok) {
                
                // set error for alert message
                setMessage({
                    type: 'error',
                    title: 'Error iniciando sesión',
                    content: data.error,
                })

                // reset form
                setUserData({
                    username: '',
                    password: '',
                })
                
                // set timeout to hide error message
                setTimeout(() => {
                    setMessage(null)
                }, 6000)

            } else {
                // set success for alert message
                setMessage({
                    type: 'success',
                    title: 'Inicio de sesión exitoso',
                    content: 'Bienvenido de vuelta',
                })

                // temporal,  add the logic to handle userdata
                console.log(data)

                // set timeout to redirect to user main page
                setTimeout(() => {
                    navigation('/dashboard')
                }, 2000)
            }
        } catch (err) {
            // set error for alert message
            setMessage({
                type: 'error',
                title: 'Error',
                content: `No se pudo establecer comunicación con el servidor. Por favor contacte al administrador`,
            })
            console.log(`Error de red/servidor: ${err}`)
            
            // set timeout to hide error message
            setTimeout(() => {
                setMessage(null)
            }, 6000)
        }
    } 

    return (
      <div className="flex min-h-screen flex-col justify-center px-6 py-12 lg:px-8 bg-primary/10">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
            <img 
            className="mx-auto h-50 w-auto object-contain rounded-2xl" 
            src="/images/logo.png" 
            alt="Microbial systems logo"/>

            <h2 className="mt-10 text-center text-2xl/9 font-bold tracking-tight text-accent">Iniciar sesión en ModuLims</h2>
        </div>

        {/* dynamic message */}
        {message && <AlertMessages 
        type={message.type} 
        title={message.title} 
        content={message.content}/>}
    
        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
            <form className="space-y-6" onSubmit={handleSubmit}>
                <div>
                    <label className="block text-sm/6 font-medium text-black-100" htmlFor="username">Nombre de Usuario</label>
                    <div className="mt-2">
                        <input className="block w-full rounded-md bg-gray/5 px-3 py-1.5 text-base text-black outline-1 -outline-offset-1 
                        outline-black/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 
                        focus:outline-focus sm:text-sm/6" 
                        type='text' 
                        name='username' 
                        required autoComplete='username'
                        onChange={formChange} value={userData.username}/>
                    </div>
                </div>

                <div>
                    <div className="flex items-center justify-between">
                        <label className="block text-sm/6 font-medium text-black-100" htmlFor="password">Contraseña</label>
                    </div>
                        <div className="mt-2">
                            <input className="block w-full rounded-md bg-gray/5 px-3 py-1.5 text-base text-black outline-1 -outline-offset-1 
                            outline-black/10 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2 
                            focus:outline-focus sm:text-sm/6" 
                            type='password' 
                            name='password' 
                            required autoComplete='current-password'
                            onChange={formChange} value={userData.password}/>
                        </div>
                </div>

                <div>
                    <button className="flex w-full justify-center rounded-md bg-interactive px-3 py-1.5 text-sm/6 font-semibold text-white transition-colors
                    enabled:hover:bg-interactive-hover 
                    focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent 
                    disabled:opacity-50 disabled:cursor-not-allowed"
                    type='submit'
                    disabled={!userData.username.trim() || !userData.password.trim()}>Iniciar Sesión</button>
                </div>
            </form>

            <p className="mt-10 text-center text-sm/6 text-gray-900">
              Contactese con la administración si aun no ha recibido sus credenciales.  
            </p>
        </div>

        <footer className="mt-auto pt-12 text-center text-xs text-gray-500">
            <div className="border-t border-interactive/10 pt-6">
                <p>© {new Date().getFullYear()} Microbial Systems. Todos los derechos reservados.</p>
                <p className="mt-1 text-gray-400">ModuLims - Laboratory Information Management System v1.0</p>
            </div>
            </footer>
      </div>
    );
}