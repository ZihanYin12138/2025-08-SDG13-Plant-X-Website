<script setup>
import { onMounted } from 'vue'

const BASE = 'http://plantx-alb-1374376113.us-east-1.elb.amazonaws.com'

async function hit(url) {
  const t0 = performance.now()
  try {
    const res = await fetch(url, { headers: { Accept: 'application/json' } })
    const ms = Math.round(performance.now() - t0)
    const text = await res.text()

    console.log('%c[API]%c ' + url, 'color:#10b981;font-weight:bold', 'color:inherit')
    console.log('status:', res.status, res.ok ? 'OK' : 'FAIL', '| time:', `${ms} ms`)

    try {
      console.log('json:', JSON.parse(text))
    } catch {
      console.log('body (text):', text.slice(0, 800))
    }
  } catch (err) {
    console.log('%c[API ERROR]', 'color:#ef4444;font-weight:bold', url, err?.message || err)
  }
}

onMounted(() => {
  hit(`${BASE}/api/map/data/2022`)
  hit(`${BASE}/api/map/geojson`)
  hit(`${BASE}/api/chart/data/${encodeURIComponent('New South Wales')}`)
})
</script>


<template>
  <section class="section">
    <div class="container">
    <h2 class="title">Community</h2>
    <p class="lead">Join gardening enthusiasts to share experiences and collaborate on climate-positive actions.</p>
    </div>
  </section>

  <section>
    <div class="container">
      <p></p>
    </div>
  </section>
</template>

<style scoped>

</style>
