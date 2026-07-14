import { useState } from "react";

interface LoginData {
        username: '';
        password: '';
    }
export default function Login(){
    
    const apiBase = import.meta.env.VITE_API_URL;

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

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
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
                alert('credenciales incorrectas')

                setUserData({
                    username: '',
                    password: '',
                })
            }
        } catch (err) {
        'An error has happened, please try again later'
        }
    } 

    return (
      <div className="flex items-center justify-center px-4">
        <form onSubmit={handleSubmit}>
            <input type='text' name='username' placeholder='Nombre de usuario'
            onChange={formChange} value={userData.username}/>
            <input type='password' name='password' placeholder='contraseña'
            onChange={formChange} value={userData.password}/>
            <button type='submit'>Iniciar Sesión</button>
            <h2>Contactese con la administración si aun no ha recibido sus credenciales</h2>
        </form>
      </div>
    );
}