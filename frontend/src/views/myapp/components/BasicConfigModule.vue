<template>
  <base-module
    title="Basic Config"
    icon="Setting"
    :state="state"
    :data="data"
  >
    <template #actions="{ disabled }">
      <router-link :to="'/myapp/edit_app/' + id" class="link-type">
        <el-button type="success" size="small" :disabled="disabled">Edit Basic Config</el-button>
      </router-link>
    </template>
  </base-module>
</template>

<script>
import BaseModule from './BaseModule'

export default {
  name: 'BasicConfigModule',
  components: {
    BaseModule
  },
  props: {
    id: {
      type: String,
      required: true
    },
    state: {
      type: String,
      default: 'active'
    },
    data: {
      type: Object,
      default: () => ({ isCompleted: false })
    }
  }
}
</script>
