<template>
  <div class="split-layout">
    <section class="panel form-panel">
      <h2>新增楼栋</h2>
      <form @submit.prevent="saveBuilding" class="form-grid">
        <label>楼栋名称<input v-model="buildingForm.name" required placeholder="1号楼" /></label>
        <label>地址<input v-model="buildingForm.address" placeholder="小区东区" /></label>
        <label>楼层数<input v-model.number="buildingForm.floor_count" type="number" min="1" /></label>
        <label>单元数<input v-model.number="buildingForm.unit_count" type="number" min="1" /></label>
        <label>楼管员<input v-model="buildingForm.manager" /></label>
        <button type="submit">保存楼栋</button>
      </form>

      <h2>新增房屋</h2>
      <form @submit.prevent="saveRoom" class="form-grid">
        <label>所属楼栋
          <select v-model="roomForm.building" required>
            <option value="" disabled>请选择</option>
            <option v-for="building in buildings" :key="building.id" :value="building.id">{{ building.name }}</option>
          </select>
        </label>
        <label>房号<input v-model="roomForm.room_no" required placeholder="1-101" /></label>
        <label>业主<input v-model="roomForm.owner_name" required /></label>
        <label>电话<input v-model="roomForm.phone" /></label>
        <label>面积<input v-model.number="roomForm.area" type="number" step="0.01" min="0" /></label>
        <button type="submit">保存房屋</button>
      </form>
    </section>

    <section class="panel">
      <div class="panel-head">
        <h2>楼栋列表</h2>
        <button @click="load">刷新</button>
      </div>
      <DataTable :columns="buildingColumns" :rows="buildings" />

      <div class="panel-head section-gap">
        <h2>房屋档案</h2>
      </div>
      <DataTable :columns="roomColumns" :rows="rooms" />
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { propertyApi } from "../api/property";
import DataTable from "../components/DataTable.vue";

const buildings = ref([]);
const rooms = ref([]);
const buildingForm = reactive({ name: "", address: "", floor_count: 1, unit_count: 1, manager: "" });
const roomForm = reactive({ building: "", room_no: "", owner_name: "", phone: "", area: 0 });
const buildingColumns = [
  { key: "name", label: "楼栋" },
  { key: "address", label: "地址" },
  { key: "floor_count", label: "楼层" },
  { key: "unit_count", label: "单元" },
  { key: "manager", label: "楼管员" },
  { key: "room_count", label: "房屋数" }
];
const roomColumns = [
  { key: "building_name", label: "楼栋" },
  { key: "room_no", label: "房号" },
  { key: "owner_name", label: "业主" },
  { key: "phone", label: "电话" },
  { key: "area", label: "面积" }
];

async function load() {
  [buildings.value, rooms.value] = await Promise.all([propertyApi.listBuildings(), propertyApi.listRooms()]);
}

async function saveBuilding() {
  await propertyApi.createBuilding({ ...buildingForm });
  Object.assign(buildingForm, { name: "", address: "", floor_count: 1, unit_count: 1, manager: "" });
  await load();
}

async function saveRoom() {
  await propertyApi.createRoom({ ...roomForm });
  Object.assign(roomForm, { building: "", room_no: "", owner_name: "", phone: "", area: 0 });
  await load();
}

onMounted(load);
</script>
