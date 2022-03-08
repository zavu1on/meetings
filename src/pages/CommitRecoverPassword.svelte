<script lang="ts">
  import { push, params } from 'svelte-spa-router'
  import request from '../request'

  let password = ''

  const btnClickHandler = async () => {
    await request(
      '/auth/commit-recover-password/' + $params.token + '/',
      'POST',
      {
        password,
      },
      {},
      false
    )

    M.toast({
      html: `<span>Вы успешно сменили пароль!</span>`,
      classes: 'light-green darken-3',
    })

    push('/')
  }
</script>

<div class="container">
  <h1>Восстановление пароля</h1>
  <div class="input-field">
    <input id="login" type="text" bind:value={password} />
    <label for="login">Новый пароль</label>
  </div>
  <button
    class="btn waves-effect waves-light amber darken-4"
    on:click={btnClickHandler}
  >
    отправить
    <i class="material-icons left">send</i>
  </button>
</div>
