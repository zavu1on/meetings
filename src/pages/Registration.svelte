<script lang="ts">
  import request from '../request'

  let username = ''
  let email = ''
  let password = ''
  let fio = ''

  const btnClickHandler = async () => {
    if (fio.split(' ').length !== 3) {
      return M.toast({
        html: 'Введено некорректное ФИО!',
        classes: 'red darken-4',
      })
    }

    await request(
      '/auth/registration/',
      'POST',
      {
        username,
        password,
        email,
        first_name: fio.split(' ')[0],
        last_name: fio.split(' ')[1],
        patronymic: fio.split(' ')[2],
      },
      {},
      false
    )

    M.toast({
      html: `<span>На почту <b>${email}</b> была отправлена ссылка для завершения регистрации!</span>`,
      classes: 'light-green darken-3',
    })
  }
</script>

<div class="container">
  <h1>Регистрация</h1>
  <div class="input-field">
    <input id="login" type="text" bind:value={username} />
    <label for="login">Логин</label>
  </div>
  <div class="input-field">
    <input id="email" type="email" bind:value={email} />
    <label for="email">Email</label>
  </div>
  <div class="input-field">
    <input id="fio" type="text" bind:value={fio} />
    <label for="fio">ФИО</label>
  </div>
  <div class="input-field">
    <input id="password" type="password" bind:value={password} />
    <label for="password">Пароль</label>
  </div>

  <button
    class="btn waves-effect waves-light amber darken-4"
    on:click={btnClickHandler}
  >
    регистрация
    <i class="material-icons left">person</i>
  </button>
</div>
