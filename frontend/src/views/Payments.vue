<template>
  <div class="page-stack">
    <section class="panel">
      <div class="panel-head">
        <h2>待缴账单</h2>
        <button @click="load">刷新</button>
      </div>
      <DataTable :columns="billColumns" :rows="unpaidBills">
        <template #cell-status="{ row }"><StatusBadge :status="row.status" /></template>
        <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
        <template #actions="{ row }">
          <button @click="pay(row)">缴费</button>
        </template>
      </DataTable>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>缴费记录</h2>
      </div>
      <DataTable :columns="paymentColumns" :rows="payments">
        <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
      </DataTable>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { propertyApi } from "../api/property";
import DataTable from "../components/DataTable.vue";
import StatusBadge from "../components/StatusBadge.vue";

const bills = ref([]);
const payments = ref([]);
const unpaidBills = computed(() => bills.value.filter((bill) => ["unpaid", "overdue"].includes(bill.status)));
const billColumns = [
  { key: "bill_no", label: "账单编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "业主" },
  { key: "amount", label: "金额" },
  { key: "due_date", label: "截止日期" },
  { key: "status", label: "状态" }
];
const paymentColumns = [
  { key: "receipt_no", label: "票据编号" },
  { key: "bill_no", label: "账单编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "付款人" },
  { key: "amount", label: "金额" },
  { key: "method", label: "方式" },
  { key: "paid_at", label: "支付时间" }
];

async function load() {
  [bills.value, payments.value] = await Promise.all([propertyApi.listBills(), propertyApi.listPayments()]);
}

async function pay(row) {
  await propertyApi.payBill(row.id, { method: "wechat", payer: row.owner_name });
  await load();
}

onMounted(load);
</script>
