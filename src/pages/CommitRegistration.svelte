<script lang="ts">
  import { params } from 'svelte-spa-router'
  import Loader from '../components/Loader.svelte'
  import request from '../request'
  params.subscribe(async p => {
    if (p) {
      const resp = await request(
        `/auth/commit-registration/${p.token}/`,
        'POST',
        null,
        {},
        false
      )

      localStorage.setItem('access', resp.data.access_token)
      localStorage.setItem('refresh', resp.data.refresh_token)

      location.replace('/')
    }
  })
</script>

<div class="container">
  <Loader />
</div>

<style>
  .container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }
</style>
