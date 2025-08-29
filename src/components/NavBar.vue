<script setup>
import { ref, onMounted } from 'vue'
import ThemeToggle from './ThemeToggle.vue'
const open = ref(false)


// Close mobile menu on route change via hash (accessibility safe)
onMounted(()=>{
window.addEventListener('resize', ()=>{ if(window.innerWidth>768) open.value=false })
})
</script>

<template>
<nav class="nav">
<div class="container nav-inner" :class="{open: open}">
<a class="brand" href="/" @click.prevent="$router.push('/')">Plant'X</a>
<button class="menu" aria-label="Toggle menu" aria-expanded="open" @click="open=!open">
<span></span><span></span><span></span>
</button>
<ul class="links" @click="open=false">
<li><router-link to="/"> Home </router-link></li>
<li><RouterLink to="/garden">Garden</RouterLink></li>
<li><RouterLink to="/urbanwild">Urban & Wild</RouterLink></li>
<li><RouterLink to="/community">Community</RouterLink></li>
</ul>
<ThemeToggle class="theme" />
</div>
</nav>
</template>

<style scoped>
.nav{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:1px solid color-mix(in oklab, var(--fg) 10%, transparent);backdrop-filter:saturate(1.1) blur(6px)}
.nav-inner{display:flex;align-items:center;gap:.5rem;min-height:72px}
.brand{font-weight:800;letter-spacing:.3px}
.links{display:flex;gap:1rem;margin-left:auto}
.links a{padding:.5rem .6rem;border-radius:10px}
.links a.router-link-active{background:color-mix(in oklab, var(--fg) 8%, transparent)}
.theme{margin-left:.5rem}
.menu{display:inline-flex;flex-direction:column;gap:4px;border:0;background:transparent;padding:.5rem;margin-right:.25rem}
.menu span{width:20px;height:2px;background:var(--fg);border-radius:1px}
@media(max-width:768px){
.links{position:fixed;inset:72px 0 auto 0;background:var(--bg);padding:1rem 1.25rem;display:grid;gap:.5rem;border-bottom:1px solid color-mix(in oklab, var(--fg) 10%, transparent);transform:translateY(-110%);transition:transform .24s ease}
.nav-inner.open .links{transform:translateY(0)}
}
</style>