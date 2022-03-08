import { writable } from 'svelte/store'
import type { IAuthStore } from './../types/auth'

const auth = writable<IAuthStore>({
  id: -1,
  fullName: '',
  avatarUrl: '',
  username: '',
})

export default auth
