import request from '@/utils/request'

// 获取APP列表
export function fetchAppList(query) {
  return request({
    url: '/api/target-app-list/',
    method: 'get',
    params: query
  })
}

// 获取APP详情
export function getAppDetail(query) {
  return request({
    url: '/api/target-app/',
    method: 'get',
    params: query
  })
}

// 保存APP基本信息
export function putAppBasicInfo(id, data) {
  return request({
    url: '/api/target-app/',
    method: 'put',
    params: { id },
    data
  })
}

// 创建APP
export function postAppBasicInfo(data) {
  return request({
    url: '/api/target-app/',
    method: 'post',
    params: {},
    data
  })
}

// 获取feature List
export function getFeatureList(query) {
  return request({
    url: '/api/detection/features/',
    method: 'get',
    params: query
  })
}

// 创建APP/保存APP基本信息
export function saveFeatureList(app_id, data) {
  return request({
    url: '/api/detection/features/',
    method: 'put',
    params: { app_id },
    data
  })
}

// 保存detection config
export function saveDetectionConfig(app_id, data) {
  return request({
    url: '/api/detection/config/',
    method: 'put',
    params: { app_id },
    data
  })
}

// 开启API发现
export function apiDiscoveryStart(query) {
  return request({
    url: '/api/api-discovery/start/',
    method: 'get',
    params: query
  })
}

// 获取API发现状态
export function getApiDiscoveryStatus(query) {
  return request({
    url: '/api/api-discovery/status/',
    method: 'get',
    params: query
  })
}

// 获取API手动发现状态
export function getApiManualDiscoveryStatus(query) {
  return request({
    url: '/api/api-discovery/manual/status/',
    method: 'get',
    params: query
  })
}

// 开启模型构建
export function modelConstruct(query) {
  return request({
    url: '/api/model-construct',
    method: 'get',
    params: query
  })
}

// 获取模型构建状态
export function getModelConstructStatus(query) {
  return request({
    url: '/api/model-construct/data-collection-status/',
    method: 'get',
    params: query
  })
}

// 开启探测
export function detectionStart(query) {
  return request({
    url: '/api/detection/start/',
    method: 'get',
    params: query
  })
}

// 中断探测
export function detectionPause(query) {
  return request({
    url: '/api/detection/pause/',
    method: 'get',
    params: query
  })
}

// 中断手动api发现
export function apiManualDiscoveryCancel(query) {
  return request({
    url: '/api/api-discovery/cancel/',
    method: 'get',
    params: query
  })
}

// 结束手动api发现
export function apiManualDiscoveryFinish(query) {
  return request({
    url: '/api/api-discovery/finish/',
    method: 'get',
    params: query
  })
}

// 获取检测报告
export function getFinalReport(query) {
  return request({
    url: '/api/detection/record/combination/',
    method: 'get',
    params: query
  })
}

// 获取api列表
export function getApiList(query) {
  return request({
    url: '/api/api-lists/',
    method: 'get',
    params: query
  })
}

// 保存用户api列表
export function putUserApiList(app_id, data) {
  return request({
    url: '/api/v2/user-api-list/',
    method: 'put',
    params: { app_id: app_id },
    data
  })
}
