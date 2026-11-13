import {useEffect,useState} from 'react';
import {authApi} from '../api/auth';
import type {User} from '../types/domain';
export function useSession(){
 const [user,setUser]=useState<User|null>(null),[loading,setLoading]=useState(true);
 useEffect(()=>{if(localStorage.getItem('hemo-token'))authApi.me().then(setUser).catch(()=>localStorage.removeItem('hemo-token')).finally(()=>setLoading(false));else setLoading(false);const expired=()=>setUser(null);window.addEventListener('session-expired',expired);return()=>window.removeEventListener('session-expired',expired);},[]);
 async function login(email:string,password:string){const r=await authApi.login(email,password);localStorage.setItem('hemo-token',r.token);setUser(r.user);}
 function logout(){localStorage.removeItem('hemo-token');setUser(null);}
 return {user,loading,login,logout};
}
