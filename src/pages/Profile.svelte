<script lang="ts">
  import { onMount, afterUpdate } from 'svelte'
  import { push } from 'svelte-spa-router'
  import Loader from '../components/Loader.svelte'
  import request, { BASE_URL } from '../request'
  import auth from '../store/auth'
  import images from '../store/images'
  import meetings from '../store/meetings'
  import type { IMeeting } from '../types/meetings'

  let avatar
  let isLoaded = false
  let isInitialised = false
  let rowed_meetings: IMeeting[][] = []

  let name = ''
  let password = ''
  let url = ''
  let enterPassword = ''
  let roomName = ''

  onMount(async () => {
    const resp = await request('/meetings/get/')
    meetings.set(resp.data)

    for (let i = 0; i < $meetings.length; i++) {
      if (i % 6 === 0) {
        rowed_meetings.push([])
      }

      rowed_meetings[rowed_meetings.length - 1].push($meetings[i])
    }

    isLoaded = true
  })

  afterUpdate(() => {
    if (isLoaded && !isInitialised) {
      let elems = document.querySelectorAll('.sidenav')
      M.Sidenav.init(elems)

      elems = document.querySelectorAll('.modal')
      M.Modal.init(elems)

      elems = document.querySelectorAll('select')
      M.FormSelect.init(elems)

      // @ts-ignore
      document.querySelector('#pass').focus()

      isInitialised = true
    }

    M.updateTextFields()
  })

  const openModal = (selector: string) =>
    M.Modal.getInstance(document.querySelector(selector)).open()

  const createClickHandler = async () => {
    const resp = await request('/meetings/create/', 'POST', {
      name,
      password: password || null,
      // @ts-ignore
      room: document.querySelector('#select1').value,
      room_name: roomName,
    })

    meetings.update(d => [...d, resp.data.meeting])

    rowed_meetings = []
    for (let i = 0; i < $meetings.length; i++) {
      if (i % 6 === 0) {
        rowed_meetings.push([])
      }

      rowed_meetings[rowed_meetings.length - 1].push($meetings[i])
    }

    M.toast({
      html: `Вы успешно создали встречу!`,
      classes: 'light-green darken-3',
    })
  }

  const enterClickHandler = async () => {
    await request('/meetings/enter/', 'POST', {
      url,
      password: enterPassword || null,
    })

    M.toast({
      html: `Вы успешно зашли на встречу!`,
      classes: 'light-green darken-3',
    })

    push(`/meeting/${url}/`)
  }
</script>

