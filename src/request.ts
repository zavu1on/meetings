import type { IResponse, Method } from './types/request'

export const BASE_URL = 'http://localhost:8000/api/v1' // http://localhost:8000

function getCookie(name: string) {
  var cookieValue = null
  if (document.cookie && document.cookie !== '') {
    var cookies = document.cookie.split(';')
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim()
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue!
}

export default async function request<R = any>(
  url: string,
  method: Method = 'GET',
  data: any = null,
  headers: HeadersInit = {},
  useCredentials: boolean = true
): Promise<IResponse<R>> | never {
  headers = {
    ...headers,
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken'),
  }

  if (useCredentials) {
    headers['Authorization'] = `Bearer ${localStorage.getItem('access')}`
  }

  const resp = await fetch(BASE_URL + url, {
    method,
    headers,
    body: data ? JSON.stringify(data) : data,
  })

  let json
  try {
    json = await resp.json()
  } catch (e) {
    json = {}
  }

  if (!resp.ok) {
    if (json.detail === 'Invalid authentication. Could not decode token.') {
      const access_resp = await fetch(BASE_URL + '/auth/refresh-token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
          token: localStorage.getItem('refresh'),
        }),
      })
      const access_json = await access_resp.json()

      if (
        access_json.detail ===
        'Токен повтора истек, необходима повторная авторизация!'
      ) {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        location.replace('/#/login/')
        location.reload()

        return
      }

      localStorage.setItem('access', access_json.access_token)

      return request(url, method, data, headers, useCredentials)
    } else if (
      json.detail === 'Такой токен не зарегистрирован!' ||
      json.detail === 'Вы используете чужой токен!' ||
      json.detail === 'Такой пользователь не найден!'
    ) {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')

      location.replace('/#/login/')
      location.reload()
    } else if (resp.status === 406) {
      let html = '<span>'
      for (const [k, v] of Object.entries(json.serialize_error)) {
        html += `<b>${k}</b> - ${v}<br>`
      }

      M.toast({
        html: html + '</span>',
        classes: 'red darken-4',
      })
    } else {
      M.toast({
        html: `<span>Что-то пошло не так: <b>${json.detail}</b></span>`,
        classes: 'red darken-4',
      })
    }

    throw Error(
      `Request failed with status code ${resp.status}.\nDetail: ${json.detail}`
    )
  }

  return {
    data: json,
    status: resp.status,
    headers: resp.headers,
  }
}
