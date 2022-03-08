<script lang="ts">
  import request from '../request'
  import { link } from 'svelte-spa-router'

  let username = ''
  let password = ''

  const btnClickHandler = async () => {
    const resp = await request(
      '/auth/login/',
      'POST',
      {
        username,
        password,
      },
      {},
      false
    )

    localStorage.setItem('access', resp.data.access_token)
    localStorage.setItem('refresh', resp.data.refresh_token)

    location.replace('/')
  }
</script>

<div class="container">
  <h1>Авторизация</h1>
  <div class="input-field">
    <input id="login" type="text" bind:value={username} />
    <label for="login">Логин</label>
  </div>
  <div class="input-field">
    <input id="password" type="password" bind:value={password} />
    <label for="password">Пароль</label>
  </div>

  <button
    class="btn waves-effect waves-light amber darken-4"
    on:click={btnClickHandler}
  >
    Войти
    <i class="material-icons left">person</i>
  </button>
  <br />
  <a use:link={'/recover-password/'}>Не помню пароль</a>
</div>
