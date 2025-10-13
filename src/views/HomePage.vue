<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { searchPlants, type PlantCardItem } from '@/api/plants'
import PlantCard from '@/components/PlantCard.vue'
import PlantCardSkeleton from '@/components/CardSkeleton.vue'

/* =================== Plants list (homepage cards) =================== */
const plants = ref<PlantCardItem[]>([])
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await searchPlants('')
    plants.value = res.items.slice(0, 8)
  } catch (e: any) {
    error.value = e.message || String(e)
  } finally {
    loading.value = false
  }
}
onMounted(load)

/* =================== Articles：横幅轮播（循环 + 动画） =================== */
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
      title: 'Plants are suffering from excessive heat',
      href: 'https://www.sbs.com.au/news/article/nearly-half-of-australias-native-plants-are-under-threat-from-climate-change/eotnh8c3f',
      desc: `47% of Australia's native plant species may face challenges by 2070 as temperatures rise.
      Plants that have survived in stable conditions for thousands of years are now at risk of dying because they cannot tolerate the extreme heat.`,
      bg: lm11,
    },
    {
      title: 'Rainfall patterns are changing',
      href: 'https://www.nespthreatenedspecies.edu.au/news-and-media/latest-news/race-to-unlock-secret-to-save-endangered-orchids',
      desc: `Unpredictable rainfall disrupts natural cycles that provide water to plants.
      Many species are under stress and struggling to adapt to conditions very different from what they are accustomed to.`,
      bg: lm12,
    },
    {
      title: 'Species can be wiped out by one bad storm',
      href: 'https://theconversation.com/the-50-beautiful-australian-plants-at-greatest-risk-of-extinction-and-how-to-save-them-160362',
      desc: `A single severe storm can destroy an entire species.
      Approximately 33 threatened species exist in just one location, so a bushfire or a big storm could end their existence.`,
      bg: lm13,
    },
    {
      title: 'Plant partnerships that took millions of years are crumbling',
      href: '',
      desc: `Many orchids rely on fungi in their roots to survive.
      Climate change is disrupting these vital relationships, threatening species that have evolved over millions of years.`,
      bg: lm14,
    },
    {
      title: 'Plants do not receive fire when they need it',
      href: 'https://theconversation.com/australia-first-research-reveals-staggering-loss-of-threatened-plants-over-20-years-151408',
      desc: `Fire is essential for seed germination in many Australian plants.
      However, altered fire patterns now prevent reproduction, leaving some species unable to regenerate.`,
      bg: lm15,
    },
  ],
  g2: [
    {
      title: 'Turn Your Backyard Into a Wildlife Highway',
      href: 'https://conservationvolunteers.com.au/australias-endangered-plants-and-animals-creating-nature-blocks-to-save-them/',
      desc: `Planting native species can transform suburban gardens into vital habitats, linking fragmented landscapes.
      This creates safe corridors for wildlife to move between natural areas.`,
      bg: lm21,
    },
    {
      title: 'Provide food and shelter for wildlife',
      href: 'https://www.gardeningaustraliamag.com.au/growing-australian-native-plants/',
      desc: `Native plants such as banksias, grevilleas, and bottlebrush supply essential food for bees, birds, and small mammals.
      Gardens offer safe shelter and passageways, helping endangered species survive and move between fragmented environments.`,
      bg: lm22,
    },
    {
      title: 'Seeds and Genetic Diversity Matter',
      href: 'https://www.rbg.vic.gov.au/science/research/orchid-conservation-program/',
      desc: `Growing a variety of native plants preserves genetic diversity, which is critical for species survival.
      Your garden becomes a valuable seed bank, strengthening resilience in wild populations.`,
      bg: lm23,
    },
    {
      title: 'Native gardens support pollinators',
      href: 'https://wwf.org.au/blogs/9-australian-native-plants-and-trees-to-attract-wildlife-and-bees-to-your-apartment-balcony-or-garden/',
      desc: `Native plants sustain vital relationships with pollinators like bees and birds,
      ensuring ecological interactions that are essential for reproduction and biodiversity.`,
      bg: lm24,
    },
    {
      title: 'Plants help climate change adaption',
      href: 'https://www.sbs.com.au/news/article/nearly-half-of-australias-native-plants-are-under-threat-from-climate-change/eotnh8c3f',
      desc: `Cultivating endangered species in different environments helps them adapt to changing conditions,
      enabling resilience as climate zones shift.`,
      bg: lm25,
    },
  ],
  g3: [
    {
      title: 'Eastern Suburbs Banksia - Tough as Nails',
      href: 'https://conservationvolunteers.com.au/australias-endangered-plants-and-animals-creating-nature-blocks-to-save-them/',
      desc: `This hardy shrub supports Yellow-tailed Black Cockatoos and connects fragmented habitats across Sydney.
      It’s also beginner-friendly, making it a great choice for new gardeners.`,
      bg: lm31,
    },
    {
      title: 'Native Orchids - Easier to Grow Than You Might Expect',
      href: 'https://gardeningwithangus.com.au/australian-native-orchids/',
      desc: `Many Australian orchids thrive in gardens with shaded areas.
      Growing them helps conserve species that are at risk in the wild.`,
      bg: lm32,
    },
    {
      title: "Local Grevilleas: Nature's Hardy Survivors",
      href: 'https://theconversation.com/australia-first-research-reveals-staggering-loss-of-threatened-plants-over-20-years-151408',
      desc: `Grevilleas have adapted to harsh conditions for millions of years.
      Planting region-specific grevilleas supports pollinators and ensures resilience to climate change.`,
      bg: lm33,
    },
    {
      title: 'Bottlebrush - The Crowd Favorite',
      href: 'https://wwf.org.au/blogs/9-australian-native-plants-and-trees-to-attract-wildlife-and-bees-to-your-apartment-balcony-or-garden/',
      desc: `Vibrant red blooms attract birds and pollinators while strengthening ecosystems.
      Bottlebrushes are both beautiful and functional in any garden.`,
      bg: lm34,
    },
    {
      title: 'Native Grasses - Set and Forget',
      href: 'https://www.nespthreatenedspecies.edu.au/news-and-media/latest-news/race-to-unlock-secret-to-save-endangered-orchids',
      desc: `Once established, native grasses require little care but provide lasting habitat for wildlife,
      supporting biodiversity with minimal effort.`,
      bg: lm35,
    },
  ],
}

