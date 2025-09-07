<script>


</script>

<template>
<div class="Learnmore">
    <p>Learn More page</p>
    <section class="container">
        <div class="card">
            <RouterLink to="/LmOne">
            <h2 class="card__title">
            How Climate change threatens on Australian Plants
            <div>
            <small>Read Mores</small>
            </div>
            </h2>
            </RouterLink>
        </div>
    </section>

    <section class="container">
        <div class="card">
            <RouterLink to="/LmTwo">
            <h2 class="card__title">
            How Your Garden Support Nature In a Changing Climate
            <div>
            <small>Read Mores</small>
            </div>
            </h2>
            </RouterLink>
        </div>
    </section>

    <section class="container">
        <div class="card">
            <RouterLink to="/LmThree">
            <h2 class="card__title">
            Grow to protect: native plants you can save in your garden
            <div>
            <small>Read Mores</small>
            </div>
            </h2>
            </RouterLink>
    </div>
    </section>
</div>
</template>

<style scoped>
.container{
    margin-bottom: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.container:hover{
    transform: translateY(-8px) scale(1.03);
    box-shadow: 0 12px 24px rgba(0,0,0,0.2);
}


</style>