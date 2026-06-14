import { createRouter, createWebHistory } from "vue-router";

import Dashboard from "../views/Dashboard.vue";
import Buildings from "../views/Buildings.vue";
import Fees from "../views/Fees.vue";
import Payments from "../views/Payments.vue";
import Reminders from "../views/Reminders.vue";
import Receipts from "../views/Receipts.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Dashboard, meta: { title: "工作台" } },
    { path: "/buildings", component: Buildings, meta: { title: "楼栋管理" } },
    { path: "/fees", component: Fees, meta: { title: "费用生成" } },
    { path: "/payments", component: Payments, meta: { title: "在线缴费" } },
    { path: "/reminders", component: Reminders, meta: { title: "欠费催缴" } },
    { path: "/receipts", component: Receipts, meta: { title: "票据打印" } }
  ]
});

export default router;
