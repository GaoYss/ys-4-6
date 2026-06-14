<template>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
          <th v-if="$slots.actions">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="!rows.length">
          <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="empty">暂无数据</td>
        </tr>
        <tr v-for="row in rows" :key="row.id || row.bill_no || row.payment_no">
          <td v-for="column in columns" :key="column.key">
            <slot :name="`cell-${column.key}`" :row="row">{{ formatValue(row, column.key) }}</slot>
          </td>
          <td v-if="$slots.actions" class="actions">
            <slot name="actions" :row="row"></slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  rows: { type: Array, default: () => [] }
});

function formatValue(row, key) {
  return key.split(".").reduce((value, part) => value?.[part], row) ?? "-";
}
</script>