{#if isLoaded}
  <nav class="orange darken-4">
    <div class="nav-wrapper">
      <a href="/" class="brand-logo">Meetings</a>
      <a href="#" data-target="mobile-demo" class="sidenav-trigger"
        ><i class="material-icons">menu</i></a
      >
      <ul class="right hide-on-med-and-down">
        <li>
          <a href="javascript:void()" on:click={() => openModal('#create')}
            >Организовать встречу</a
          >
        </li>
        <li>
          <a
            href="javascript:void()"
            on:click={() => {
              url = ''
              openModal('#join')
            }}>Присоединиться к встрече</a
          >
        </li>
      </ul>
    </div>
  </nav>

  <ul class="sidenav" id="mobile-demo">
    <li>
      <a href="javascript:void()" on:click={() => openModal('#create')}
        >Организовать встречу</a
      >
    </li>
    <li>
      <a
        href="javascript:void()"
        on:click={() => {
          url = ''
          openModal('#join')
        }}>Присоединиться к встрече</a
      >
    </li>
  </ul>

  <div class="container">
    <div class="img-container">
      <img src={$auth.avatarUrl} alt="avatar" />
    </div>
    <h5>{$auth.username}</h5>
    <h6>{$auth.fullName}</h6>
    <div class="file-field input-field" style="width: 300px;">
      <div class="btn amber darken-4">
        <span>avatar</span>
        <input
          type="file"
          accept="image/*"
          bind:files={avatar}
          on:change={async () => {
            const fd = new FormData()

            fd.append('avatar', avatar[0])

            const resp = await fetch(BASE_URL + '/auth/set-user-avatar/', {
              method: 'POST',
              headers: {
                Authorization: `Bearer ${localStorage.getItem('access')}`,
              },
              body: fd,
            })
            const json = await resp.json()

            auth.update(d => ({
              ...d,
              avatarUrl: json.avatarUrl,
            }))
          }}
        />
      </div>
      <div class="file-path-wrapper">
        <input class="file-path validate" type="text" />
      </div>
    </div>

    <h3>Запланированные встречи</h3>
    {#each rowed_meetings as row}
      <div class="row">
        {#each row as meeting}
          <div class="col s2">
            <h5>
              <a
                class="waves-effect waves-light btn amber darken-3"
                href="javascript:void()"
                on:click={() => {
                  url = meeting.slug
                  openModal('#join')
                }}
              >
                <i class="material-icons left">details</i>
                {meeting.name}
              </a>
            </h5>
          </div>
        {/each}
      </div>
    {/each}
  </div>

  <!-- Modal Structure -->
  <div id="create" class="modal">
    <div class="modal-content">
      <h4>Организовать встречу</h4>
      <div class="input-field">
        <input id="name" type="text" bind:value={name} />
        <label for="name">Название</label>
      </div>
      <div class="input-field">
        <input
          id="pass"
          type="text"
          bind:value={password}
          placeholder="Отсутствует"
        />
        <label for="pass">Пароль для входа</label>
      </div>

      <div class="input-field">
        <input id="name" type="text" bind:value={roomName} />
        <label for="name">Название комнаты</label>
      </div>

      <div class="input-field">
        <select id="select1">
          {#each $images as image}
            <option value={image.id}>{image.name}</option>
          {/each}
        </select>
        <label>Вид комнаты</label>
      </div>

      <button
        class="btn waves-effect waves-light amber darken-4"
        on:click={createClickHandler}
        >Создать
        <i class="material-icons right">send</i>
      </button>
    </div>
  </div>

  <!-- Modal Structure -->
  <div id="join" class="modal">
    <div class="modal-content">
      <h4>Присоединиться к встрече</h4>
      <div class="input-field">
        <input id="name" type="text" bind:value={url} />
        <label for="name">Идентификатор входа</label>
      </div>
      <div class="input-field">
        <input
          type="text"
          bind:value={enterPassword}
          placeholder="Отсутствует"
        />
        <label for="pass">Пароль для входа</label>
      </div>

      <button
        class="btn waves-effect waves-light amber darken-4"
        on:click={enterClickHandler}
        >Войти
        <i class="material-icons right">send</i>
      </button>
      <button
        class="btn waves-effect waves-light light-green darken-3"
        on:click={async () => {
          await navigator.clipboard.writeText(url)
          M.toast({
            html: `Идентификатор входа скопирован в буфер обена!`,
            classes: 'light-green darken-3',
          })
        }}
        >Поделиться
        <i class="material-icons right">share</i>
      </button>
      <button
        class="waves-effect waves-light btn red darken-4"
        on:click={async () => {
          await request(`/meetings/delete/${url}/`, 'POST')

          meetings.update(state => state.filter(m => m.slug !== url))

          rowed_meetings = []
          for (let i = 0; i < $meetings.length; i++) {
            if (i % 6 === 0) {
              rowed_meetings.push([])
            }

            rowed_meetings[rowed_meetings.length - 1].push($meetings[i])
          }

          M.toast({
            html: `Вы успешно удалили встречу!`,
            classes: 'light-green darken-3',
          })
        }}><i class="material-icons left">delete</i>удалить</button
      >
    </div>
  </div>
{:else}
  <div class="container loader-container">
    <Loader />
  </div>
{/if}

<style>
  .loader-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }

  nav {
    padding: 0 20px;
  }

  .img-container {
    width: 260px;
    height: 260px;
    margin-top: 16px;
  }

  .img-container img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
  }
</style>
