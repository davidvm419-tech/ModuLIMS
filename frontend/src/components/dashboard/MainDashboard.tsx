// hooks imports
import { useAuth } from "../context/AuthContext";

// components imports
import Footer from "../ui/Footer";

export default function MainDashboard() {
    const { user, logout }= useAuth()
    return (

        <div className="flex min-h-screen flex-col justify-center px-6 py-12 lg:px-8 bg-primary/10">
            <nav>
                and here there will be  a nav bar
            </nav>

            <h1>Here you  will find a dashboard!</h1>
            <p>{user?.id}</p>
            <p>{user?.username}</p>
            <p>{user?.role}</p>
            <button onClick={logout}>Cerrar Sesión</button>
            <Footer/>
        </div>
    );
}