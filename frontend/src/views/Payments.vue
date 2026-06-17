<template>
  <div class="page-stack">
    <section class="panel">
      <div class="panel-head">
        <h2>待缴账单</h2>
        <button @click="load">刷新</button>
      </div>
      <DataTable :columns="billColumns" :rows="unpaidBills">
        <template #cell-status="{ row }">
          <div class="status-col">
            <StatusBadge :status="row.status" />
            <span v-if="row.is_overdue && row.status !== 'overdue'" class="overdue-tag">已逾期</span>
          </div>
        </template>
        <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
        <template #cell-paid_amount="{ row }">¥{{ Number(row.paid_amount).toFixed(2) }}</template>
        <template #cell-remaining_amount="{ row }">¥{{ Number(row.remaining_amount).toFixed(2) }}</template>
        <template #cell-installments="{ row }">
          <span v-if="row.has_installments">
            第 {{ row.paid_installment_count }}/{{ row.installment_count }} 期
          </span>
          <span v-else>-</span>
        </template>
        <template #actions="{ row }">
          <button v-if="!row.has_installments" @click="openPayDialog(row)">缴费</button>
          <button v-if="!row.has_installments" class="secondary" @click="openInstallmentDialog(row)">分期</button>
          <button v-if="row.has_installments" @click="openInstallmentDetail(row)">查看分期</button>
        </template>
      </DataTable>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>缴费记录</h2>
      </div>
      <DataTable :columns="paymentColumns" :rows="payments">
        <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
        <template #cell-method="{ row }">{{ methodLabels[row.method] || row.method }}</template>
        <template #cell-installment="{ row }">
          <span v-if="row.installment_sequence">第 {{ row.installment_sequence }} 期</span>
          <span v-else>-</span>
        </template>
        <template #cell-overdue="{ row }">
          <span v-if="row.bill_is_overdue" class="overdue-tag">已逾期</span>
          <span v-else-if="row.bill_ever_overdue" class="ever-overdue-tag">曾逾期</span>
          <span v-else>-</span>
        </template>
      </DataTable>
    </section>

    <div v-if="showPayDialog" class="modal-overlay" @click.self="showPayDialog = false">
      <div class="modal">
        <div class="modal-head">
          <h3>账单缴费</h3>
          <button class="close" @click="showPayDialog = false">&times;</button>
        </div>
        <div class="modal-body" v-if="currentBill">
          <p>账单编号：<strong>{{ currentBill.bill_no }}</strong></p>
          <p>房屋：{{ currentBill.room_label }} / 业主：{{ currentBill.owner_name }}</p>
          <p>应收：<strong>¥{{ Number(currentBill.amount).toFixed(2) }}</strong></p>
          <p>已缴：¥{{ Number(currentBill.paid_amount).toFixed(2) }} / 剩余：<strong class="warn">¥{{ Number(currentBill.remaining_amount).toFixed(2) }}</strong></p>
          <form class="form-grid" @submit.prevent="submitPay">
            <label>支付金额
              <input type="number" v-model.number="payForm.amount" :max="Number(currentBill.remaining_amount)" step="0.01" min="0.01" required />
            </label>
            <label>支付方式
              <select v-model="payForm.method">
                <option value="wechat">微信</option>
                <option value="alipay">支付宝</option>
                <option value="bank">银行卡</option>
                <option value="cash">现金</option>
              </select>
            </label>
            <label>付款人
              <input v-model="payForm.payer" :placeholder="currentBill.owner_name" />
            </label>
            <div class="modal-actions">
              <button type="button" class="secondary" @click="showPayDialog = false">取消</button>
              <button type="submit">确认支付</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="showInstallmentDialog" class="modal-overlay" @click.self="showInstallmentDialog = false">
      <div class="modal">
        <div class="modal-head">
          <h3>申请分期缴费</h3>
          <button class="close" @click="showInstallmentDialog = false">&times;</button>
        </div>
        <div class="modal-body" v-if="currentBill">
          <p>账单编号：<strong>{{ currentBill.bill_no }}</strong></p>
          <p>应收：¥{{ Number(currentBill.amount).toFixed(2) }} / 已缴：¥{{ Number(currentBill.paid_amount).toFixed(2) }}</p>
          <p>分期拆分总额（剩余金额）：<strong class="warn">¥{{ Number(currentBill.remaining_amount).toFixed(2) }}</strong></p>
          <form class="form-grid" @submit.prevent="submitInstallment">
            <label>分期期数（2-12）
              <input type="number" v-model.number="installmentForm.count" min="2" max="12" required />
            </label>
            <label>首期截止日期
              <input type="date" v-model="installmentForm.first_due_date" />
            </label>
            <label>间隔天数
              <input type="number" v-model.number="installmentForm.interval_days" min="1" max="365" />
            </label>
            <div class="preview" v-if="installmentPreview.length">
              <p>分期预览：</p>
              <ul>
                <li v-for="(item, idx) in installmentPreview" :key="idx">
                  第 {{ idx + 1 }} 期：¥{{ Number(item.amount).toFixed(2) }}，截止 {{ item.due_date }}
                </li>
              </ul>
            </div>
            <div class="modal-actions">
              <button type="button" class="secondary" @click="showInstallmentDialog = false">取消</button>
              <button type="submit">确认分期</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <div v-if="showInstallmentDetail" class="modal-overlay" @click.self="showInstallmentDetail = false">
      <div class="modal wide">
        <div class="modal-head">
          <h3>
            分期详情 - {{ currentBill?.bill_no }}
            <span v-if="currentBill?.is_overdue" class="overdue-tag-inline">已逾期</span>
          </h3>
          <button class="close" @click="showInstallmentDetail = false">&times;</button>
        </div>
        <div class="modal-body" v-if="currentBill">
          <p>房屋：{{ currentBill.room_label }} / 业主：{{ currentBill.owner_name }}</p>
          <p>应收：¥{{ Number(currentBill.amount).toFixed(2) }} / 已缴：¥{{ Number(currentBill.paid_amount).toFixed(2) }} / 剩余：<strong class="warn">¥{{ Number(currentBill.remaining_amount).toFixed(2) }}</strong></p>
          <DataTable :columns="installmentColumns" :rows="currentBill.installments || []">
            <template #cell-status="{ row }"><StatusBadge :status="row.status" /></template>
            <template #cell-amount="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
            <template #actions="{ row }">
              <button v-if="row.status !== 'paid'" @click="openInstallmentPayDialog(row)">支付本期</button>
            </template>
          </DataTable>
          <div class="modal-actions">
            <button class="secondary" @click="showInstallmentDetail = false">关闭</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showInstallmentPayDialog" class="modal-overlay" @click.self="showInstallmentPayDialog = false">
      <div class="modal">
        <div class="modal-head">
          <h3>分期缴费确认</h3>
          <button class="close" @click="showInstallmentPayDialog = false">&times;</button>
        </div>
        <div class="modal-body" v-if="currentInstallment && currentBill">
          <p>账单编号：<strong>{{ currentBill.bill_no }}</strong></p>
          <p>房屋：{{ currentBill.room_label }} / 业主：{{ currentBill.owner_name }}</p>
          <p>期次：<strong>第 {{ currentInstallment.sequence }} 期</strong> / 共 {{ currentBill.installment_count }} 期</p>
          <p>本期金额：<strong class="warn">¥{{ Number(currentInstallment.amount).toFixed(2) }}</strong></p>
          <p>当前账单剩余：¥{{ Number(currentBill.remaining_amount).toFixed(2) }}</p>
          <p>付完本期后剩余：<strong>¥{{ afterPayRemaining.toFixed(2) }}</strong></p>
          <form class="form-grid" @submit.prevent="submitPayInstallment">
            <label>支付方式
              <select v-model="installmentPayForm.method">
                <option value="wechat">微信</option>
                <option value="alipay">支付宝</option>
                <option value="bank">银行卡</option>
                <option value="cash">现金</option>
              </select>
            </label>
            <label>付款人
              <input v-model="installmentPayForm.payer" :placeholder="currentBill.owner_name" />
            </label>
            <div class="modal-actions">
              <button type="button" class="secondary" @click="showInstallmentPayDialog = false">取消</button>
              <button type="submit">确认支付</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { propertyApi } from "../api/property";
