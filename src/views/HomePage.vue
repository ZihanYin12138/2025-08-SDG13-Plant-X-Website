<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { searchPlants, type Plant } from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/PlantCardSkeleton.vue'

const plants = ref<Plant[]>([])
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await searchPlants('')
    plants.value = res.items.slice(0,8)
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>


<template>
  <!-- HERO / INTRO -->
  <section class="section container hero-home">
    <div class="hero-grid">
      <div>
        <h1 class="display">Plant'X</h1>
        <h2 class="title">Keep Your Garden Thriving Under Changing Climate</h2>
        <p class="lead">
          Caring for personal plants is more than just a hobby. With the right attention to sunlight, soil, watering,
          and composting, a home garden can thrive, bringing health and joy to daily life. From balconies and city parks
          to wild landscapes, plants connect us to the environment. Urban greenery helps build climate resilience, while
          wild plants protect biodiversity—together, they remind us that caring for our own garden is also caring for
          the planet.
        </p>
        <div class="hero-cta">
          <RouterLink class="btn btn-primary" to="/garden">Explore</RouterLink>
        </div>
      </div>
      <div class="img-col">
        <img src="@/assets/home 1.png" />
      </div>
    </div>
  </section>

  <section class="section container">
    <div>
      <img src="@/assets/home 2.png" />
    </div>
  </section>

  <hr class="divider-red" aria-hidden="true" />

  <section class="section container">
    <div class="feature-grid">
      <div>
        <h2 class="title">Supporting Climate Action</h2>
        <p class="lead">
          Based on our project objectives, we help users better understand and respond to the impact of climate change
          on plant growth by providing climate-adaptive planting solutions and environmental data. This platform
          encourages sustainable gardening practices, thereby supporting the achievement of climate action (SDG 13)
          goals.
        </p>
      </div>
      <div class="sdg">
        <img src="@/assets/SDG 13.png" />
      </div>
    </div>
  </section>

  <hr class="divider-red" aria-hidden="true" />

  <!-- Garden / Urban & Wild / Community -->
  <section class="section container">
    <div class="grid cards">
      <article class="card">
        <img src="@/assets/h gps.png" />
        <h3>Garden Plant Support</h3>
        <p>
          Our Garden Plant Support feature offers personalized care guidance to help you easily monitor and maintain the
          health of your plants, tailored to the specific types and environmental conditions in your garden.
        </p>
        <RouterLink class="btn btn-ghost" to="/garden">Learn more →</RouterLink>
      </article>
      <article class="card">
        <img src="@/assets/h U&W.png" />
        <h3>Explore Urban & Wild Forest</h3>
        <p>
          The "Explore Urban & Wild Forest feature helps users discover native plant species and their ecological roles
          in urban and forest environments, aiding in better garden plant choices.
        </p>
        <!-- <RouterLink class="btn btn-ghost" to="/urbanwild">Learn more →</RouterLink> -->
      </article>
      <article class="card">
        <img src="@/assets/h jc.png" />
        <h3>Join Community Activity</h3>
        <p>
          The "Join Community Activity feature connects gardening enthusiasts to share experiences, collaborate, and
          gain inspiration and support from a broader community.
        </p>
        <!-- <RouterLink class="btn btn-ghost" to="/community">Learn more →</RouterLink> -->
      </article>
    </div>
  </section>

  <hr class="divider-red" aria-hidden="true" />

  <!-- 首页推荐植物 -->
  <section id="plants" class="section container">
    <h2 class="title">We Have Tons Of Plants Data</h2>
    <div class="seeall">
      <RouterLink class="btn btn-ghost" to="/garden">See all</RouterLink>
    </div>

    <div class="plants-grid">
      <template v-if="loading">
        <PlantCardSkeleton v-for="n in 8" :key="'s' + n" />
      </template>

      <p v-else-if="error" class="error">加载失败：{{ error }}</p>

      <PlantCard v-else v-for="p in plants" :key="p.general_plant_id" :plant="p" />
    </div>
  </section>

  <hr class="divider-red" aria-hidden="true" />

  <section>
    <div class="center">
    <RouterLink class="btn btn-ghost" to="/learnmore">Learn More</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.hero-home .hero-grid {
  display: grid;
  gap: 1.25rem;
  align-items: center;
  grid-template-columns: 1.15fr 0.85fr;
}
@media (max-width: 1000px) {
  .hero-home .hero-grid {
    grid-template-columns: 1fr;
  }
}
.img-col {
  display: grid;
  place-items: center;
}
.img-placeholder {
  width: 100%;
  aspect-ratio: 16/10;
  border: 2px dashed color-mix(in oklab, var(--fg) 25%, transparent);
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: var(--muted);
}
.img-placeholder.small {
  aspect-ratio: 4/3;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.badge {
  border: 1px solid color-mix(in oklab, var(--fg) 20%, transparent);
  padding: 0.35rem 0.6rem;
  border-radius: 999px;
  font-size: 0.9rem;
}

.feature-grid {
  display: grid;
  gap: 1.25rem;
  align-items: start;
  grid-template-columns: 1.1fr 0.9fr;
}
@media (max-width: 900px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
.stats {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}
.stat {
  background: var(--card);
  box-shadow: var(--shadow);
  border-radius: 12px;
  padding: 0.8rem 1rem;
  display: grid;
}
.stat strong {
  font-size: 1.25rem;
}
.stat span {
  color: var(--muted);
  font-size: 0.9rem;
}

.callout {
  display: flex;
  gap: 1rem;
  align-items: end;
  justify-content: space-between;
}
.seeall {
  white-space: nowrap;
}

.plants-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 768px) {
  .plants-grid {
    grid-template-columns: repeat(2, 1fr); /* 平板及以下一行2个 */
  }
}

@media (max-width: 480px) {
  .plants-grid {
    grid-template-columns: 1fr; /* 手机上一行1个 */
  }
}

.plant {
  background: var(--card);
  box-shadow: var(--shadow);
  border-radius: 14px;
  padding: 0.8rem;
}
.plant .thumb {
  aspect-ratio: 4/3;
  border-radius: 10px;
  border: 2px dashed color-mix(in oklab, var(--fg) 25%, transparent);
  margin-bottom: 0.5rem;
}
.plant h4 {
  margin: 0.25rem 0;
}
.plant .latin {
  color: var(--muted);
  font-size: 0.9rem;
}

.divider-red {
  border: 0;
  height: 3px;
  background: linear-gradient(90deg, #ff3b3b, #ff9a3b);
  margin: 0;
}

.center {
  display: flex;
  justify-content: center; 
  align-items: center;     
  height: 90px;          
}

.sdg{
  height: 300px;
  width: 300px;
  margin-left: auto;
}

.display{
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 0 0 .4rem;
  font-size: clamp(2.6rem, 1.6rem + 5vw, 4.25rem); /* 手机~大屏逐级放大 */
  color: var(--fg);
}

/* 仅在首页 hero 里，副标题稍小一些（不影响全局 .title 的其他用法） */
.hero-home .title{
  margin: 0 0 .6rem;
  font-size: clamp(1.4rem, 1rem + 2.2vw, 2.1rem);
}

/* 可选：导语与按钮的间距微调，让层级更清晰 */
.hero-home .lead{ margin-top: .25rem; color: var(--muted); }
.hero-home .hero-cta{ margin-top: .75rem; }
</style>
