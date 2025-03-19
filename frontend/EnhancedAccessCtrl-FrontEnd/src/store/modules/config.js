import Cookies from 'js-cookie'

const state = {
  mock: Cookies.get('mock') === 'true' // 从 Cookies 中读取，默认值为 true
}

const mutations = {
  SET_MOCK(state, value) {
    state.mock = value
    Cookies.set('mock', value, { expires: 1 }) // 将 mock 状态存储到 Cookies
  }
}

const actions = {
  setMock({ commit }, value) {
    commit('SET_MOCK', value)
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
