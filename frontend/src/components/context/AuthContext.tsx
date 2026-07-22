// hooks imports
import { createContext, useContext, useState, useEffect} from "react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom"

// components imports
import Loading from "../ui/Loading";

// interface and types imports
import type { AuthContextType, UserLogin, UserProfile } from "../../interfaces/users";

// create context object typed to authentication interface
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// component to provide the data to the app
export function AuthProvider({ children }: { children: ReactNode }) {

    // navigation
    const navigation = useNavigate();
    
    // states
    const [user, setUser] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);

    // state for user
    const isAuthenticated = !!user;

    // check for saved tokens in local storage
    useEffect(()=>{
        const token =  localStorage.getItem('token');
        const savedUser = localStorage.getItem('user');

        if (token && savedUser) {
            setUser(JSON.parse(savedUser))
        }

        setLoading(false);
    }, []); 

    // when user logs in save data in localstorage
    const login = (authData: UserLogin) => {
        localStorage.setItem('accessToken', authData.access);
        localStorage.setItem('refreshToken', authData.refresh);
        localStorage.setItem('user', JSON.stringify(authData.user));
        setUser(authData.user);
    };

    //  clean session of storage if te user logs out and redirect to login
    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        setUser(null);
        navigation('/login')
    };

    if (loading) {
        return (
            <Loading message='Cargando...'/>
        );
    }

    return (
        <AuthContext.Provider value={{user, isAuthenticated, loading, login, logout,
        }}>
            {children}
        </AuthContext.Provider>
    );
}

// hook to read the context values
export function  useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new  Error('useAuth must be used with an AuthProvider');
    }
    return context;
}
