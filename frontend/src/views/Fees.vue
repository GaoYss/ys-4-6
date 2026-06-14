<template>
  <div class="split-layout">
    <section class="panel form-panel">
      <h2>费用标准</h2>
      <form @submit.prevent="saveFeeType" class="form-grid">
        <label>费用名称<input v-model="feeForm.name" required placeholder="物业费" /></label>
        <label>计费方式
          <select v-model="feeForm.billing_method">
            <option value="fixed">固定金额</option>
            <option value="area">按面积</option>
          </select>
        </label>
        <label>金额/单价<input v-model.number="feeForm.amount" type="number" min="0" step="0.01" required /></label>
        <label>周期
          <select v-model="feeForm.cycle">
            <option value="monthly">月度</option>
            <option value="quarterly">季度</option>
            <option value="yearly">年度</option>
          </select>
        </label>
        <button type="submit">保存标准</button>
      </form>

      <h2>批量生成账单</h2>
      <form @submit.prevent="generate" class="form-grid">
        <label>费用类型
          <select v-model="generateForm.fee_type" required>
            <option value="" disabled>请选择</option>
            <option v-for="fee in feeTypes" :key="fee.id" :value="fee.id">{{ fee.name }}</option>
          </select>
        </label>
        <label>账期<input v-model="generateForm.period" required placeholder="2026-06" /></label>
        <label>截止日期<input v-model="generateForm.due_date" type="date" required /></label>
        <button type="submit">生成账单</button>
      </form>
      <p v-if="message" class="notice">{{ message }}</p>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>费用标准</h2>
        <button @click="load">刷新</button>
      </div>
      <DataTable :columns="feeColumns" :rows="feeTypes" />

      <div class="panel-head section-gap">
        <h2>账单列表</h2>
      </div>
      <DataTable :columns="billColumns" :rows="bills">
        <template #cell-status="{ row }"><StatusBadge :status="row.status" /></template>
        <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
      </DataTable>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { propertyApi } from "../api/property";
import DataTable from "../components/DataTable.vue";
import StatusBadge from "../components/StatusBadge.vue";

const feeTypes = ref([]);
const bills = ref([]);
const message = ref("");
const feeForm = reactive({ name: "", billing_method: "fixed", amount: 0, cycle: "monthly" });
const generateForm = reactive({ fee_type: "", period: "2026-06", due_date: "2026-06-30" });
const feeColumns = [
  { key: "name", label: "名称" },
  { key: "billing_method", label: "计费方式" },
  { key: "amount", label: "金额/单价" },
  { key: "cycle", label: "周期" }
];
const billColumns = [
  { key: "bill_no", label: "账单编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "业主" },
  { key: "fee_name", label: "费用" },
  { key: "period", label: "账期" },
  { key: "amount", label: "金额" },
  { key: "status", label: "状态" }
];

async function load() {
  [feeTypes.value, bills.value] = await Promise.all([propertyApi.listFeeTypes(), propertyApi.listBills()]);
}

async function saveFeeType() {
  await propertyApi.createFeeType({ ...feeForm });
  Object.assign(feeForm, { name: "", billing_method: "fixed", amount: 0, cycle: "monthly" });
  await load();
}

async function generate() {
  const result = await propertyApi.generateBills({ ...generateForm });
  message.value = `已生成 ${result.created_count} 条，跳过重复 ${result.skipped_count} 条`;
  await load();
}

onMounted(load);
</script>
