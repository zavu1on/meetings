export interface IUser {
  id: number
  first_name: string
  last_name: string
  patronymic: string
}

export interface IRoomImage {
  id: number
  name: string
  preview_image: string
}

export interface IRoom {
  id: number
  name: string
  slug: string

  can_customers_speak: boolean
  do_loud_voice: boolean
  show_customers_video: boolean

  room_image: IRoomImage
}

export interface IMeeting {
  id: number
  name: string
  slug: string
}
