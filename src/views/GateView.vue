<template>
  <div class="gate-wrap">
    <form class="gate-box" @submit.prevent="submit">
      <h1>请输入访问密码</h1>
      <input v-model="pwd" type="password" placeholder="Password" autofocus />
      <button type="submit">解锁</button>
      <p v-if="err" class="err">{{ err }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const pwd = ref('')
const err = ref('')


const PASSWORD = '123456' // <- 改成你想要的密码

function submit () {
  err.value = ''
  if (pwd.value === PASSWORD) {
    sessionStorage.setItem('gate:ok', '1') // 标记已解锁
    const redirect = route.query.redirect || '/'
    router.replace(String(redirect))
  } else {
    err.value = 'Wrong Password'
  }
}
</script>

<style scoped>
.gate-wrap{
  min-height:100vh; display:flex; align-items:center; justify-content:center; background:#f3f4f6;
}
.gate-box{
  width:100%; max-width:380px; padding:24px; background:#fff; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,.06);
  display:flex; flex-direction:column; gap:12px; align-items:stretch;
}
.gate-box h1{ margin:0; font-size:18px; text-align:center; }
.gate-box input{ padding:10px 12px; border-radius:8px; border:1px solid #e5e7eb; }
.gate-box button{ padding:10px; border-radius:8px; border:0; background:#111827; color:white; font-weight:600; cursor:pointer; }
.err{ color:#dc2626; text-align:center; margin-top:6px; }
</style>
