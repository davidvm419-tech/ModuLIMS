// hooks imports
import { createContext, useContext, useState, useEffect, useRef} from "react";
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom"

// components imports
import Loading from "../ui/Loading";

// interface and types imports
import type { AuthContextType, UserLogin, UserProfile } from "../../interfaces/users";

// 30 minutes in milliseconds for user inactivity
const THIRTY_MINUTES: number = 30 * 60 * 1000;

// create context object typed to authentication interface
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// component to provide the data to the app
export function AuthProvider({ children }: { children: ReactNode }) {

    // navigation
    const navigation = useNavigate();
    
    // states
    const [user, setUser] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);

    // inactivity tracking
    const IdleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const lastActiveRef =  useRef<number>(Date.now());

    // state for user
    const isAuthenticated = !!user;

    // check for saved tokens in local storage
    useEffect(()=>{
        const accesstoken =  localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');
        const savedUser = localStorage.getItem('user');

        if (accesstoken && refreshToken && savedUser) {
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
        localStorage.clear();
        setUser(null);
        navigation('/login')
    };

    // check user inactivity to close the session after 30 minutes
    useEffect(()=> {
        if (!isAuthenticated){
            return;
        } 

        const resetIdleTimer = () => {
            lastActiveRef.current = Date.now();

            if (IdleTimerRef.current) {
                clearTimeout(IdleTimerRef.current);
            } 

            IdleTimerRef.current = setTimeout(() => {
                console.warn('Cerrando sesión por inactividad');
                logout();
            }, THIRTY_MINUTES)
        };

        // tracking user activity on the system
        const activityEvents: string[] = ['mousemove', 'keydown', 'click', 'scroll'];
        const handleActivity = () => resetIdleTimer();

        activityEvents.forEach((e) => {
            window.addEventListener(e, handleActivity)
        })

        // tracking if user changes tab and is not on the system
        const handleVisibilityChange = () => {
            if (document.visibilityState === 'visible') {
                const timeAway = Date.now() - lastActiveRef.current;
                
                if (timeAway >= THIRTY_MINUTES) {
                    console.warn('Cerrando sesión por inactividad');
                    logout();
                } else {
                    resetIdleTimer();
                }
            } else {
                lastActiveRef.current = Date.now();
            }
        };

        document.addEventListener('visibilitychange', handleVisibilityChange);

        // start count when user logs in
        resetIdleTimer();

        // clear event listeners whenuser logs out
        return ()=> {
            if (IdleTimerRef.current) {
                clearTimeout(IdleTimerRef.current);
            }

            activityEvents.forEach((e) => {
                window.removeEventListener(e, handleActivity)
            })
        };
    }, [isAuthenticated])

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
