<script lang="ts">
  import { onMount } from 'svelte'
  import { push } from 'svelte-spa-router'
  import { writable } from 'svelte/store'
  import Loader from '../components/Loader.svelte'
  import request from '../request'
  import auth from '../store/auth'
  import Peer from 'peerjs'

  // todo переделать перемещение
  // todo добавить перемещение по щелчку

  export let params

  async function getUserMedia(
    video: boolean,
    audio: boolean
  ): Promise<MediaStream> {
    try {
      return await navigator.mediaDevices.getUserMedia({ video, audio })
    } catch (e) {
      M.toast({
        html: 'Медиа девайс не был найден!',
        classes: 'red darken-4',
      })

      return new MediaStream()
    }
  }

  const step = 1
  let isLoaded = false

  const peer = new Peer()

  const users = writable<
    {
      id: number
      peerId: string
      x: number
      y: number
      name: string
      avatarUrl: string
      isAudio: boolean
      isVideo: boolean
    }[]
  >([])

  const toggleAudio = async () => {
    users.update(state =>
      state.map(u => {
        if (u.id === $auth.id) {
          u.isAudio = !u.isAudio
        }

        return u
      })
    )

    await toggle()
  }
  const toggleVideo = async () => {
    users.update(state =>
      state.map(u => {
        if (u.id === $auth.id) {
          u.isVideo = !u.isVideo
        }

        return u
      })
    )

    await toggle()
  }
  const toggle = async () => {
    const me = $users.find(u => u.id === $auth.id)

    if (me.isVideo || me.isAudio) {
      const stream = await getUserMedia(me.isVideo, me.isAudio)
      const video = document.getElementById(`video-${me.id}`)

      // @ts-ignore
      video.srcObject = stream
      // @ts-ignore
      video.play()

      $users
        .filter(u => u.id !== $auth.id)
        .forEach(u => {
          var mediaCall = peer.call(u.peerId, stream)
          mediaCall.on('stream', function (remoteStream) {
            const video = document.getElementById(`video-${u.id}`)

            // @ts-ignore
            video.srcObject = remoteStream
            // @ts-ignore
            video.play()
          })
        })
    }

    WS.send(
      JSON.stringify({
        type: 'move',
        data: $users.find(u => u.id === $auth.id),
      })
    )
  }

  onMount(async () => {
    try {
      await request(`/meetings/rooms/get/${params.id1}/${params.id2}/`)
    } catch (e) {
      M.toast({
        html: `<span>Вы не можете зайти на конференцию</span>`,
        classes: 'red darken-4',
      })
      push('/')
    }
  })

  const WS = new WebSocket(
    'ws://127.0.0.1:8000/meetings/moving' +
      `/${params.id1}/${params.id2}/${localStorage.getItem('access')}/`
  )

  window.onbeforeunload = () => {
    WS.close(1)
  }

  WS.onopen = async () => {
    const r = await request('/auth/get-user-data/')
    auth.set(r.data)

    peer.on('call', async function (call) {
      const me = $users.find(u => u.id === $auth.id)

      if (me.isVideo || me.isAudio) {
        const stream = await getUserMedia(me.isVideo, me.isAudio)

        call.answer(stream)
      } else {
        call.answer(new MediaStream())
      }

      const id = $users.find(u => u.peerId === call.peer).id

      call.on('stream', function (remoteStream) {
        const video = document.getElementById(`video-${id}`)

        // @ts-ignore
        video.srcObject = remoteStream
        // @ts-ignore
        video.play()
      })
    })

    users.set([
      {
        id: $auth.id,
        peerId: peer.id,
        x: Math.floor(Math.random() * 101),
        y: Math.floor(Math.random() * 101),
        name: $auth.username,
        avatarUrl: $auth.avatarUrl,
        isAudio: false,
        isVideo: false,
      },
    ])

    WS.send(
      JSON.stringify({
        type: 'move',
        data: $users.find(u => u.id === $auth.id),
      })
    )
    WS.send(
      JSON.stringify({
        type: 'enter',
        data: $auth.id,
      })
    )

    isLoaded = true
  }
  WS.onmessage = async event => {
    const data = JSON.parse(event.data)

    if (data.users) {
      // data.type === 'move'
      users.set(data.users)
    } else if (data.type === 'enter' && data.data === $auth.id) {
      M.toast({
        html: `Подвигайтесь, чтобы видеть лица других пользователей`,
        classes: 'light-green darken-3',
      })
    }
  }

  document.addEventListener('keypress', event => {
    const user = $users.find(u => u.id === $auth.id)

    if (event.key.toLowerCase() === 'w' && user.y - step > 0) {
      users.update(state =>
        state.map(u => {
          if (u.id === $auth.id) {
            u.y -= step
          }

          return u
        })
      )
    } else if (event.key.toLowerCase() === 's' && user.y + step < 100) {
      users.update(state =>
        state.map(u => {
          if (u.id === $auth.id) {
            u.y += step
          }

          return u
        })
      )
    } else if (event.key.toLowerCase() === 'a' && user.x - step > 0) {
      users.update(state =>
        state.map(u => {
          if (u.id === $auth.id) {
            u.x -= step
          }

          return u
        })
      )
    } else if (event.key.toLowerCase() === 'd' && user.x + step < 100) {
      users.update(state =>
        state.map(u => {
          if (u.id === $auth.id) {
            u.x += step
          }

          return u
        })
      )
    }

    WS.send(
      JSON.stringify({
        type: 'move',
        data: $users.find(u => u.id === $auth.id),
      })
    )
  })
