/** When your routing table is too long, you can split it into small modules **/

import Layout from '@/layout'

const myappRouter = {
  path: '/myapp',
  component: Layout,
  redirect: '/myapp/list',
  name: 'myapp',
  meta: {
    title: 'MYAPP',
    icon: 'table'
  },
  children: [
    // 显示项
    {
      path: 'list',
      component: () => import('@/views/myapp/detection_task'),
      name: 'Detection Task',
      meta: { title: 'Detection Task' } // 保持显示
    },
    {
      path: 'create_app',
      component: () => import('@/views/myapp/new_target'),
      name: 'Create New App',
      meta: { title: 'Create New App' } // 保持显示
    },

    // 隐藏项
    {
      path: 'detail/:id(\\d+)',
      component: () => import('@/views/myapp/detection_task_detail'),
      name: 'Detection Detail',
      meta: { title: 'Detection Detail' },
      hidden: true
    },
    {
      path: 'basic_edit/:id(\\d+)',
      component: () => import('@/views/myapp/basic_edit'),
      name: 'Basic Config',
      meta: { title: 'Basic Config' },
      hidden: true
    },
    {
      path: 'edit_feature_list/:id(\\d+)',
      component: () => import('@/views/myapp/edit_feature_list'),
      name: 'Edit Feature',
      meta: { title: 'Edit Feature' },
      hidden: true
    },
    {
      path: 'model_report/:id(\\d+)',
      component: () => import('@/views/myapp/model_report'),
      name: 'Model Report',
      meta: { title: 'Model Report' },
      hidden: true
    },
    {
      path: 'detection_config_edit/:id(\\d+)',
      component: () => import('@/views/myapp/detection_config_edit'),
      name: 'Detection Config Edit',
      meta: { title: 'Detection Config Edit' },
      hidden: true
    },
    {
      path: 'api_discovery_result/:id(\\d+)',
      component: () => import('@/views/myapp/api_discovery_result'),
      name: 'Api Discovery Result',
      meta: { title: 'Api Discovery Result' },
      hidden: true
    },
    {
      path: 'api_edit/:id(\\d+)',
      component: () => import('@/views/myapp/api_edit'),
      name: 'Api Edit',
      meta: { title: 'Api Edit' },
      hidden: true
    }
  ]
}

export default myappRouter
