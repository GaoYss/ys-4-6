<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">物</span>
        <div>
          <strong>物业收费</strong>
          <small>Property Billing</small>
        </div>
      </div>
      <nav>
        <RouterLink v-for="item in navItems" :key="item.path" :to="item.path">
          <span>{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>
    <main class="content">
      <header class="topbar">
        <div>
          <h1>{{ currentTitle }}</h1>
          <p>楼栋、账单、缴费、催缴与票据集中管理</p>
        </div>
      </header>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const navItems = [
  { path: "/", label: "工作台", icon: "▦" },
  { path: "/buildings", label: "楼栋管理", icon: "⌂" },
  { path: "/fees", label: "费用生成", icon: "¥" },
  { path: "/payments", label: "在线缴费", icon: "✓" },
  { path: "/reminders", label: "欠费催缴", icon: "!" },
  { path: "/receipts", label: "票据打印", icon: "▣" }
];

const currentTitle = computed(() => route.meta.title || "小区物业费收缴系统");
</script>
