import { writable } from 'svelte/store'
import type { IRoomImage } from './../types/meetings'

const images = writable<IRoomImage[]>([])

export default images