const tabMeta: Record<GroupKey, { title: string; subtitle: string }> = {
  g1: { title: 'How Climate change threatens on Australian Plants', subtitle: 'Impacts on native plants & ecosystems' },
  g2: { title: 'How Your Garden Support Nature In a Changing Climate', subtitle: 'How your garden helps nature' },
  g3: { title: 'Grow to protect: native plants you can save in your garden', subtitle: 'Starter-friendly native plant ideas' },
}

/* ===== "Middle Plate" is selected by default ===== */
const activeGroup = ref<GroupKey>('g2')
const activeIndex = ref(0)

const items = computed(() => groups[activeGroup.value] || [])
const len = computed(() => items.value.length)
const currentItem = computed(() => items.value[activeIndex.value])

const prevIdx = computed(() => (activeIndex.value - 1 + len.value) % len.value)
const nextIdx = computed(() => (activeIndex.value + 1) % len.value)
const prevItem = computed(() => items.value[prevIdx.value])
const nextItem = computed(() => items.value[nextIdx.value])

const animName = ref<'slide-next' | 'slide-prev'>('slide-next')

function switchGroup(g: GroupKey) {
  if (activeGroup.value === g) return
  activeGroup.value = g
  activeIndex.value = 0
  animName.value = 'slide-next'
}
function go(step: number) {
  if (!len.value) return
  animName.value = step > 0 ? 'slide-next' : 'slide-prev'
  activeIndex.value = (activeIndex.value + step + len.value) % len.value
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') go(1)
  if (e.key === 'ArrowLeft') go(-1)
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))

let touchStartX = 0
function onTouchStart(e: TouchEvent) { touchStartX = e.changedTouches[0].clientX }
function onTouchEnd(e: TouchEvent) {
  const dx = e.changedTouches[0].clientX - touchStartX
  if (Math.abs(dx) > 40) { dx < 0 ? go(1) : go(-1) }
}
</script>

