<script lang="ts">
  import Router from 'svelte-spa-router'
  import Index from './pages/Index.svelte'
  import Login from './pages/Login.svelte'
  import Registration from './pages/Registration.svelte'
  import Profile from './pages/Profile.svelte'
  import M from 'materialize-css'
  import request from './request'
  import auth from './store/auth'
  import CommitRegistration from './pages/CommitRegistration.svelte'
  import RecoverPassword from './pages/RecoverPassword.svelte'
  import CommitRecoverPassword from './pages/CommitRecoverPassword.svelte'
  import images from './store/images'
  import Lobby from './pages/Lobby.svelte'
  import Room from './pages/Room.svelte'

  let routes: any = {
    '/': Index,
    '/login/': Login,
    '/registration/': Registration,
    '/commit-registration/:token/': CommitRegistration,
    '/recover-password/': RecoverPassword,
    '/commit-recover-password/:token/': CommitRecoverPassword,

    '*': Index,
  }

  const id = localStorage.getItem('id')
  const access = localStorage.getItem('access')
  const refresh = localStorage.getItem('refresh')

  if (id || access || refresh) {
    request('/auth/get-user-data/').then(r => auth.set(r.data))
    request('/meetings/images/get/').then(r => images.set(r.data))

    routes = {
      '/': Profile,
      '/recover-password/': RecoverPassword,
      '/commit-recover-password/:token/': CommitRecoverPassword,
      '/meeting/:id1/': Lobby,
      '/meeting/:id1/:id2/': Room,

      '*': Profile,
    }
  }
</script>

<Router {routes} />
