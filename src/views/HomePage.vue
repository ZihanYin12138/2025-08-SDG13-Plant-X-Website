<script setup lang="ts">
import { ref, onMounted, computed, watch, onUnmounted } from 'vue'
import { searchPlants, type PlantCardItem } from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'

const plants = ref<PlantCardItem[]>([])
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

// ====== Modal 数据与逻辑（新增） ======
type Article = { title: string; href: string; desc: string; bg?: string }
type GroupKey = 'g1' | 'g2' | 'g3'

const lm11 = new URL('@/assets/lm11.jpg', import.meta.url).href
const lm12 = new URL('@/assets/lm12.jpg', import.meta.url).href
const lm13 = new URL('@/assets/lm13.jpg', import.meta.url).href
const lm14 = new URL('@/assets/lm14.jpg', import.meta.url).href
const lm15 = new URL('@/assets/lm15.jpg', import.meta.url).href

const lm21 = new URL('@/assets/lm21.jpg', import.meta.url).href
const lm22 = new URL('@/assets/lm22.png', import.meta.url).href
const lm23 = new URL('@/assets/lm23.png', import.meta.url).href
const lm24 = new URL('@/assets/lm24.jpg', import.meta.url).href
const lm25 = new URL('@/assets/lm25.jpg', import.meta.url).href

const lm31 = new URL('@/assets/lm31.png', import.meta.url).href
const lm32 = new URL('@/assets/lm32.png', import.meta.url).href
const lm33 = new URL('@/assets/lm33.png', import.meta.url).href
const lm34 = new URL('@/assets/lm34.png', import.meta.url).href
const lm35 = new URL('@/assets/lm35.png', import.meta.url).href

