import { useState } from "react";

export default function Login(){
    const apiBase = import.meta.env.VITE_API_URL;
    const [userData, setUserData] = useState({
        username: '',
        password: '',
    });

    const formChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setUserData({
            ...userData,
            [e.target.name]: e.target.value,
        })
    };

    return (
      <div className="flex items-center justify-center px-4">
        <form>
            <input type='text' name='username' placeholder='Nombre de usuario'
            onChange={formChange} value={userData['username']}/>
            <input type='password' name='password' placeholder='contraseña'
            onChange={formChange} value={userData['password']}/>
            <button type='submit' onClick={()=> alert('no funciona aun')}>Iniciar Sesión</button>
            <h2>Contactese con la administración si aun no ha recibido sus credenciales</h2>
        </form>
      </div>
    );
}