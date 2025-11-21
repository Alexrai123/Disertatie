import React, { createContext, useContext, useEffect, useState } from 'react'
import axios from 'axios'

// References:
// - see docs/13_app_arch.txt §1 Presentation Layer (Authentication)
// - see docs/02_functional_req.txt §1 (Admin/User roles)

export type User = { id: number; username: string; role: 'admin' | 'user' }

type AuthContextType = {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({} as any)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const t = localStorage.getItem('token')
    if (t) {
      setToken(t)
      axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
      axios.get('/users/me').then((res) => setUser(res.data)).catch(() => logout())
    }
  }, [])

  async function login(username: string, password: string) {
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    const { data } = await axios.post('/auth/token', params)
    const t = data.access_token as string
    setToken(t)
    localStorage.setItem('token', t)
    axios.defaults.headers.common['Authorization'] = `Bearer ${t}`
    const me = await axios.get('/users/me')
    setUser(me.data)
  }

  function logout() {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  return <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
