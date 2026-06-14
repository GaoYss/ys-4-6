<template>
  <section class="stat-card">
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
  </section>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true }
});
</script>