</script>

{#if isLoaded}
  <div class="canvas">
    {#each $users as user}
      <div class="user" style={`left: ${user.x}%; top: ${user.y}%`}>
        {#if user.isVideo}
          <video id={`video-${user.id}`} />
        {:else if user.isAudio}
          <video id={`video-${user.id}`} style="display: none" />
          <img src={user.avatarUrl} alt="avatar" />
        {:else}
          <img src={user.avatarUrl} alt="avatar" />
        {/if}
        <span>{user.name}</span>
      </div>
    {/each}
  </div>
  <footer class="yellow darken-4">
    <div class="container">
      <div class="row">
        <div class="col s2">
          <button
            class="waves-effect waves-light btn light-green darken-3"
            on:click={toggleAudio}
            ><i class="material-icons left"
              >{$users.find(u => u.id === $auth.id).isAudio
                ? 'mic_off'
                : 'mic'}</i
            >{$users.find(u => u.id === $auth.id).isAudio ? 'выкл' : 'вкл'}.
            звук</button
          >
        </div>
        <div class="col s2">
          <button
            class="waves-effect waves-light btn light-green darken-3"
            on:click={toggleVideo}
            ><i class="material-icons left"
              >{$users.find(u => u.id === $auth.id).isVideo
                ? 'videocam_off'
                : 'videocam'}</i
            >{$users.find(u => u.id === $auth.id).isVideo ? 'выкл' : 'вкл'}.
            видео</button
          >
        </div>
        <div class="col s8">q</div>
      </div>
    </div>
  </footer>
{:else}
  <div class="container loader-container">
    <Loader />
  </div>
{/if}

<style>
  .canvas {
    width: 100%;
    flex: 1;
    background-image: url('https://quban.ru/upload/iblock/99c/99cb40fc5fdf85dd917ac1d60d9fd122.jpg');
    overflow: hidden;
    color: #fff;
    position: relative;
  }

  .user {
    width: 75px;
    height: 75px;
    position: absolute;
  }

  .user img,
  .user video {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
  }

  .user video {
    transform: rotateY(180deg);
  }

  .user span {
    position: absolute;
    bottom: 4px;
    left: 4px;
    font-size: 15px;
    overflow: hidden;
  }

  footer {
    width: 100%;
    height: 80px;
  }

  .container,
  .row,
  .col {
    height: 100%;
  }

  .col {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .loader-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
  }
</style>
