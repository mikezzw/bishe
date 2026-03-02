<template>
  <div class="adoptions">
    <div class="container">
      <h2>领养流程</h2>
      <div class="process-steps">
        <div class="step-item">
          <div class="step-number">1</div>
          <h3>浏览动物</h3>
          <p>在动物列表中浏览可领养的流浪动物，查看它们的详细信息</p>
        </div>
        <div class="step-item">
          <div class="step-number">2</div>
          <h3>提交申请</h3>
          <p>选择心仪的动物，填写领养申请表格，提交个人信息</p>
        </div>
        <div class="step-item">
          <div class="step-number">3</div>
          <h3>审核流程</h3>
          <p>工作人员会对您的申请进行审核，可能会联系您进行进一步了解</p>
        </div>
        <div class="step-item">
          <div class="step-number">4</div>
          <h3>领养成功</h3>
          <p>审核通过后，您可以前往指定地点领养您的新伙伴</p>
        </div>
      </div>
      <div class="adoption-actions">
        <router-link to="/animals" class="btn btn-primary">浏览可领养动物</router-link>
        <router-link to="/adoption/my" class="btn btn-secondary">查看我的申请</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Adoptions'
}
</script>

<style scoped>
.adoptions {
  padding: 40px 0;
  background: linear-gradient(135deg, #fff8f0 0%, #ffeaa7 100%);
  min-height: 100vh;
}

.adoptions h2 {
  margin-bottom: 40px;
  font-size: 28px;
  color: #333;
  text-align: center;
}

.process-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
  margin-bottom: 40px;
}

.step-item {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  text-align: center;
  position: relative;
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #ff9a3d;
  color: white;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.step-item h3 {
  font-size: 20px;
  margin-bottom: 15px;
  color: #333;
}

.step-item p {
  color: #666;
  line-height: 1.5;
}

.adoption-actions {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
}

.btn {
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  text-decoration: none;
  transition: background-color 0.3s;
  display: inline-block;
}

.btn-primary {
  background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 15px rgba(255, 154, 61, 0.3);
  font-weight: bold;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff9a3d 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, #ffffff 0%, #fff5e6 100%);
  color: #ff6b6b;
  border: 2px solid #ffcc99;
  box-shadow: 0 2px 8px rgba(255, 154, 61, 0.2);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #fff5e6 0%, #ffffff 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 61, 0.3);
  border-color: #ff9a3d;
}

@media (max-width: 768px) {
  .adoption-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 200px;
    text-align: center;
  }
}
</style>
