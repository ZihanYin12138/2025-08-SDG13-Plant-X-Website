<script setup>
import { ref } from 'vue'
const email = ref('')
const name = ref('')
const onSubmit = () => {
// Placeholder — here you would POST to your API with CSRF and validation
alert(`Welcome, ${name.value}! Check your inbox at ${email.value}.`)
}
</script>

<template>
<section class="section">
<div class="container">
<h2 class="title">Community</h2>
<p class="lead">Join gardening enthusiasts to share experiences and collaborate on climate-positive actions.</p>



</div>
</section>
</template>

<style scoped>
form.card{display:grid;gap:.75rem}
input{width:100%;padding:.7rem 1rem;border-radius:12px;border:1px solid color-mix(in oklab, var(--fg) 15%, transparent);background:var(--surface);color:var(--fg)}
input:focus{outline:2px solid var(--ring);outline-offset:2px}
.small{font-size:.9rem}
</style>