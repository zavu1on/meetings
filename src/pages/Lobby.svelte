<script type="ts">
  import { afterUpdate, onMount } from 'svelte'
  import { push, link } from 'svelte-spa-router'
  import { writable } from 'svelte/store'
  import Loader from '../components/Loader.svelte'
  import request from '../request'
  import images from '../store/images'
  import type { IRoom } from '../types/meetings'

  export let params

  let isLoaded = false
  let isInitialised = false
  let name = ''

  let reqData: {
    name: string
    isHost: boolean
  } = {
    name: '',
    isHost: false,
  }

  const rooms = writable<IRoom[]>([])

  onMount(async () => {
    try {
      const resp = await request(`/meetings/data/get/${params.id1}/`)

      reqData = resp.data
      rooms.set(resp.data.rooms)

      isLoaded = true
    } catch (e) {
      M.toast({
        html: `<span>Вы не можете зайти на конференцию</span>`,
        classes: 'red darken-4',
      })
      push('/')
    }
  })

  afterUpdate(() => {
    if (isLoaded && !isInitialised) {
      let elems = document.querySelectorAll('.sidenav')
      M.Sidenav.init(elems)

      elems = document.querySelectorAll('.modal')
      M.Modal.init(elems)

      elems = document.querySelectorAll('select')
      M.FormSelect.init(elems)

      isInitialised = true
    }
  })

  const openModal = (selector: string) =>
    M.Modal.getInstance(document.querySelector(selector)).open()

  const addClickHandler = async () => {
    const resp = await request(`/meetings/rooms/add/${params.id1}/`, 'POST', {
      // @ts-ignore
      id: document.querySelector('#select1').value,
      name,
    })

    rooms.update(r => [...r, resp.data.room])
  }
</script>

{#if isLoaded}
  <nav class="orange darken-4">
    <div class="nav-wrapper">
      <a href="/" class="brand-logo">{reqData.name}</a>
      <a href="#" data-target="mobile-demo" class="sidenav-trigger"
        ><i class="material-icons">menu</i></a
      >
      {#if reqData.isHost}
        <ul class="right hide-on-med-and-down">
          <li>
            <a href="javascript:viod()" on:click={() => openModal('#add')}
              >Добавить комнату</a
            >
          </li>
        </ul>
      {/if}
    </div>
  </nav>

  <ul class="sidenav" id="mobile-demo">
    {#if reqData.isHost}
      <li>
        <a href="javascript:void()" on:click={() => openModal('#add')}
          >Добавить комнату</a
        >
      </li>
    {/if}
  </ul>

  <div class="container">
    <h3>Доступные комнаты</h3>
    <div class="row">
      {#each $rooms as room}
        <div class="col s3">
          <div class="card small">
            <div class="card-image">
              <img
                src={'http://127.0.0.1:8000' + room.room_image.preview_image}
                alt="preview"
              />
              <span class="card-title">{room.name}</span>
            </div>
            <div class="card-content">
              <p>Комната открыта для посещения всем участникам конференции</p>
            </div>
            <div class="card-action">
              <a use:link={`/meeting/${params.id1}/${room.slug}/`}>войти</a>
              <button
                class="waves-effect waves-light btn red darken-4"
                on:click={async () => {
                  await request(
                    `/meetings/rooms/delete/${params.id1}/`,
                    'POST',
                    {
                      id: room.id,
                    }
                  )

                  rooms.update(data => data.filter(r => r.id !== room.id))
                }}><i class="material-icons left">delete</i>удалить</button
              >
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Modal Structure -->
  <div id="add" class="modal">
    <div class="modal-content">
      <h4>Добавить комнату</h4>

      <div class="input-field">
        <input id="name" type="text" bind:value={name} />
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
        on:click={addClickHandler}
        >Добавить
        <i class="material-icons right">add</i>
      </button>
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
</style>
