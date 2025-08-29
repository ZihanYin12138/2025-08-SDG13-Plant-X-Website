<script setup>
</script>

<template>
<section class="section">
<div class="container">
<h2 class="title">Garden</h2>
<p class="lead">
    Tools and tips for climate-adaptive home gardening — sunlight, soil, watering, composting, and more.
</p>

<div class="psearch">
    <div class="sbox">
        
        <input type="text" id="myInput" onkeyup="myFunction()" placeholder="Search for plants..">

            <table id="myTable">
            <tr class="header">
                <th> Plant Finder:</th>
                <th >Name</th>
                <th >Country</th>
            </tr>
            <tr>
                <td>Alfreds Futterkiste</td>
                <td>Germany</td>
            </tr>
            <tr>
                <td>Berglunds snabbkop</td>
                <td>Sweden</td>
            </tr>
            <tr>
                <td>Island Trading</td>
                <td>UK</td>
            </tr>
            <tr>
                <td>Koniglich Essen</td>
                <td>Germany</td>
            </tr>
            </table>

    </div>

    <div class="filter">
        
    </div>
    <div class="pcard">
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
    </div>

</div>



</div>
</section>
</template>


<style lang="css" scoped>






.pcard{}

.plants-grid{display:grid;gap:1rem;grid-template-columns:repeat(auto-fit,minmax(180px,1fr))}
.plant{background:var(--card);box-shadow:var(--shadow);border-radius:14px;padding:.8rem}
.plant .thumb{aspect-ratio:4/3;border-radius:10px;border:2px dashed color-mix(in oklab, var(--fg) 25%, transparent);margin-bottom:.5rem}
.plant h4{margin:.25rem 0}
.plant .latin{color:var(--muted);font-size:.9rem}
</style>