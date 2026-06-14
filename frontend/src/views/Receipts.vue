<template>
  <div class="split-layout">
    <section class="panel">
      <div class="panel-head">
        <h2>票据列表</h2>
        <button @click="load">刷新</button>
      </div>
      <DataTable :columns="columns" :rows="payments" @click="noop">
        <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
        <template #actions="{ row }">
          <button @click="selected = row">预览</button>
        </template>
      </DataTable>
    </section>

    <section class="receipt-panel">
      <article v-if="selected" class="receipt">
        <header>
          <h2>物业费电子票据</h2>
          <span>{{ selected.receipt_no }}</span>
        </header>
        <dl>
          <div><dt>房屋</dt><dd>{{ selected.room_label }}</dd></div>
          <div><dt>业主</dt><dd>{{ selected.owner_name }}</dd></div>
          <div><dt>费用</dt><dd>{{ selected.period }} {{ selected.fee_name }}</dd></div>
          <div><dt>金额</dt><dd>¥{{ Number(selected.amount).toFixed(2) }}</dd></div>
          <div><dt>支付方式</dt><dd>{{ selected.method }}</dd></div>
          <div><dt>支付时间</dt><dd>{{ selected.paid_at }}</dd></div>
        </dl>
        <footer>
          <span>收款单位：小区物业服务中心</span>
          <button @click="printReceipt">打印票据</button>
        </footer>
      </article>
      <div v-else class="placeholder">选择一条缴费记录预览票据</div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { propertyApi } from "../api/property";
import DataTable from "../components/DataTable.vue";

const payments = ref([]);
const selected = ref(null);
const columns = [
  { key: "receipt_no", label: "票据编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "业主" },
  { key: "fee_name", label: "费用" },
  { key: "amount", label: "金额" },
  { key: "paid_at", label: "支付时间" }
];

async function load() {
  payments.value = await propertyApi.listPayments();
  selected.value = selected.value || payments.value[0] || null;
}

function printReceipt() {
  window.print();
}

function noop() {}

onMounted(load);
</script>
