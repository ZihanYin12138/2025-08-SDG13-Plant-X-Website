<script setup>

</script>


<template>
  <!-- HERO / INTRO -->
  <section class="section container hero-home">
    <div class="hero-grid">
      <div>
        <h1 class="title">Keep your garden thriving under changing climate</h1>
        <p class="lead">
          Caring for personal plants is more than just a hobby. With the right attention to sunlight, soil, watering, and composting, a home garden can thrive, 
          bringing health and joy to daily life. From balconies and city parks to wild landscapes, plants connect us to the environment. 
          Urban greenery helps build climate resilience, while wild plants protect biodiversity—together, 
          they remind us that caring for our own garden is also caring for the planet.
        </p>
        <div class="hero-cta">
          <RouterLink class="btn btn-primary" to="/Garden">Explore</RouterLink>
        </div>
      </div>
      <div class="img-col">
        <div class="img-placeholder" aria-label="Hero image placeholder">Add image here</div>
      </div>
    </div>
  </section>

  
  <hr class="divider-red" aria-hidden="true" />

  <!--  
  <section class="section container">
    <div class="badge-row">
      <span class="badge">Planty'X Plant Knowledge</span>
      <span class="badge">Climate Resources</span>
      <span class="badge">Resources for SDG13</span>
    </div>
  </section> -->

  <!--  -->
  <section class="section container">
    <div class="feature-grid">
      <div>
        <h2 class="title">Supporting climate action</h2>
        <p class="lead">
            Based on our project objectives, we help users better understand and respond to the impact of climate change on plant growth by providing climate-adaptive planting solutions and environmental data. 
            This platform encourages sustainable gardening practices, thereby supporting the achievement of climate action (SDG 13) goals.
        </p>
        <!--
        <div class="stats">
          <div class="stat"><strong>100</strong><span>Species entries</span></div>
          <div class="stat"><strong>00</strong><span>Tips & practices</span></div>
          <div class="stat"><strong>SDG 13</strong><span>Climate action</span></div>
        </div>-->

      </div>
      <div class="img-col">
        <div class="img-placeholder" aria-label="Data illustration placeholder">Add image here</div>
      </div>
    </div>
  </section>


  <hr class="divider-red" aria-hidden="true" />

  <!-- Garden / Urban & Wild / Community -->
  <section class="section container">
    <div class="grid cards">
      <article class="card">
        <div class="img-placeholder small" aria-label="Garden feature image placeholder">Image</div>
        <h3>Garden Plant Support</h3>
        <p>
            Our Garden Plant Support feature offers personalized care guidance to help you easily monitor and maintain the health of your plants, 
            tailored to the specific types and environmental conditions in your garden.
        </p>
        <RouterLink class="btn btn-ghost" to="/garden">Learn more →</RouterLink>
      </article>
      <article class="card">
        <div class="img-placeholder small" aria-label="Urban & Wild feature image placeholder">Image</div>
        <h3>Explore Urban & Wild Forest</h3>
        <p>
            The "Explore Urban & Wild Forest feature helps users discover native plant species and their ecological roles in urban and forest environments, 
            aiding in better garden plant choices.
        </p>
        <RouterLink class="btn btn-ghost" to="/urbanwild">Learn more →</RouterLink>
      </article>
      <article class="card">
        <div class="img-placeholder small" aria-label="Community feature image placeholder">Image</div>
        <h3>Join Community Activity</h3>
        <p>
            The "Join Community Activity feature connects gardening enthusiasts to share experiences, 
            collaborate, and gain inspiration and support from a broader community.
        </p>
        <RouterLink class="btn btn-ghost" to="/community">Learn more →</RouterLink>
      </article>
    </div>
  </section>


  <hr class="divider-red" aria-hidden="true" />


  <section class="section container">
    <div class="callout">
      <div>
        <h2 class="title">Supporting climate action</h2>
        <p class="lead">
          Caring for personal plants is more than just a hobby. Urban greenery builds climate resilience, while wild plants protect biodiversity — caring for our own garden is also caring for the planet.
        </p>
      </div>
      
    </div>
  </section>

  
  <hr class="divider-red" aria-hidden="true" />

  <!-- plant list -->
  <section id="plants" class="section container">
    <h2 class="title">We have tons of plants data</h2>
    <div class="seeall">
        <a class="btn btn-ghost" href="#plants">See all</a>
    </div>
    <div class="plants-grid">
      <article class="plant">
        <div class="thumb" aria-label="American Burnweed image placeholder"></div>
        <h4>American Burnweed</h4>
        <p class="latin">Erechtites hieraclifolius</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>Pilea Dark Mystery</h4>
        <p class="latin">Pilea involucrata</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>Phillipine Evergreen</h4>
        <p class="latin">Aglaonema commutatum</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>European Cypress</h4>
        <p class="latin">Cupressus sempervirens</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>Lawyer's Tongue</h4>
        <p class="latin">Gasteria</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>Big Leaf Philodendron</h4>
        <p class="latin">Philodendron maximum</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>Hebe Plant</h4>
        <p class="latin">Hebe andersonii</p>
      </article>
      <article class="plant">
        <div class="thumb"></div>
        <h4>Teddy Bear Vine</h4>
        <p class="latin">Cyanotis beddomei</p>
      </article>
    </div>
  </section>
</template>



<style scoped>
.hero-home .hero-grid{display:grid;gap:1.25rem;align-items:center;grid-template-columns:1.15fr .85fr}
@media(max-width:1000px){.hero-home .hero-grid{grid-template-columns:1fr}}
.img-col{display:grid;place-items:center}
.img-placeholder{width:100%;aspect-ratio:16/10;border:2px dashed color-mix(in oklab, var(--fg) 25%, transparent);border-radius:16px;display:grid;place-items:center;color:var(--muted);}
.img-placeholder.small{aspect-ratio:4/3}

.badge-row{display:flex;flex-wrap:wrap;gap:.5rem}
.badge{border:1px solid color-mix(in oklab, var(--fg) 20%, transparent);padding:.35rem .6rem;border-radius:999px;font-size:.9rem}

.feature-grid{display:grid;gap:1.25rem;align-items:start;grid-template-columns:1.1fr .9fr}
@media(max-width:900px){.feature-grid{grid-template-columns:1fr}}
.stats{display:flex;gap:1rem;flex-wrap:wrap;margin-top:1rem}
.stat{background:var(--card);box-shadow:var(--shadow);border-radius:12px;padding:.8rem 1rem;display:grid}
.stat strong{font-size:1.25rem}
.stat span{color:var(--muted);font-size:.9rem}

.callout{display:flex;gap:1rem;align-items:end;justify-content:space-between}
.seeall{white-space:nowrap}

.plants-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.plant{background:var(--card);box-shadow:var(--shadow);border-radius:14px;padding:.8rem}
.plant .thumb{aspect-ratio:4/3;border-radius:10px;border:2px dashed color-mix(in oklab, var(--fg) 25%, transparent);margin-bottom:.5rem}
.plant h4{margin:.25rem 0}
.plant .latin{color:var(--muted);font-size:.9rem}

.divider-red{border:0;height:3px;background:linear-gradient(90deg,#ff3b3b,#ff9a3b);margin:0}
</style>

