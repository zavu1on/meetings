<script lang="ts">
  import request from '../request'

  let username = ''
  let email = ''

  const btnClickHandler = async () => {
    await request(
      '/auth/recover-password/',
      'POST',
      {
        username,
        email,
      },
      {},
      false
    )

    M.toast({
      html: `<span>На почту <b>${email}</b> была отправлена ссылка для восстановления пароля!</span>`,
      classes: 'light-green darken-3',
    })
  }
</script>

<div class="container">
  <h1>Восстановление пароля</h1>
  <div class="input-field">
    <input id="login" type="text" bind:value={username} />
    <label for="login">Логин</label>
  </div>
  <div class="input-field">
    <input id="email" type="email" bind:value={email} />
    <label for="email">Email</label>
  </div>

  <button
    class="btn waves-effect waves-light amber darken-4"
    on:click={btnClickHandler}
  >
    отправить
    <i class="material-icons left">send</i>
  </button>
</div>