const groups: Record<GroupKey, Article[]> = {
  g1: [
    {
      title: '(i) Plants are suffering from excessive heat',
      href: 'https://www.sbs.com.au/news/article/nearly-half-of-australias-native-plants-are-under-threat-from-climate-change/eotnh8c3f',
      desc: `47% of Australia's native plant species may face challenges by 2070 as temperatures rise.
      Plants that have survived in stable conditions for thousands of years are now at risk of dying because they cannot tolerate the extreme heat.`,
      bg: lm11,
    },
    {
      title: '(ii) Rainfall patterns are changing',
      href: 'https://www.nespthreatenedspecies.edu.au/news-and-media/latest-news/race-to-unlock-secret-to-save-endangered-orchids',
      desc: `Unpredictable rainfall disrupts natural cycles that provide water to plants.
      Many species are under stress and struggling to adapt to conditions very different from what they are accustomed to.`,
      bg: lm12,
    },
    {
      title: '(iii) Species can be wiped out by one bad storm',
      href: 'https://theconversation.com/the-50-beautiful-australian-plants-at-greatest-risk-of-extinction-and-how-to-save-them-160362',
      desc: `A single severe storm can destroy an entire species.
      Approximately 33 threatened species exist in just one location, so a bushfire or a big storm could end their existence.`,
      bg: lm13,
    },
    {
      title: '(iv) Plant partnerships that took millions of years are crumbling',
      href: '',
      desc: `Many orchids rely on fungi in their roots to survive.
      Climate change is disrupting these vital relationships, threatening species that have evolved over millions of years.`,
      bg: lm14,
    },
    {
      title: '(v) Plants do not receive fire when they need it',
      href: 'https://theconversation.com/australia-first-research-reveals-staggering-loss-of-threatened-plants-over-20-years-151408',
      desc: `Fire is essential for seed germination in many Australian plants.
      However, altered fire patterns now prevent reproduction, leaving some species unable to regenerate.`,
      bg: lm15,
    },
  ],
  g2: [
    {
      title: '(i) Turn Your Backyard Into a Wildlife Highway',
      href: 'https://conservationvolunteers.com.au/australias-endangered-plants-and-animals-creating-nature-blocks-to-save-them/',
      desc: `Planting native species can transform suburban gardens into vital habitats, linking fragmented landscapes.
      This creates safe corridors for wildlife to move between natural areas.`,
      bg: lm21,
    },
    {
      title: '(ii) Provide food and shelter for wildlife',
      href: 'https://www.gardeningaustraliamag.com.au/growing-australian-native-plants/',
      desc: `Native plants such as banksias, grevilleas, and bottlebrush supply essential food for bees, birds, and small mammals.
      Gardens offer safe shelter and passageways, helping endangered species survive and move between fragmented environments.`,
      bg: lm22,
    },
    {
      title: '(iii) Seeds and Genetic Diversity Matter',
      href: 'https://www.rbg.vic.gov.au/science/research/orchid-conservation-program/',
      desc: `Growing a variety of native plants preserves genetic diversity, which is critical for species survival.
      Your garden becomes a valuable seed bank, strengthening resilience in wild populations.`,
      bg: lm23,
    },
    {
      title: '(iv) Native gardens support pollinators',
      href: 'https://wwf.org.au/blogs/9-australian-native-plants-and-trees-to-attract-wildlife-and-bees-to-your-apartment-balcony-or-garden/',
      desc: `Native plants sustain vital relationships with pollinators like bees and birds,
      ensuring ecological interactions that are essential for reproduction and biodiversity.`,
      bg: lm24,
    },
    {
      title: '(v) Plants help climate change adaption',
      href: 'https://www.sbs.com.au/news/article/nearly-half-of-australias-native-plants-are-under-threat-from-climate-change/eotnh8c3f',
      desc: `Cultivating endangered species in different environments helps them adapt to changing conditions,
      enabling resilience as climate zones shift.`,
      bg: lm25,
    },
  ],
  g3: [
    {
      title: '(i) Eastern Suburbs Banksia - Tough as Nails',
      href: 'https://conservationvolunteers.com.au/australias-endangered-plants-and-animals-creating-nature-blocks-to-save-them/',
      desc: `This hardy shrub supports Yellow-tailed Black Cockatoos and connects fragmented habitats across Sydney.
      It’s also beginner-friendly, making it a great choice for new gardeners.`,
      bg:lm31,
    },
    {
      title: '(ii) Native Orchids - Easier to Grow Than You Might Expect',
      href: 'https://gardeningwithangus.com.au/australian-native-orchids/',
      desc: `Many Australian orchids thrive in gardens with shaded areas.
      Growing them helps conserve species that are at risk in the wild.`,
      bg:lm32,
    },
    {
      title: "(iii) Local Grevilleas: Nature's Hardy Survivors",
      href: 'https://theconversation.com/australia-first-research-reveals-staggering-loss-of-threatened-plants-over-20-years-151408',
      desc: `Grevilleas have adapted to harsh conditions for millions of years.
      Planting region-specific grevilleas supports pollinators and ensures resilience to climate change.`,
      bg:lm33,
    },
    {
      title: '(iv) Bottlebrush - The Crowd Favorite',
      href: 'https://wwf.org.au/blogs/9-australian-native-plants-and-trees-to-attract-wildlife-and-bees-to-your-apartment-balcony-or-garden/',
      desc: `Vibrant red blooms attract birds and pollinators while strengthening ecosystems.
      Bottlebrushes are both beautiful and functional in any garden.`,
      bg:lm34,
    },
    {
      title: '(v) Native Grasses - Set and Forget',
      href: 'https://www.nespthreatenedspecies.edu.au/news-and-media/latest-news/race-to-unlock-secret-to-save-endangered-orchids',
      desc: `Once established, native grasses require little care but provide lasting habitat for wildlife,
      supporting biodiversity with minimal effort.`,
      bg:lm35,
    },
  ],
}

const modalOpen = ref(false)
const currentGroup = ref<GroupKey | null>(null)
const currentIndex = ref(0)
let wheelLocked = false

const items = computed(() => (currentGroup.value ? groups[currentGroup.value] : []))
const hasPrev = computed(() => currentIndex.value > 0)
const hasNext = computed(() => currentIndex.value < items.value.length - 1)
const currentItem = computed(() => items.value[currentIndex.value])

