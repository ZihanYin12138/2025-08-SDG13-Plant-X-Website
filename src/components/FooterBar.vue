<script setup></script>

<template>
<footer class="footer">
<div class="container grid" style="grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:1.25rem">
<div>
<strong>Plant'X</strong>
<p class="small">Climate-adaptive planting resources and community.</p>
</div>
<div>
<strong>Explore</strong>
<ul>
<li><RouterLink to="/garden">Garden</RouterLink></li>
<li><RouterLink to="/urban-wild">Urban & Wild</RouterLink></li>
<li><RouterLink to="/community">Community</RouterLink></li>
</ul>
</div>
<div>
<strong>Legal</strong>
<ul>
<li><a href="/privacy" rel="nofollow">Privacy</a></li>
<li><a href="/terms" rel="nofollow">Terms</a></li>
</ul>
</div>
</div>
<div class="container" style="margin-top:1rem;font-size:.9rem">© {{ new Date().getFullYear() }} Plant'X</div>
</footer>
</template>
