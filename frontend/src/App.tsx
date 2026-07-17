import './index.css'
import {Routes, Route, Navigate} from 'react-router-dom';

// components imports
import Login from './components/users/Login'
import MainDashboard from './components/dashboard/MainDashboard';

function App() {
  return (
    <Routes>
      <Route path='/login' element={<Login/>}/>
      <Route path='/dashboard' element={<MainDashboard/>}/>
    </Routes>
  )
}

export default App
