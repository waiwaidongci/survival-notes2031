<script setup lang="ts">
import {Bootstrap} from '../types/domain';import {number} from '../utils/format';
defineProps<{bootstrap:Bootstrap}>();
const interval=(v:[number,number]|null)=>v?number(v[0],0)+' – '+number(v[1],0)+' h':'不可估计';
</script>
<template>
<section class="boot-panel">
  <div class="section-top">
    <span class="eyebrow">ROLL CLUSTER BOOTSTRAP / 整卷重抽样</span>
    <span class="boot-meta">种子 {{bootstrap.seed}} · {{bootstrap.replicates}} 次重复 · {{Math.round(bootstrap.confidence*100)}}% 百分位区间</span>
  </div>
  <div class="boot-grid">
    <div v-for="g in bootstrap.groups" :key="g.cohort_id" class="boot-group">
      <span class="eyebrow">{{g.code}} / 来源卷</span>
      <b>{{g.rolls}} 卷</b>
      <small>中位区间 {{interval(g.median_interval)}}</small>
      <small>中位未达到 {{g.median_not_reached}} 次单列 · 有效 {{g.median_valid}} 次</small>
    </div>
    <div class="boot-diff">
      <span class="eyebrow">中位时长差（{{bootstrap.groups[1].code}} − {{bootstrap.groups[0].code}}）</span>
      <b>{{interval(bootstrap.median_difference.interval)}}</b>
      <small>有效重复 {{bootstrap.median_difference.valid}} / {{bootstrap.replicates}}</small>
      <small v-if="bootstrap.median_difference.not_reached">中位未达到 {{bootstrap.median_difference.not_reached}} 次单列，未计入区间</small>
      <small v-else>全部重复均达到中位</small>
    </div>
  </div>
  <p class="caption">抽中一卷保留该卷全部试件；固定种子 {{bootstrap.seed}} 重算结果一致。同卷灯带共用缺陷，按独立试件计算会低估不确定性；本区间为整卷重抽样百分位区间，仍是逐点口径。</p>
</section>
</template>
