import { writable } from 'svelte/store'
import type { IMeeting } from './../types/meetings'

const meetings = writable<IMeeting[]>([])

export default meetings