<template>
  <section class="section container hero-home">
    <div class="hero-grid">
      <div>
        <h1 class="display">Plant'X</h1>
        <h2 class="title">Keep Your Garden Thriving Under Changing Climate in Australia</h2>
        <p class="lead">
          Caring for plants is more than a hobby. With proper sunlight, soil, water, and compost, gardens thrive and bring joy.
          From city balconies to wild landscapes, plants connect us to nature—urban greenery builds resilience,
          and wild plants preserve biodiversity. Tending our gardens means caring for the planet.
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
              Our Garden Support feature provides personalized guidance to help you monitor & maintain plant health based on your garden’s specific conditions.
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
              The Explore feature of Urban & Wild Forest helps users discover native plants and their ecological roles, guiding better garden choices.
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
              The Join Community Activity feature connects gardeners to share experiences, collaborate on projects, and find inspiration and support.
            </p>
          </div>
        </article>
      </RouterLink>
    </div>
  </section>

  <hr class="divider-red" aria-hidden="true" />

  <!-- Homepage recommended plants -->
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

  <!-- Index + Articles -->
  <section class="section container">
    <h2 class="title">More About Our Goal and Vision</h2>

    <div class="container">
      <h2>🌱 Victoria Plants Index (1985–2021)</h2>
      <div class="plantindex">
        <img src="@/assets/mainindex.jpg" class="miimg" />
        <p class="mitext">
          This chart shows that threatened plants in Victoria have declined by over 70% since 1985.
          Climate change, droughts, and habitat loss are major pressures. By choosing native, climate-resilient plants and gardening ecologically,
          home gardeners can help support biodiversity.
        </p>
      </div>
    </div>

    <div class="articles-block">
      <h3 class="article-heading">Articles</h3>

      <!-- Tabs with background highlight -->
      <div class="story-header">
        <div class="tabs" role="tablist" aria-label="Article groups">
          <button
            v-for="(meta, key) in tabMeta"
            :key="key"
            role="tab"
            :aria-selected="activeGroup === key"
            :class="['tab', { active: activeGroup === key }]"
            @click="switchGroup(key as GroupKey)"
          >
            <strong class="tab-title">{{ meta.title }}</strong>
            <span class="tab-subtitle">{{ meta.subtitle }}</span>
          </button>
        </div>
      </div>

      <!-- Dots -->
      <div class="story-dots" aria-label="Article pagination">
        <button
          v-for="(_it, i) in items"
          :key="i"
          :aria-current="i === activeIndex"
          @click="activeIndex = i; animName = 'slide-next'"
        />
      </div>

      <!-- Banner stage -->
      <div class="story-stage" :class="animName" role="region" aria-label="Article slider"
           @keydown.passive="onKey" @touchstart.passive="onTouchStart" @touchend.passive="onTouchEnd" tabindex="0">

        <div class="side-peek side-peek--left"
             :style="{ backgroundImage: `linear-gradient(90deg, rgba(0,0,0,.45), rgba(0,0,0,0)), url(${prevItem?.bg})` }"
             @click="go(-1)" aria-label="Show previous">
          <span class="chevron">‹</span>
        </div>
        <div class="side-peek side-peek--right"
             :style="{ backgroundImage: `linear-gradient(270deg, rgba(0,0,0,.45), rgba(0,0,0,0)), url(${nextItem?.bg})` }"
             @click="go(1)" aria-label="Show next">
          <span class="chevron">›</span>
        </div>

        <div class="stage-card">
          <Transition :name="animName" mode="out-in">
            <div class="stage-layer"
                 :key="activeIndex"
                 :style="{
                   backgroundImage: currentItem?.bg
                     ? `linear-gradient(180deg, rgba(0,0,0,.10), rgba(0,0,0,.68)), url(${currentItem.bg})`
                     : `linear-gradient(180deg, rgba(0,0,0,.10), rgba(0,0,0,.68))`
                 }">
              <div class="stage-content" aria-live="polite">
                <p class="stage-eyebrow">{{ tabMeta[activeGroup].subtitle }}</p>
                <h3 class="stage-title">
                  <a v-if="currentItem?.href" :href="currentItem.href" target="_blank" rel="noopener">
                    {{ currentItem?.title }}
                  </a>
                  <template v-else>{{ currentItem?.title }}</template>
                </h3>
                <p class="stage-desc">{{ currentItem?.desc }}</p>
                <div class="stage-cta" v-if="currentItem?.href">
                  <a class="btn btn-primary" :href="currentItem.href" target="_blank" rel="noopener">Read more</a>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ===== Basic layout ===== */
