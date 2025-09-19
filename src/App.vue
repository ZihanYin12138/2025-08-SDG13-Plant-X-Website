<script setup>
import ThemeToggle from './components/ThemeToggle.vue'
</script>

<template>
  <header
    class="section"
    style="padding:.75rem 0;border-bottom:1px solid color-mix(in oklab, var(--fg) 10%, transparent);position:sticky;top:0;background:var(--bg);z-index:50;"
  >
    <div
      class="container"
      style="display:flex;align-items:center;gap:.75rem;margin:0 auto;max-width:1300px;"
    >
      <RouterLink to="/" aria-label="Plant'X Home">
        <img src="@/assets/logo.svg" alt="Plant'X Logo" />
      </RouterLink>
      <RouterLink to="/" style="font-weight:800;">Plant'X</RouterLink>

      <nav style="margin-left:auto;display:flex;gap:.99rem;font-size:larger;">
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/garden">Garden</RouterLink>
        <RouterLink to="/urbanwild">Urban & Wild</RouterLink>
        <RouterLink to="/community">Community</RouterLink>
      </nav>

      <ThemeToggle />
    </div>
  </header>

  <main class="container" style="padding:1.25rem 1rem;">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <!-- ✅ 统一包一层元素，保证可动画的是“单一元素根节点” -->
        <div class="route-shell" :key="route.fullPath">
          <component :is="Component" />
        </div>
      </Transition>
    </RouterView>
  </main>

  <footer
    class="section"
    style="border-top:1px solid color-mix(in oklab, var(--fg) 10%, transparent);color:var(--muted);"
  >
    <div class="container">© {{ new Date().getFullYear() }} Plant'X</div>
  </footer>
</template>

<style scoped>
/* 过渡动画（可按需调整时长/缓动） */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

/* 让 shell 作为路由页的单一根节点容器 */
.route-shell {
  display: block;
}

/* 可选：为当前激活的路由添加下划线/高亮（如果使用了 RouterLink 的 active-class 可移除） */
a.router-link-active {
  text-decoration: underline;
}
</style>
