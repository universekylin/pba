// src/api/matchStats.ts
import axios from 'axios'

export type PlayerRow = {
  player_id: number
  team_id: number
  one: number
  two: number
  three: number
  foul: number
  points: number
  number?: number   // 球衣号码，可选
  name?: string     // 球员名字，可选
}

export type Totals = {
  light: { pts: number; fouls: number }
  dark:  { pts: number; fouls: number }
}

// 获取整场 boxscore
export async function fetchBoxscore(matchId: number) {
  const { data } = await axios.get(`/api/matches/${matchId}/boxscore`)
  return data as {
    players: PlayerRow[]
    totals: Totals
    home_team_id: number
    away_team_id: number
  }
}

// 录入 +1 / -1
export async function postDelta(
  matchId: number,
  playerId: number,
  field: 'one'|'two'|'three'|'foul',
  delta: 1 | -1,
) {
  const { data } = await axios.post(`/api/matches/${matchId}/stat`, {
    player_id: playerId,
    field,
    delta,
  })
  return data as { updated: PlayerRow & { field: string; value: number }, totals: Totals }
}
