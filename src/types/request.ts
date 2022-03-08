export interface IResponse<T> {
  status: number
  data: T
  headers: Headers
}

export type Method = 'GET' | 'POST' | 'DELETE' | 'PUT'
