import { createRouter, createWebHistory } from 'vue-router'

// ===== Public (eager) =====
import HomeView from '@/views/HomeView.vue'
import ChampD1 from '@/views/ChampD1.vue'
import Division2 from '@/views/Division2.vue'
import EnrolIndividual from '@/views/EnrolIndividual.vue'
import EnrolTeam from '@/views/EnrolTeam.vue'

// ===== Admin pages (eager) =====
import Ladder from '@/views/admin/Ladder.vue'
import AdminPage from '@/views/AdminPage.vue'
import AdminOverview from '@/views/admin/AdminOverview.vue'
import ManageTeams from '@/views/admin/ManageTeams.vue'
import PlayersManage from '@/views/admin/PlayersManage.vue'
import ScheduleManage from '@/views/admin/ScheduleManage.vue'
import RoundDetail from '@/views/admin/RoundDetail.vue'
import MatchEdit from '@/views/admin/MatchEdit.vue'

// ===== Lazy-loaded public/admin read-only pages =====
const TeamSchedule = () => import('@/views/TeamSchedule.vue')
const ChampionTeamSchedule = () => import('@/views/admin/ChampionTeamSchedule.vue')
const MatchDetail = () => import('@/views/MatchDetail.vue')
const ChampionMatchDetail = () => import('@/views/admin/ChampionMatchDetail.vue')
const AboutUs = () => import('@/views/AboutUs.vue')
const HallOfFame = () => import('@/views/HallOfFame.vue')
const Policy = () => import('@/views/Policy.vue')

// Public 专用页面
const PublicRound = () => import('@/views/PublicRound.vue')        // Champ + D1
const PublicRoundD2 = () => import('@/views/PublicRoundD2.vue')    // D2
const LadderPublic = () => import('@/views/LadderPublic.vue')      // 公共 Ladder

// Player Ranking
const PlayerRankingChampion = () => import('@/views/PlayerRankingChampion.vue')
const PlayerRankingD1 = () => import('@/views/PlayerRankingD1.vue')
const PlayerRankingD2 = () => import('@/views/PlayerRankingD2.vue')

// Teams & TeamRoster（公开只读）
const Teams = () => import('@/views/Teams.vue')
const TeamRoster = () => import('@/views/TeamRoster.vue')

// Champion 比赛详情（只读版）
const ChampionMatchPublic = () => import('@/views/ChampionMatchPublic.vue')

const routes = [
  // ===== Public =====
  { path: '/', name: 'home', component: HomeView },
  { path: '/champ-d1', name: 'champD1', component: ChampD1 },
  { path: '/division-2', name: 'division2', component: Division2 },
  { path: '/enrolment/individual', name: 'enrolIndividual', component: EnrolIndividual },
  { path: '/enrolment/team', name: 'enrolTeam', component: EnrolTeam },
  { path: '/about', name: 'about', component: AboutUs, meta: { public: true } },
  { path: '/hall-of-fame', name: 'hallOfFame', component: HallOfFame, meta: { public: true } },
  { path: '/policy', name: 'policy', component: Policy, meta: { public: true } },

  // Public: team schedule / roster
  { path: '/teams/:id/schedule', name: 'teamSchedule', component: TeamSchedule, meta: { public: true }, props: true },
  { path: '/teams/:id/players', name: 'teamRosterPublic', component: TeamRoster, meta: { public: true, hideNav: true }, props: true },

  // ===== Player Ranking =====
  { path: '/s8/ranking', redirect: '/s8/ranking/champ', meta: { public: true } },
  { path: '/s8/ranking/champ', name: 'PlayerRankingChampion', component: PlayerRankingChampion, meta: { public: true }, props: { division: 'champ' } },
  { path: '/s8/ranking/div1',  name: 'PlayerRankingD1',       component: PlayerRankingD1,       meta: { public: true } },
  { path: '/s8/ranking/div2',  name: 'PlayerRankingD2',       component: PlayerRankingD2,       meta: { public: true } },

  // ===== Match detail（新增规范含 division 的路由，兼容旧地址） =====
  { path: '/:division(champion|d1|d2)/matches/:id', name: 'matchDetailWithDiv', component: MatchDetail, meta: { public: true }, props: true },
  { path: '/matches/:id', name: 'matchDetail', component: MatchDetail, meta: { public: true }, props: true },
  { path: '/games/:id',   name: 'gameDetail',  component: MatchDetail, meta: { public: true }, props: true },

  // Champion match (readonly)
  { path: '/s8/champ/matches/:id', name: 'championMatchPublic', component: ChampionMatchPublic, meta: { public: true }, props: true },

  // ⚠️ Round 页面
  { path: '/division-2/round/:no', name: 'PublicRoundD2', component: PublicRoundD2, meta: { public: true }, props: true },
  { path: '/:division/round/:no',  name: 'PublicRound',   component: PublicRound,   meta: { public: true }, props: true },

  // Public: Ladder & Teams
  { path: '/s8/ladder', name: 'ladderPublic', component: LadderPublic, meta: { public: true } },
  { path: '/s8/teams',  name: 'teamsPage',    component: Teams,        meta: { public: true } },

  // ===== Admin (without AdminPage layout) =====
  { path: '/admin-panel/teams/:id/schedule',          name: 'teamScheduleAdminAlias',    component: TeamSchedule,         meta: { requiresAdmin: true }, props: true },
  { path: '/admin-panel/teams/:id/champion-schedule', name: 'adminChampionTeamSchedule', component: ChampionTeamSchedule, meta: { requiresAdmin: true }, props: true },
  { path: '/admin-panel/matches/:id',                 name: 'championMatchDetail',       component: ChampionMatchDetail,  meta: { requiresAdmin: true }, props: true },

  // ===== Admin with layout =====
  {
    path: '/admin-panel',
    component: AdminPage,
    meta: { requiresAdmin: true, layout: 'admin' },
    children: [
      { path: '', name: 'adminHome', component: AdminOverview },
      { path: 'teams', name: 'manageTeams', component: ManageTeams },
      { path: 'teams/:id/players', name: 'playersManage', component: PlayersManage, props: true },
      { path: 'teams/:id', name: 'manageTeam', component: PlayersManage, props: true },
      { path: 'matches', name: 'matchesManage', component: ScheduleManage, alias: 'schedule' },
      { path: 'matches/round/:no', name: 'roundDetail', component: RoundDetail, props: true },
      { path: 'matches/:id/edit', name: 'matchEdit', component: MatchEdit, props: true },
      { path: 'ladder', name: 'ladder', component: Ladder },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

// ===== Guards =====
router.beforeEach((to, from, next) => {
  // Public pages
  if (to.meta && to.meta.public) return next()

  const isAdminOk = sessionStorage.getItem('ADMIN_OK') === '1'
  const isChampion = (v) =>
    ['champion', 'champ', 'c', 'championship'].includes(String(v || '').toLowerCase())

  // Admin alias -> downgrade when not champion
  if (to.name === 'teamScheduleAdminAlias' && !isChampion(to.query.division)) {
    return next({ name: 'teamSchedule', params: to.params, query: to.query, replace: true })
  }

  // Not admin -> downgrade admin-only pages
  if (!isAdminOk) {
    if (to.name === 'teamScheduleAdminAlias' || to.name === 'adminChampionTeamSchedule') {
      return next({ name: 'teamSchedule', params: to.params, query: to.query, replace: true })
    }
    if (to.name === 'championMatchDetail') {
      return next({ name: 'matchDetail', params: to.params, query: to.query, replace: true })
    }
  }

  // Password gate
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