import DataTable from "../components/DataTable.vue";
import StatusBadge from "../components/StatusBadge.vue";

const bills = ref([]);
const payments = ref([]);
const unpaidBills = computed(() => bills.value.filter((bill) => ["unpaid", "partial", "overdue"].includes(bill.status)));
const afterPayRemaining = computed(() => {
  if (!currentBill.value || !currentInstallment.value) return 0;
  const remaining = Number(currentBill.value.remaining_amount) - Number(currentInstallment.value.amount);
  return remaining < 0 ? 0 : Math.round(remaining * 100) / 100;
});

const billColumns = [
  { key: "bill_no", label: "账单编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "业主" },
  { key: "amount", label: "应收" },
  { key: "paid_amount", label: "已缴" },
  { key: "remaining_amount", label: "剩余" },
  { key: "due_date", label: "截止日期" },
  { key: "installments", label: "分期" },
  { key: "status", label: "状态" }
];
const paymentColumns = [
  { key: "receipt_no", label: "票据编号" },
  { key: "bill_no", label: "账单编号" },
  { key: "room_label", label: "房屋" },
  { key: "owner_name", label: "付款人" },
  { key: "installment", label: "分期期次" },
  { key: "amount", label: "金额" },
  { key: "method", label: "方式" },
  { key: "overdue", label: "逾期状态" },
  { key: "paid_at", label: "支付时间" }
];
const installmentColumns = [
  { key: "sequence", label: "期次" },
  { key: "amount", label: "金额" },
  { key: "due_date", label: "截止日期" },
  { key: "paid_at", label: "缴费时间" },
  { key: "status", label: "状态" }
];

const methodLabels = { wechat: "微信", alipay: "支付宝", bank: "银行卡", cash: "现金" };

const showPayDialog = ref(false);
const showInstallmentDialog = ref(false);
const showInstallmentDetail = ref(false);
const showInstallmentPayDialog = ref(false);
const currentBill = ref(null);
const currentInstallment = ref(null);

const payForm = reactive({ amount: 0, method: "wechat", payer: "" });
const installmentForm = reactive({ count: 3, first_due_date: "", interval_days: 30 });
const installmentPayForm = reactive({ method: "wechat", payer: "" });
const installmentPreview = ref([]);

async function load() {
  [bills.value, payments.value] = await Promise.all([propertyApi.listBills(), propertyApi.listPayments()]);
}

function openPayDialog(row) {
  currentBill.value = row;
  payForm.amount = Number(row.remaining_amount);
  payForm.method = "wechat";
  payForm.payer = row.owner_name;
  showPayDialog.value = true;
}

async function submitPay() {
  await propertyApi.payBill(currentBill.value.id, {
    method: payForm.method,
    payer: payForm.payer,
    amount: payForm.amount
  });
  showPayDialog.value = false;
  await load();
}

function openInstallmentDialog(row) {
  currentBill.value = row;
  installmentForm.count = 3;
  installmentForm.first_due_date = row.due_date;
  installmentForm.interval_days = 30;
  installmentPreview.value = [];
  showInstallmentDialog.value = true;
}

function _roundCentsToYuan(cents) {
  return Math.trunc(cents) / 100;
}

function _yuanToCents(yuanStr) {
  const s = String(yuanStr ?? "0").trim();
  if (!s) return 0;
  const [intPart, decPart = ""] = s.split(".");
  const padded = (decPart + "00").slice(0, 2);
  const sign = intPart.startsWith("-") ? -1 : 1;
  const absInt = intPart.replace(/^-/, "") || "0";
  return sign * (parseInt(absInt, 10) * 100 + parseInt(padded, 10));
}

function computePreview() {
  if (!currentBill.value) return;
  const totalYuan = Number(currentBill.value.remaining_amount || currentBill.value.amount);
  const totalCents = _yuanToCents(totalYuan.toFixed(2));
  const count = Math.min(Math.max(2, installmentForm.count || 2), 12);
  const baseCents = Math.floor(totalCents / count);
  const remainderCents = totalCents - baseCents * count;
  const start = installmentForm.first_due_date
    ? new Date(installmentForm.first_due_date)
    : currentBill.value.due_date
      ? new Date(currentBill.value.due_date)
      : new Date();
  const interval = Math.min(Math.max(1, installmentForm.interval_days || 30), 365);
  installmentPreview.value = Array.from({ length: count }, (_, i) => {
    const d = new Date(start);
    d.setDate(d.getDate() + interval * i);
    const iso = d.toISOString().slice(0, 10);
    const cents = i === count - 1 ? baseCents + remainderCents : baseCents;
    return { amount: _roundCentsToYuan(cents), due_date: iso };
  });
}

watch([() => installmentForm.count, () => installmentForm.first_due_date, () => installmentForm.interval_days], computePreview);

async function submitInstallment() {
  await propertyApi.createInstallments(currentBill.value.id, {
    count: installmentForm.count,
    first_due_date: installmentForm.first_due_date || undefined,
    interval_days: installmentForm.interval_days
  });
  showInstallmentDialog.value = false;
  await load();
}

async function openInstallmentDetail(row) {
  const detail = await propertyApi.getBill(row.id);
  currentBill.value = detail;
  showInstallmentDetail.value = true;
}

function openInstallmentPayDialog(inst) {
  currentInstallment.value = inst;
  installmentPayForm.method = "wechat";
  installmentPayForm.payer = currentBill.value.owner_name;
  showInstallmentPayDialog.value = true;
}

async function submitPayInstallment() {
  await propertyApi.payInstallment(currentInstallment.value.id, {
    method: installmentPayForm.method,
    payer: installmentPayForm.payer
  });
  showInstallmentPayDialog.value = false;
  const detail = await propertyApi.getBill(currentBill.value.id);
  currentBill.value = detail;
  await load();
}

onMounted(load);
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: grid;
  place-items: center;
  z-index: 50;
}
.modal {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  width: min(520px, 94vw);
  max-height: 90vh;
  overflow: auto;
}
.modal.wide { width: min(780px, 96vw); }
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e6edf2;
  padding-bottom: 10px;
  margin-bottom: 14px;
}
.modal-head h3 { margin: 0; font-size: 17px; }
.close {
  background: transparent;
  color: #52606d;
  font-size: 22px;
  padding: 0 6px;
  min-height: 28px;
}
.close:hover { background: #f1f5f9; color: #1f2933; }
.modal-body p { margin: 4px 0; color: #334155; }
.modal-body .warn { color: #b42318; }
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}
.secondary {
  background: #e2e8f0;
  color: #1f2933;
}
.secondary:hover { background: #cbd5e1; }
.preview {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 10px 14px;
}
.preview ul { margin: 6px 0 0; padding-left: 20px; }
.preview li { padding: 2px 0; color: #334155; }
.actions button + button { margin-left: 6px; }
.status-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
}
.overdue-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  background: #ffe2e2;
  color: #b42318;
  font-size: 12px;
}
.overdue-tag-inline {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #ffe2e2;
  color: #b42318;
  font-size: 13px;
  font-weight: 500;
}
</style>
