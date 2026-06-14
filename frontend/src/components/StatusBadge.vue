<template>
  <span class="status-badge" :class="status">{{ labels[status] || status }}</span>
</template>

<script setup>
defineProps({ status: { type: String, required: true } });

const labels = {
  unpaid: "待缴费",
  paid: "已缴费",
  overdue: "已逾期",
  cancelled: "已作废",
  pending: "待发送",
  sent: "已发送"
};
</script>