function openModal(g: GroupKey, start = 0) {
  currentGroup.value = g
  currentIndex.value = start
  modalOpen.value = true
}
function closeModal() {
  modalOpen.value = false
  currentGroup.value = null
  currentIndex.value = 0
}
function go(step: number) {
  const next = Math.min(items.value.length - 1, Math.max(0, currentIndex.value + step))
  if (next !== currentIndex.value) currentIndex.value = next
}
function onWheel(e: WheelEvent) {
  e.preventDefault()
  if (wheelLocked) return
  wheelLocked = true
  const dir = Math.sign(e.deltaY)
  if (dir > 0) go(1)
  else if (dir < 0) go(-1)
  setTimeout(() => (wheelLocked = false), 350)
}
function onKey(e: KeyboardEvent) {
  if (!modalOpen.value) return
  if (e.key === 'Escape') closeModal()
  if (e.key === 'ArrowRight') go(1)
  if (e.key === 'ArrowLeft') go(-1)
}

watch(modalOpen, v => {
  // 锁定滚动
  document.body.style.overflow = v ? 'hidden' : ''
})

onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))

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
      <RouterLink class="infocard" to="/garden">
      <article class="card">
        <img src="@/assets/h gps.png" />
        <h3>Garden Plant Support</h3>
        <div>
        <p>
          Our Garden Plant Support feature offers personalized care guidance to help you easily monitor and maintain the
          health of your plants, tailored to the specific types and environmental conditions in your garden.
        </p>
        </div>
      </article>
      </RouterLink>

      <RouterLink class="infocard" to="/urbanwild">
      <article class="card">
        <img src="@/assets/h U&W.png" />
        <h3>Explore Urban & Wild Forest</h3>
        <div>
        <p>
          The Explore feature of "Urban & Wild Forest" helps users discover native plants and species,
          along with their ecological roles in both urban and forest environments, supporting better garden plant choices.
        </p>
        </div>
      </article>
      </RouterLink>
      <RouterLink class="infocard" to="/community">
      <article class="card">
        <img src="@/assets/h jc.png" />
        <div>
        <h3>Join Community Activity</h3>
        <p>
          With the Join Community Activity feature, gardening enthusiasts can connect, share their experiences,
          collaborate on projects, and find inspiration and support from a vibrant community.
        </p>
        </div>
      </article>
      </RouterLink>
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

      <p v-else-if="error" class="error">Load Failed：{{ error }}</p>

      <PlantCard
        v-else
        v-for="p in plants"
        :key="p.id_type === 'general' ? `g-${p.general_plant_id}` : `t-${p.threatened_plant_id}`"
        :plant="p"
      />
    </div>
  </section>

  <hr class="divider-red" aria-hidden="true" />

  <!-- here -->
  <section class="section container">
    <h2 class="title">More About Our Goal and Vision</h2>

    <div class="card">
      <h2>🌱 Victoria Plants Index (1985–2021)</h2>
      <p>
        This chart shows that threatened plants in Victoria have declined by over 70% since 1985.
        Climate change, droughts, and habitat loss are major pressures. By choosing native, climate-resilient plants and gardening ecologically,
        home gardeners can help support biodiversity.
      </p>
      <div class="plantindex">

      </div>
    </div>

    <!-- 三张入口卡片（点击打开对应组） -->
    <div class="grid cards vertical">
      <div class="card clickable" @click="openModal('g1')">
        <h2 class="card__title">How Your Garden Support Nature In a Changing Climate</h2>
        <p class="muted">Impacts on native plants & ecosystems</p>
      </div>

      <div class="card clickable" @click="openModal('g2')">
        <h2 class="card__title">How Your Garden Support Nature In a Changing Climate</h2>
        <p class="muted">How your garden helps nature</p>
      </div>

      <div class="card clickable" @click="openModal('g3')">
        <h2 class="card__title">Grow to protect: native plants you can save in your garden</h2>
        <p class="muted">Starter-friendly native plant ideas</p>
      </div>
    </div>
  </section>

  <!-- 弹窗 -->
  <teleport to="body">
    <div
      class="modal"
      v-show="modalOpen"
      aria-hidden="false"
      role="dialog"
      aria-modal="true"
    >
      <div class="modal__overlay" @click="closeModal"></div>

      <div class="modal__panel" @wheel.passive.prevent="onWheel">
        <button class="modal__close" aria-label="Close" @click="closeModal">×</button>

        <!-- 背景层 -->
        <div
          class="slide"
          :style="{
            backgroundImage: currentItem?.bg
              ? `linear-gradient(180deg, rgba(0,0,0,.35), rgba(0,0,0,.55)), url(${currentItem.bg})`
              : `linear-gradient(180deg, rgba(0,0,0,.35), rgba(0,0,0,.55))`
          }"
        >
          <div class="article-wrap">
            <article class="modal-article">
              <h1>
                <a
                  v-if="currentItem?.href"
                  :href="currentItem.href"
                  target="_blank"
                  rel="noopener"
                >{{ currentItem?.title }}</a>
                <template v-else>{{ currentItem?.title }}</template>
              </h1>
              <p>{{ currentItem?.desc }}</p>
            </article>
          </div>
        </div>

        <!-- 底部分页器 -->
        <div class="pager pager--left">
          <button class="pager__btn" :disabled="!hasPrev" @click="go(-1)">↑ Prev</button>
          <div class="pager__dots">
            <button
              v-for="(it, i) in items"
              :key="i"
              :aria-current="i === currentIndex"
              @click="currentIndex = i"
            />
          </div>
          <button class="pager__btn" :disabled="!hasNext" @click="go(1)">↓ Next</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
