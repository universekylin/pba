// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

// ===== Public =====
import HomeView from '@/views/HomeView.vue'
import ChampD1 from '@/views/ChampD1.vue'
import Division2 from '@/views/Division2.vue'
import EnrolIndividual from '@/views/EnrolIndividual.vue'
import EnrolTeam from '@/views/EnrolTeam.vue'

// ===== Admin layout =====
import AdminPage from '@/views/AdminPage.vue'

// ===== Admin pages =====
import AdminOverview from '@/views/admin/AdminOverview.vue'
import ManageTeams from '@/views/admin/ManageTeams.vue'
import PlayersManage from '@/views/admin/PlayersManage.vue'
import ScheduleManage from '@/views/admin/ScheduleManage.vue'
import RoundDetail from '@/views/admin/RoundDetail.vue'
import MatchEdit from '@/views/admin/MatchEdit.vue'

// Lazy-loaded pages
const TeamSchedule = () => import('@/views/TeamSchedule.vue')
const ChampionTeamSchedule = () => import('@/views/admin/ChampionTeamSchedule.vue')
const MatchDetail = () => import('@/views/MatchDetail.vue')
const ChampionMatchDetail = () => import('@/views/admin/ChampionMatchDetail.vue')

const routes = [
  // ===== Public =====
  { path: '/', name: 'home', component: HomeView },
  { path: '/champ-d1', name: 'champD1', component: ChampD1 },
  { path: '/division-2', name: 'division2', component: Division2 },
  { path: '/enrolment/individual', name: 'enrolIndividual', component: EnrolIndividual },
  { path: '/enrolment/team', name: 'enrolTeam', component: EnrolTeam },

  // Public: team schedule (read-only)
  {
    path: '/teams/:id/schedule',
    name: 'teamSchedule',
    component: TeamSchedule,
    meta: { public: true },
    props: true,
  },

  // Public: match detail (read-only)
  {
    path: '/matches/:id',
    name: 'matchDetail',
    component: MatchDetail,
    meta: { public: true },
    props: true,
  },

  // ===== Admin (without AdminPage layout) =====
  // Admin alias for team schedule (same UI as public)
  {
    path: '/admin-panel/teams/:id/schedule',
    name: 'teamScheduleAdminAlias',
    component: TeamSchedule,
    meta: { requiresAdmin: true },
    props: true,
  },

  // Admin: Champion-only team schedule
  {
    path: '/admin-panel/teams/:id/champion-schedule',
    name: 'adminChampionTeamSchedule',
    component: ChampionTeamSchedule,
    meta: { requiresAdmin: true },
    props: true,
  },

  // Admin: Champion match detail (editable)
  {
    path: '/admin-panel/matches/:id',
    name: 'championMatchDetail',
    component: ChampionMatchDetail,
    meta: { requiresAdmin: true },
    props: true,
  },

  // ===== Admin with layout =====
  {
    path: '/admin-panel',
    component: AdminPage,
    meta: { requiresAdmin: true, layout: 'admin' },
    children: [
      { path: '', name: 'adminHome', component: AdminOverview },
      { path: 'teams', name: 'manageTeams', component: ManageTeams },

      // Existing players manager route (ScheduleManage.vue uses this name)
      {
        path: 'teams/:id/players',
        name: 'playersManage',
        component: PlayersManage,
        props: true,
      },
      // Convenience alias (optional): /admin-panel/teams/:id -> PlayersManage
      {
        path: 'teams/:id',
        name: 'manageTeam',
        component: PlayersManage,
        props: true,
      },

      { path: 'matches', name: 'matchesManage', component: ScheduleManage, alias: 'schedule' },
      { path: 'matches/round/:no', name: 'roundDetail', component: RoundDetail, props: true },
      { path: 'matches/:id/edit', name: 'matchEdit', component: MatchEdit, props: true },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// ===== Guards: simple admin password + graceful downgrade for some admin aliases =====
router.beforeEach((to, from, next) => {
  // Public pages: allow
  if (to.meta && to.meta.public) return next()

  const isAdminOk = sessionStorage.getItem('ADMIN_OK') === '1'
  const isChampion = (v) =>
    ['champion', 'champ', 'c', 'championship'].includes(String(v || '').toLowerCase())

  // If accessing admin schedule alias but division is not champion -> downgrade to public
  if (to.name === 'teamScheduleAdminAlias' && !isChampion(to.query.division)) {
    return next({
      name: 'teamSchedule',
      params: to.params,
      query: to.query,
      replace: true,
    })
  }

  // If not admin, downgrade admin schedule/detail to public pages
  if (!isAdminOk) {
    if (to.name === 'teamScheduleAdminAlias' || to.name === 'adminChampionTeamSchedule') {
      return next({
        name: 'teamSchedule',
        params: to.params,
        query: to.query,
        replace: true,
      })
    }
    if (to.name === 'championMatchDetail') {
      return next({
        name: 'matchDetail',
        params: to.params,
        query: to.query,
        replace: true,
      })
    }
  }

  // Other admin pages: prompt simple password
  const needAdmin = to.matched.some((r) => r.meta && r.meta.requiresAdmin)
  if (needAdmin) {
    if (isAdminOk) return next()
    const pwd = window.prompt('请输入管理员访问密码：')
    if (pwd === '123456') {
      sessionStorage.setItem('ADMIN_OK', '1')
      return next()
    }
    if (pwd === null) return next(false)
    alert('密码错误')
    return next(false)
  }

  next()
})

export default router
