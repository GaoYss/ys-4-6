<template>
  <div class="page-stack">
    <section class="stats-grid">
      <StatCard label="楼栋/房屋" :value="`${stats.building_count || 0} / ${stats.room_count || 0}`" />
      <StatCard label="应收金额" :value="money(stats.receivable_total)" />
      <StatCard label="实收金额" :value="money(stats.paid_total)" />
      <StatCard label="欠费金额" :value="money(stats.unpaid_total)" />
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>近期账单</h2>
        <button @click="load">刷新</button>
      </div>
      <DataTable :columns="columns" :rows="stats.recent_bills || []">
        <template #cell-status="{ row }">
          <StatusBadge :status="row.status" />
        </template>
        <template #cell-amount="{ row }">{{ money(row.amount) }}</template>
      </DataTable>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { propertyApi } from "../api/property";
import DataTable from "../components/DataTable.vue";
import StatCard from "../components/StatCard.vue";
import StatusBadge from "../components/StatusBadge.vue";

const stats = ref({});
const columns = [
  { key: "bill_no", label: "账单编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "业主" },
  { key: "fee_name", label: "费用" },
  { key: "period", label: "账期" },
  { key: "amount", label: "金额" },
  { key: "status", label: "状态" }
];

function money(value) {
  return `¥${Number(value || 0).toFixed(2)}`;
}

async function load() {
  stats.value = await propertyApi.dashboard();
}

onMounted(load);
</script>