/* =================== 基础布局 =================== */
.hero-home .hero-grid {
  display: grid;
  gap: 1.25rem;
  align-items: center;
  grid-template-columns: 1.15fr 0.85fr;
}
@media (max-width: 1000px) {
  .hero-home .hero-grid { grid-template-columns: 1fr; }
}
.img-col { display: grid; place-items: center; }
.img-placeholder {
  width: 100%;
  aspect-ratio: 16/10;
  border: 2px dashed color-mix(in oklab, var(--fg) 25%, transparent);
  border-radius: 16px;
  display: grid;
  place-items: center;
  color: var(--muted);
}
.img-placeholder.small { aspect-ratio: 4/3; }

.badge-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }
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
  .feature-grid { grid-template-columns: 1fr; }
}

.stats { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: 1rem; }
.stat {
  background: var(--card);
  box-shadow: var(--shadow);
  border-radius: 12px;
  padding: 0.8rem 1rem;
  display: grid;
}
.stat strong { font-size: 1.25rem; }
.stat span { color: var(--muted); font-size: 0.9rem; }

.callout {
  display: flex;
  gap: 1rem;
  align-items: end;
  justify-content: space-between;
}
.seeall { white-space: nowrap; }

/* =================== 列表 / 网格 =================== */
.plants-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 768px) {
  .plants-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .plants-grid { grid-template-columns: 1fr; }
}

.infocard { height: 580px; }

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
.plant h4 { margin: 0.25rem 0; }
.plant .latin { color: var(--muted); font-size: 0.9rem; }

