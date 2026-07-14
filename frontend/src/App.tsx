import './index.css'
import {Routes, Route, Navigate} from 'react-router-dom';

import Login from './assets/features/users/Login'

function App() {
  return (
    <Routes>
      <Route path='login' element={<Login/>}/>
    </Routes>
  )
}

export default App
