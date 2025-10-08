// src/api/schedule.js
// 说明：使用你项目里的 axios 实例（已设置 baseURL='/api'）
import axios from '@/api/axios'

/**
 * 获取某支球队在指定轮次区间内的赛程
 * 后端支持：/api/teams/:teamId/schedule?from=&to=&division=&season=&use_raw=1
 *
 * @param {number} teamId
 * @param {number} [from=1]
 * @param {number} [to=11]
 * @param {string} [division]    'd1'|'d2'|'champion'（可选）
 * @param {Object} [opts]
 * @param {string}  [opts.season]
 * @param {boolean} [opts.useRaw=false]  是否直接使用 DB 原始 status（use_raw=1）
 * @returns {Promise<Object>}
 */
export async function fetchTeamSchedule(teamId, from = 1, to = 11, division, opts = {}) {
  const params = { from, to }
  if (division) params.division = division
  if (opts.season) params.season = opts.season
  if (opts.useRaw) params.use_raw = 1

  const res = await axios.get(`/teams/${teamId}/schedule`, { params })
  return res?.data ?? res
}

/** 便捷：Champion 分区赛程（默认走 use_raw） */
export function fetchChampionTeamSchedule(teamId, from = 1, to = 11, opts = {}) {
  return fetchTeamSchedule(teamId, from, to, 'champion', { useRaw: true, ...opts })
}