.divider-red {
  border: 0;
  height: 3px;
  background: linear-gradient(90deg, #ff3b3b, #ff9a3b);
  margin: 0;
}

.center { display: flex; justify-content: center; align-items: center; height: 90px; }

.sdg { height: 300px; width: 300px; margin-left: auto; }

.display{
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -0.02em;
  margin: 0 0 .4rem;
  font-size: clamp(2.6rem, 1.6rem + 5vw, 4.25rem);
  color: var(--fg);
}
.hero-home .title{
  margin: 0 0 .6rem;
  font-size: clamp(1.4rem, 1rem + 2.2vw, 2.1rem);
}
.hero-home .lead{ margin-top: .25rem; color: var(--muted); }
.hero-home .hero-cta{ margin-top: .75rem; }

/* =================== 卡片悬浮 =================== */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.card:hover {
  transform: translateY(-8px) scale(1.03);
  box-shadow: 0 12px 24px rgba(0,0,0,0.2);
}

/* =================== here 区域：竖排入口卡片 =================== */
.cards.vertical {
  display: grid;
  grid-template-columns: 1fr;   /* 单列 */
  gap: 1rem;
}
.cards.vertical .card {
  width: 100%;
  background: var(--card);
  color: var(--fg);
  box-shadow: var(--shadow);
}
.muted { color: var(--muted); }
.clickable { cursor: pointer; }

/* =================== 弹窗（主题友好） =================== */
.modal {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
}
.modal__overlay {
  position: absolute;
  inset: 0;
  background: color-mix(in oklab, #000 55%, transparent);
}
.modal__panel {
  position: relative;
  width: min(980px, 96vw);
  height: min(88vh, 900px);
  margin: auto;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow);
  background: var(--card);
  display: grid;
  grid-template-rows: 1fr auto;   /* 默认底部一行给翻页 */
}
/* 使用左侧竖排翻页时，去掉底部行 */
.modal__panel.with-left-rail { grid-template-rows: 1fr; }

.modal__close {
  position: absolute;
  top: 10px; right: 12px;
  z-index: 3;
  font-size: 28px;
  width: 40px; height: 40px;
  border-radius: 999px;
  border: none;
  background: color-mix(in oklab, var(--card) 85%, #fff 15%);
  color: var(--fg);
  cursor: pointer;
  box-shadow: var(--shadow);
}
.modal__close:hover { background: color-mix(in oklab, var(--card) 75%, #fff 25%); }

/* 背景图层（带渐变） */
.slide {
  position: relative;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.article-wrap {
  position: relative;
  z-index: 1;
  height: 100%;
  display: grid;
  place-items: center;           /* 居中显示内容 */
  padding: 2rem;
}

/* 文章卡片 */
.modal-article {
  background: color-mix(in oklab, var(--card) 90%, #fff 10%);
  color: var(--fg);
  border-radius: 14px;
  padding: 1.1rem 1.25rem;
  max-width: 820px;
  margin: 0 auto;                /* 居中 */
  box-shadow: var(--shadow);
}
.modal-article h1 {
  margin: 0 0 .5rem;
  font-size: clamp(1.15rem, 1rem + .6vw, 1.45rem);
}
.modal-article p { margin: 0; line-height: 1.55; }
.modal-article a { color: color-mix(in oklab, var(--fg) 80%, #0b65c2 20%); }

/* =================== 翻页（底部横排，作小屏回退用） =================== */
.pager {
  width: 100%;
  max-height: fit-content;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: .75rem;
  padding: .75rem 1rem 1rem;
}
.pager__btn{
  border: 0; border-radius: 999px; padding: .5rem .9rem;
  background: color-mix(in oklab, var(--card) 88%, #fff 12%);
  color: var(--fg);
  cursor: pointer;
  box-shadow: var(--shadow);
}
.pager__btn:disabled { opacity: .5; cursor: not-allowed; }
.pager__btn:hover:not(:disabled){ background: color-mix(in oklab, var(--card) 78%, #fff 22%); }

.pager__dots { display: flex; gap: .4rem; }
.pager__dots button{
  width: 10px; height: 10px; border-radius: 999px; border: 0;
  background: color-mix(in oklab, var(--fg) 25%, transparent);
  cursor: pointer;
}
.pager__dots button[aria-current="true"]{ background: var(--fg); }

/* =================== 左侧竖排翻页区 =================== */
.pager.pager--left{
  position: absolute;
  left: 5px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;      /* 竖排 */
  align-items: center;
  gap: 50px;
  z-index: 3;
  padding: .25rem;
  width: auto;                 /* 覆盖底部横排的 100% */
  background: transparent;
}
.pager--left .pager__dots{
  display: flex;
  flex-direction: column;      /* 竖排圆点 */
  gap: 50px;
}
/* 内容区域给左侧轨让出空间 */
.with-left-rail .article-wrap{ padding-left: 5.5rem; }

/* 小屏回退为底部横排 */
@media (max-width: 640px){
  .modal__panel.with-left-rail { grid-template-rows: 1fr auto; }
  .with-left-rail .article-wrap{ padding-left: 2rem; }
  .pager.pager--left{
    position: static;
    transform: none;
    flex-direction: row;
    justify-content: center;
    width: 100%;
    padding: .75rem 1rem 1rem;
  }
  .pager--left .pager__dots{ flex-direction: row; }
}
</style>
