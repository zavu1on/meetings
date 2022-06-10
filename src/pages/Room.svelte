<script lang="ts">
  import { onMount } from 'svelte'
  import { push } from 'svelte-spa-router'
  import { writable } from 'svelte/store'
  import Loader from '../components/Loader.svelte'
  import request from '../request'
  import auth from '../store/auth'
  import Peer from 'peerjs'

  // todo добавить перемещение по щелчку

  export let params

  async function getUserMedia(
    video: boolean,
    audio: boolean
  ): Promise<MediaStream> {
    try {
      return await navigator.mediaDevices.getUserMedia({ video, audio })
    } catch (e) {
      users.update(state =>
        state.map(u => {
          if (u.id === $auth.id) {
            u.isAudio = false
            u.isVideo = false
          }

          return u
        })
      )

      M.toast({
        html: 'Медиа девайс не был найден',
        classes: 'red darken-4',
      })

      return new MediaStream()
    }
  }

  const step = 0.25
  const moovingProps: {
    w: boolean
    a: boolean
    s: boolean
    d: boolean
  } = {
    w: false,
    a: false,
    s: false,
    d: false,
  }
  let showChat = false
  let showScreenCast = false // admin only
  let isScreenCasting = false
  let isLoaded = false
  let isAdmin: boolean
  let wasNotificated: boolean
  let chatText = ''

  const peer = new Peer({
    config: {
      iceServers: [
        {
          urls: 'stun:stun.develz.org:3478',
        },
      ],
    },
  })
  const screenCastPeer = new Peer({
    config: {
      iceServers: [
        {
          urls: 'stun:stun.develz.org:3478',
        },
      ],
    },
  })

  const users = writable<
    {
      id: number
      peerId: string
      screenCastPeerId: string
      x: number
      y: number
      name: string
      fullName: string
      avatarUrl: string
      isAudio: boolean
      isVideo: boolean
    }[]
  >([])
  const messages = writable<
    {
      name: string
      avatarUrl: string
      text: string
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
  const toggleChat = () => {
    showChat = !showChat
  }
  const toggleScreenCast = async () => {
    showScreenCast = !showScreenCast
    let stream: MediaStream

    if (showScreenCast) {
      try {
        stream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: false,
        })
        stream.getTracks().forEach(t => {
          t.onended = () => {
            isScreenCasting = false
            showScreenCast = false
            WS.send(
              JSON.stringify({
                type: 'toggle',
                data: false,
              })
            )
          }
        })
      } catch (e) {
        showScreenCast = !showScreenCast

        return M.toast({
          html: 'Не получилось сделать захват экрана',
          classes: 'red darken-4',
        })
      }

      $users
        .filter(u => u.id !== $auth.id)
        .forEach(u => {
          var mediaCall = screenCastPeer.call(u.screenCastPeerId, stream)
          mediaCall.on('stream', function (remoteStream) {})
        })

      WS.send(
        JSON.stringify({
          type: 'toggle',
          data: true,
        })
      )
    } else {
      WS.send(
        JSON.stringify({
          type: 'toggle',
          data: false,
        })
      )
    }
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
  const copyInviteLink = async () => {
    const resp = await request('/meetings/get-password/', 'POST', {
      token: params.id1,
    })

    navigator.clipboard.writeText(location.href + '?pass=' + resp.data.password)

    M.toast({
      html: `Ссылка для приглашения скопирована в буфер обмена`,
      classes: 'light-green darken-3',
    })
  }

  onMount(async () => {
    try {
      if (
        location.href.split('?')[1] &&
        location.href.split('?')[1].split('=')[0] === 'pass'
      ) {
        await request('/meetings/enter/', 'POST', {
          url: params.id1,
          password: location.href.split('?')[1].split('=')[1] || null,
        })

        push(location.href.split('?')[0])
        location.reload()
      }

      const { data } = await request(
        `/meetings/rooms/get/${params.id1}/${params.id2}/`
      )
      isAdmin = data.is_admin

      const r = await request('/auth/get-user-data/')

      auth.set(r.data)
      users.set([
        {
          id: $auth.id,
          peerId: peer.id,
          screenCastPeerId: screenCastPeer.id,
          x: Math.floor(Math.random() * 101),
          y: Math.floor(Math.random() * 101),
          name: $auth.username,
          fullName: $auth.fullName,
          avatarUrl: $auth.avatarUrl,
          isAudio: false,
          isVideo: false,
        },
      ])

      WS.send(
        JSON.stringify({
          type: 'enter',
          data: $auth.id,
        })
      )
      WS.send(
        JSON.stringify({
          type: 'move',
          data: $users.find(u => u.id === $auth.id),
        })
      )

      peer.on('call', async function (call) {
        const me = $users.find(u => u.id === $auth.id)

        if (me.isVideo || me.isAudio) {
          const stream = await getUserMedia(me.isVideo, me.isAudio)

          call.answer(stream)
        } else {
          call.answer(new MediaStream())
        }

        const caller = $users.find(u => u.peerId === call.peer)

        call.on('stream', function (remoteStream) {
          const video = document.getElementById(`video-${caller.id}`)
          caller.isVideo = true // кастыльчик

          // @ts-ignore
          video.srcObject = remoteStream
          // @ts-ignore
          video.play().catch(() => {
            WS.send(
              JSON.stringify({
                type: 'enter',
                data: $auth.id,
              })
            )

            if (!wasNotificated) {
              M.toast({
                html: `Подвигайтесь, чтобы видеть лица других пользователей`,
                classes: 'light-green darken-3',
              })

              wasNotificated = true
            }
          })
        })
      })
      screenCastPeer.on('call', async function (call) {
        console.log('call')

        call.answer(new MediaStream())
        isScreenCasting = true // кастыльчик

        call.on('stream', function (remoteStream) {
          const video = document.getElementById(`screencast`)

          // @ts-ignore
          video.srcObject = remoteStream
          // @ts-ignore
          video.play().catch(() => {
            WS.send(
              JSON.stringify({
                type: 'enter',
                data: $auth.id,
              })
            )

            if (!wasNotificated) {
              M.toast({
                html: `Подвигайтесь, чтобы видеть лица других пользователей`,
                classes: 'light-green darken-3',
              })

              wasNotificated = true
            }
          })
        })
      })

      isLoaded = true
    } catch (e) {
      M.toast({
        html: `<span>Вы не можете зайти на конференцию</span>`,
        classes: 'red darken-4',
      })

      push('#/')
    }
  })

  const WS = new WebSocket(
    'ws://127.0.0.1:8000/meetings/moving' +
      `/${params.id1}/${params.id2}/${localStorage.getItem('access')}/`
  )

  window.onbeforeunload = () => {
    WS.close(1)
  }

  WS.onmessage = async event => {
    const data = JSON.parse(event.data)

    if (data.users) {
      // data.type === 'move'
      users.set(data.users)
    } else if (data.type === 'message') {
      messages.update(s => [...s, data.data])
    } else if (data.type === 'toggle') {
      if (typeof data.data === 'boolean') {
        isScreenCasting = data.data
      } else if (data.data === $auth.id) {
        console.log(data.data)

        isScreenCasting = true
      }
    } else if (data.type === 'enter' && data.data !== $auth.id && data.data) {
      toggle()
    }
  }

  document.addEventListener('keydown', event => {
    // @ts-ignore
    for (const el of event.path) {
      if (el.tagName === 'INPUT') return
    }

    moovingProps[event.key.toLocaleLowerCase()] = true
  })
  document.addEventListener('keyup', event => {
    moovingProps[event.key.toLocaleLowerCase()] = false
  })

  setInterval(() => {
    if (moovingProps.a || moovingProps.d || moovingProps.s || moovingProps.w) {
      const user = $users.find(u => u.id === $auth.id)

      if (moovingProps.w && user.y - step > 0) {
        users.update(state =>
          state.map(u => {
            if (u.id === $auth.id) {
              u.y -= step
            }

            return u
          })
        )
      }
      if (moovingProps.s && user.y + step < 100) {
        users.update(state =>
          state.map(u => {
            if (u.id === $auth.id) {
              u.y += step
            }

            return u
          })
        )
      }
      if (moovingProps.a && user.x - step > 0) {
        users.update(state =>
          state.map(u => {
            if (u.id === $auth.id) {
              u.x -= step
            }

            return u
          })
        )
      }
      if (moovingProps.d && user.x + step < 100) {
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
    }
  }, 10)
</script>

{#if isLoaded}
  <div class="canvas">
    {#each $users as user}
      <div
        class="user"
        style={`left: ${user.x}%; top: ${user.y}%`}
        title={user.fullName}
      >
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
    {#if showChat}
      <div class="chat">
        <h5>Чат</h5>
        <div class="content">
          {#each $messages as message}
            <div class="message">
              <div class="logo">
                <img src={message.avatarUrl} alt="avatar" />
                <span>{message.name}</span>
              </div>
              <div class="text">{message.text}</div>
            </div>
          {/each}
        </div>
        <div class="form">
          <div class="input-field">
            <input id="message" type="text" bind:value={chatText} />
            <label for="message">Сообщение</label>
          </div>
          <button
            class="btn waves-effect waves-light amber darken-4"
            on:click={() => {
              if (chatText.trim() === '') {
                return M.toast({
                  html: `Сообщение не может быть пустым`,
                  classes: 'red darken-4',
                })
              }

              WS.send(
                JSON.stringify({
                  type: 'message',
                  data: {
                    name: $auth.username,
                    avatarUrl: $auth.avatarUrl,
                    text: chatText,
                  },
                })
              )
              chatText = ''
            }}
            >Отправить
            <i class="material-icons right">send</i>
          </button>
        </div>
      </div>
    {/if}
    {#if isScreenCasting}
      <video id="screencast" />
    {/if}
  </div>
  <footer class="yellow darken-4">
    <div class="container">
      <div class="row">
        <div class="col s2">
          <button
            class="waves-effect waves-light btn light-green darken-3"
            on:click={toggleAudio}
            ><i class="material-icons left"
              >{$users.find(u => u.id === $auth.id)?.isAudio
                ? 'mic_off'
                : 'mic'}
            </i>{$users.find(u => u.id === $auth.id)?.isAudio ? 'выкл' : 'вкл'}.
            звук</button
          >
        </div>
        <div class="col s2">
          <button
            class="waves-effect waves-light btn light-green darken-3"
            on:click={toggleVideo}
            ><i class="material-icons left"
              >{$users.find(u => u.id === $auth.id)?.isVideo
                ? 'videocam_off'
                : 'videocam'}</i
            >{$users.find(u => u.id === $auth.id)?.isVideo ? 'выкл' : 'вкл'}.
            видео</button
          >
        </div>
        <div class="col s3">
          {#if isAdmin}
            <button
              class="waves-effect waves-light btn light-green darken-3"
              on:click={toggleScreenCast}
              ><i class="material-icons left"
                >{showScreenCast ? 'stop_screen_share' : 'screen_share'}</i
              >{showScreenCast ? 'скрыть' : 'демонстрировать'} экран</button
            >
          {/if}
        </div>
        <div class="col s1" />
        <div class="col s2">
          <button
            class="waves-effect waves-light btn light-green darken-3"
            on:click={copyInviteLink}
            ><i class="material-icons left">share</i>Пригласить</button
          >
        </div>
        <div class="col s2">
          <button
            class="waves-effect waves-light btn light-green darken-3"
            on:click={toggleChat}
            ><i class="material-icons left"
              >{showChat ? 'chat_bubble_outline' : 'chat_bubble'}</i
            >{showChat ? 'скрыть' : 'показать'} чат</button
          >
        </div>
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

  .chat {
    display: flex;
    flex-direction: column;
    background: #ffb74d;
    border-radius: 16px;
    position: absolute;
    right: 0;
    bottom: 0;
    height: 90%;
    width: 20%;
    margin: 8px;
    box-shadow: 0 2px 2px 0 #ffb74d, 0 3px 1px -2px #ffb74d, 0 1px 5px 0 #ffb74d;
  }

  h5 {
    margin-left: 8px;
    font-size: 2rem;
  }

  .content {
    width: 100%;
    max-height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    flex: 1;
  }

  .message {
    margin: 6px;
    margin-top: 12px;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }

  .logo {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-right: 18px;
  }

  .logo img {
    width: 42px;
    height: 42px;
    object-fit: cover;
    border-radius: 50%;
  }

  .logo span {
    font-size: 1.2rem;
    margin-top: -4px;
  }

  .text {
    font-size: 1.1rem;
  }

  .form {
    margin-bottom: 8px;
    padding: 8px;
    width: 100%;
  }

  .form input {
    border-bottom-color: #fff;
  }

  .form label {
    color: #fff;
  }

  #screencast {
    position: absolute;
    top: 0;
    left: 0;
    height: 90%;
    width: 100%;
    margin-top: 1%;
  }

  @media screen and (max-width: 1200px) {
    .chat {
      width: 40%;
    }
  }

  @media screen and (max-width: 600px) {
    .chat {
      width: 50%;
    }
  }
</style>