.hero-home .hero-grid {
  display: grid; gap: 1.25rem; align-items: center;
  grid-template-columns: 1.15fr 0.85fr;
}
@media (max-width: 1000px) { .hero-home .hero-grid { grid-template-columns: 1fr; } }
.img-col { display: grid; place-items: center; }

.feature-grid { display: grid; gap: 1.25rem; align-items: start; grid-template-columns: 1.1fr 0.9fr; }
@media (max-width: 900px) { .feature-grid { grid-template-columns: 1fr; } }

.plants-grid { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr); }
@media (max-width: 768px) { .plants-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 480px) { .plants-grid { grid-template-columns: 1fr; } }

.infocard { height: 580px; }
.card { transition: transform .3s ease, box-shadow .3s ease; box-shadow: 0 4px 8px rgba(0,0,0,.1); }
.card:hover { transform: translateY(-8px) scale(1.03); box-shadow: 0 12px 24px rgba(0,0,0,.2); }

.divider-red { border: 0; height: 3px; background: linear-gradient(90deg, #ff3b3b, #ff9a3b); margin: 0; }

.sdg { height: 300px; width: 300px; margin-left: auto; }

.display{
  font-weight: 900; line-height: 1.1; letter-spacing: -0.02em;
  margin: 0 0 .4rem; font-size: clamp(2.6rem, 1.6rem + 5vw, 4.25rem); color: var(--fg);
}
.hero-home .title{ margin: 0 0 .6rem; font-size: clamp(1.4rem, 1rem + 2.2vw, 2.1rem); }
.hero-home .lead{ margin-top: .25rem; color: var(--muted); }
.hero-home .hero-cta{ margin-top: .75rem; }

/* ===== Article block spacing & heading ===== */
.articles-block{ margin-top: clamp(18px, 3vw, 32px); }
.article-heading{
  margin: 0 0 .6rem; font-weight: 800; letter-spacing: -.01em;
  font-size: clamp(1.2rem, 1rem + 1.2vw, 1.6rem); color: var(--fg);
}

/* ===== Tabs with background highlight ===== */
.story-header { margin-bottom: .4rem; }
.tabs { display: grid; gap: .5rem; --accent: var(--brand, #0b65c2); }
@media (min-width: 900px) { .tabs { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 899px) { .tabs { grid-template-columns: 1fr; } }

.tab{
  text-align: left;
  background: color-mix(in oklab, var(--card) 90%, #fff 10%);
  color: var(--fg);
  border: 1px solid color-mix(in oklab, var(--fg) 12%, transparent);
  border-radius: 16px; padding: .8rem 1rem; box-shadow: var(--shadow);
  cursor: pointer; transition: transform .18s, box-shadow .18s, border-color .18s, background .18s;
}
.tab:hover{ transform: translateY(-1px); }
.tab.active{
  background: color-mix(in oklab, var(--accent) 18%, var(--card) 82%);
  border-color: color-mix(in oklab, var(--accent) 42%, transparent);
  box-shadow: 0 10px 26px rgba(0,0,0,.10);
}
.tab-title{ display:block; font-weight:750; line-height:1.35; }
.tab-subtitle{ display:block; font-size:.95rem; color: var(--muted); margin-top:.25rem; }

/* ===== Dots ===== */
.story-dots{ display:flex; justify-content:center; gap:8px; margin:.35rem 0 .55rem; }
.story-dots button{
  width:8px; height:8px; border-radius:999px; border:0;
  background: color-mix(in oklab, var(--fg) 35%, transparent);
  cursor:pointer; opacity:.8;
}
.story-dots button[aria-current="true"]{ background: var(--fg); opacity:1; }

/* ===== Stage (wider center, narrow gaps) ===== */
.story-stage{
  --peek: clamp(44px, 9.5vw, 140px);
  --gap: clamp(6px, .9vw, 10px);
  --stage-h: clamp(340px, 42vw, 600px);
  position: relative; height: var(--stage-h);
  border-radius: 22px; overflow: hidden; outline: none;
}

/* Side previews */
.side-peek{
  position:absolute; top:0; bottom:0; width:var(--peek);
  background-size:cover; background-position:center; background-repeat:no-repeat;
  border-radius:18px; overflow:hidden; cursor:pointer; z-index:2;
  filter: blur(1px) brightness(.85) saturate(.92);
  box-shadow:0 12px 28px rgba(0,0,0,.18) inset;
  transition: transform .42s cubic-bezier(.22,.61,.36,1), opacity .3s ease, filter .3s ease;
}
.side-peek--left{ left:var(--gap); }
.side-peek--right{ right:var(--gap); }
.side-peek:hover{ filter: blur(.5px) brightness(.92); }

/* Arrows (no circle bg) */
.chevron{
  position:absolute; top:50%; transform:translateY(-50%);
  font-size: 40px; font-weight: 800; line-height: 1;
  color:#fff; text-shadow: 0 3px 10px rgba(0,0,0,.6);
  pointer-events: none;
}
.side-peek--left .chevron{ left: 6px; }
.side-peek--right .chevron{ right: 6px; }

/* Main card */
.stage-card{
  position:absolute; inset:0;
  left:calc(var(--peek) + 1.5 * var(--gap));
  right:calc(var(--peek) + 1.5 * var(--gap));
  border-radius:20px; overflow:hidden; z-index:3;
  box-shadow:0 18px 44px rgba(0,0,0,.28);
}
.stage-layer{ position:absolute; inset:0; background-size:cover; background-position:center; }
.stage-card::after{
  content:''; position:absolute; inset:0; pointer-events:none;
  background:linear-gradient(90deg, rgba(0,0,0,.3), transparent 20%, transparent 80%, rgba(0,0,0,.3));
}
.stage-content{
  position:absolute; left:clamp(16px, 3.6vw, 42px); right:clamp(16px, 3.6vw, 42px);
  bottom:clamp(16px, 3.2vw, 36px); color:#fff; text-shadow:0 2px 10px rgba(0,0,0,.35);
  max-width:1100px; z-index:1;
}
.stage-eyebrow{ margin:0 0 .25rem; opacity:.95; font-weight:500; }
.stage-title{ margin:0 0 .5rem; font-weight:800; letter-spacing:-0.01em; font-size:clamp(1.5rem, 1rem + 2.7vw, 2.65rem); }
.stage-title a{ color:inherit; text-decoration:none; } .stage-title a:hover{ text-decoration:underline; }
.stage-desc{ margin:0 0 .8rem; opacity:.98; line-height:1.6; font-size:clamp(.95rem, .8rem + .4vw, 1.05rem); }

/* Transitions */
.slide-next-enter-active,
.slide-next-leave-active,
.slide-prev-enter-active,
.slide-prev-leave-active{
  transition: transform .42s cubic-bezier(.22,.61,.36,1), opacity .42s ease;
}
.slide-next-enter-from{ opacity:0; transform: translateX(24px); }
.slide-next-leave-to{ opacity:0; transform: translateX(-24px); }
.slide-prev-enter-from{ opacity:0; transform: translateX(-24px); }
.slide-prev-leave-to{ opacity:0; transform: translateX(24px); }
.story-stage.slide-next .side-peek--left{ transform: translateX(-6px); }
.story-stage.slide-next .side-peek--right{ transform: translateX(-2px); }
.story-stage.slide-prev .side-peek--right{ transform: translateX(6px); }
.story-stage.slide-prev .side-peek--left{ transform: translateX(2px); }

/* Index block */
.plantindex{ display:flex; flex-direction:row; gap:20px; text-align:justify; }
.miimg{ max-width:55%; max-height:55%; border-radius:12px; display:block; }
.mitext{ margin-top:70px; font-size:large; }
</style>
