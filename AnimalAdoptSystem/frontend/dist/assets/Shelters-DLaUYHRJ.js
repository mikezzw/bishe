import{s as v}from"./index-DXLNZ-xC.js";import{_,c as r,a as s,h as u,v as k,g as m,i as g,e as w,F as b,r as y,t as l,b as f,o as c,n as x,j as h}from"./index-CADhgMZA.js";const S={name:"Shelters",data(){return{shelters:[],currentPage:1,itemsPerPage:6,total:0,searchQuery:"",selectedProvince:"",sortBy:"name",loading:!1,error:""}},computed:{displayedShelters(){const e=(this.currentPage-1)*this.itemsPerPage,t=e+this.itemsPerPage;return this.shelters.slice(e,t)},totalPages(){return Math.ceil(this.total/this.itemsPerPage)}},async mounted(){await this.loadShelters()},methods:{async loadShelters(){this.loading=!0;try{const e={page:this.currentPage,page_size:this.itemsPerPage};this.searchQuery&&(e.search=this.searchQuery),this.selectedProvince&&(e.province=this.selectedProvince),this.sortBy&&(e.ordering=this.sortBy);const t=await v.getShelters(e);console.log("获取基地列表响应:",t),t.results&&Array.isArray(t.results)?(this.shelters=t.results,this.total=t.count||t.results.length):Array.isArray(t)?(this.shelters=t,this.total=t.length):(this.shelters=[],this.total=0)}catch(e){console.error("加载基地列表失败:",e),this.error="加载基地列表失败，请稍后重试",this.shelters=[],this.total=0}finally{this.loading=!1}},async handleSearch(){this.currentPage=1,await this.loadShelters()},searchShelters(){this.handleSearch()},async filterByLocation(){this.currentPage=1,await this.loadShelters()},async sortShelters(){this.currentPage=1,await this.loadShelters()},viewShelterDetails(e){this.showShelterDetail(e)},contactShelter(e){this.showContactModal(e)},applyForActivity(e,t){if(!localStorage.getItem("token")){this.$router.push("/login");return}this.showActivityApplicationModal(e,t)},getActivityTypeText(e){return{adoption:"领养活动",volunteer:"志愿活动",fundraising:"筹款活动",education:"教育活动",other:"其他活动"}[e]||e},showActivityApplicationModal(e,t){const i=document.createElement("div");i.className="modal-overlay",i.innerHTML=`
        <div class="modal-content activity-modal">
          <div class="modal-header">
            <h2>申请参与活动</h2>
            <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="activity-info">
              <h3>${e.title}</h3>
              <p class="activity-type-tag ${e.activity_type}">
                ${this.getActivityTypeText(e.activity_type)}
              </p>
              <p><strong>基地：</strong>${t.name}</p>
              <p><strong>地点：</strong>${e.location}</p>
              <p><strong>时间：</strong>${new Date(e.start_time).toLocaleString()}</p>
              <p><strong>描述：</strong>${e.description}</p>
            </div>
            <div class="application-form">
              <h4>申请信息</h4>
              <div class="form-group">
                <label>申请类型</label>
                <select id="applicationType" class="form-control">
                  <option value="visit">探访</option>
                  <option value="volunteer">志愿服务</option>
                  <option value="foster">寄养</option>
                  <option value="other">其他</option>
                </select>
              </div>
              <div class="form-group">
                <label>申请目的</label>
                <textarea id="applicationPurpose" class="form-control" rows="3" placeholder="请输入您的申请目的..."></textarea>
              </div>
              <div class="form-group">
                <label>期望参与日期</label>
                <input type="datetime-local" id="desiredDate" class="form-control">
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">取消</button>
            <button class="btn btn-primary" onclick="this.closest('.modal-overlay').querySelector('.submit-application').click()">提交申请</button>
          </div>
        </div>
      `;const p=document.createElement("button");p.className="submit-application",p.style.display="none",p.onclick=()=>this.submitActivityApplication(e,t,i),i.appendChild(p),document.body.appendChild(i),this.addModalStyles()},async submitActivityApplication(e,t,i){try{const p=i.querySelector("#applicationType").value,n=i.querySelector("#applicationPurpose").value,a=i.querySelector("#desiredDate").value;if(!n||!a){alert("请填写完整的申请信息");return}const o=await v.submitInteraction({shelter:t.id,activity:e.id,application_type:p,purpose:n,desired_date:new Date(a).toISOString()});o.code===200?(alert("申请提交成功，等待基地审核"),i.remove()):alert("申请提交失败："+o.message)}catch(p){console.error("提交申请失败:",p),alert("申请提交失败，请稍后重试")}},showShelterDetail(e){const t=document.createElement("div");t.className="modal-overlay",t.innerHTML=`
        <div class="modal-content">
          <div class="modal-header">
            <h2>${e.name} 详情</h2>
            <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="detail-section">
              <h3>基本信息</h3>
              <p><strong>地址：</strong>${e.address}</p>
              <p><strong>联系人：</strong>${e.contact_name}</p>
              <p><strong>联系电话：</strong>${e.contact_phone}</p>
              <p><strong>邮箱：</strong>${e.email}</p>
              <p><strong>网站：</strong>${e.website||"暂无"}</p>
            </div>
            <div class="detail-section">
              <h3>运营信息</h3>
              <p><strong>容纳能力：</strong>${e.capacity} 只动物</p>
              <p><strong>当前动物数：</strong>${e.current_animals} 只</p>
              <p><strong>领养率：</strong>${e.adoption_rate}%</p>
              <p><strong>状态：</strong><span class="status ${e.status}">${e.status==="active"?"运营中":"暂停运营"}</span></p>
            </div>
            <div class="detail-section">
              <h3>基地介绍</h3>
              <p>${e.description}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
            <button class="btn btn-primary" onclick="document.querySelector('.contact-modal-trigger').click(); this.closest('.modal-overlay').remove()">联系基地</button>
          </div>
        </div>
      `;const i=document.createElement("button");i.className="contact-modal-trigger",i.style.display="none",i.onclick=()=>this.showContactModal(e),t.appendChild(i),document.body.appendChild(t),this.addModalStyles()},showContactModal(e){const t=document.createElement("div");t.className="modal-overlay",t.innerHTML=`
        <div class="modal-content contact-modal">
          <div class="modal-header">
            <h2>联系 ${e.name}</h2>
            <button class="close-btn" onclick="this.closest('.modal-overlay').remove()">×</button>
          </div>
          <div class="modal-body">
            <div class="contact-info">
              <div class="contact-item">
                <i class="icon">📞</i>
                <div>
                  <strong>电话联系</strong>
                  <p>${e.contact_phone}</p>
                </div>
              </div>
              <div class="contact-item">
                <i class="icon">✉️</i>
                <div>
                  <strong>邮件联系</strong>
                  <p>${e.email}</p>
                </div>
              </div>
              ${e.website?`
              <div class="contact-item">
                <i class="icon">🌐</i>
                <div>
                  <strong>官方网站</strong>
                  <p><a href="${e.website}" target="_blank">${e.website}</a></p>
                </div>
              </div>
              `:""}
            </div>
            <div class="quick-actions">
              <h3>快捷操作</h3>
              <div class="action-buttons">
                <button class="btn btn-primary" onclick="window.location.href='tel:${e.contact_phone.replace(/[^0-9]/g,"")}'">
                  直接拨打电话
                </button>
                <button class="btn btn-secondary" onclick="window.location.href='mailto:${e.email}'">
                  发送邮件
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">关闭</button>
          </div>
        </div>
      `,document.body.appendChild(t),this.addModalStyles()},addModalStyles(){if(document.getElementById("shelter-modal-styles"))return;const e=document.createElement("style");e.id="shelter-modal-styles",e.textContent=`
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
          animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        .modal-content {
          background: white;
          border-radius: 15px;
          width: 90%;
          max-width: 600px;
          max-height: 80vh;
          overflow-y: auto;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
          animation: slideUp 0.3s ease;
        }
        
        .contact-modal {
          max-width: 500px;
        }
        
        @keyframes slideUp {
          from { 
            opacity: 0;
            transform: translateY(30px);
          }
          to { 
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #eee;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .modal-header h2 {
          margin: 0;
          color: #333;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #999;
          padding: 5px;
          border-radius: 50%;
          width: 30px;
          height: 30px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .close-btn:hover {
          background: #f5f5f5;
          color: #333;
        }
        
        .modal-body {
          padding: 20px;
        }
        
        .detail-section {
          margin-bottom: 25px;
        }
        
        .detail-section h3 {
          color: #ff6b6b;
          margin-bottom: 15px;
          padding-bottom: 8px;
          border-bottom: 2px solid #ff6b6b;
        }
        
        .detail-section p {
          margin: 10px 0;
          line-height: 1.6;
        }
        
        .status {
          padding: 3px 10px;
          border-radius: 15px;
          color: white;
          font-size: 12px;
          font-weight: bold;
        }
        
        .status.active {
          background: #28a745;
        }
        
        .status.inactive {
          background: #dc3545;
        }
        
        .contact-info {
          margin-bottom: 25px;
        }
        
        .contact-item {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 10px;
          margin-bottom: 15px;
        }
        
        .contact-item .icon {
          font-size: 24px;
        }
        
        .contact-item strong {
          display: block;
          color: #333;
          margin-bottom: 5px;
        }
        
        .contact-item p {
          margin: 0;
          color: #666;
        }
        
        .contact-item a {
          color: #ff6b6b;
          text-decoration: none;
        }
        
        .contact-item a:hover {
          text-decoration: underline;
        }
        
        .quick-actions {
          text-align: center;
        }
        
        .quick-actions h3 {
          color: #ff6b6b;
          margin-bottom: 20px;
        }
        
        .action-buttons {
          display: flex;
          gap: 15px;
          justify-content: center;
          flex-wrap: wrap;
        }
        
        .modal-footer {
          padding: 20px;
          border-top: 1px solid #eee;
          display: flex;
          justify-content: flex-end;
          gap: 10px;
        }
        
        .btn {
          padding: 10px 20px;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s ease;
        }
        
        .btn-primary {
          background: linear-gradient(135deg, #ff9a3d 0%, #ff6b6b 100%);
          color: white;
        }
        
        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(255, 107, 107, 0.4);
        }
        
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #5a6268;
          transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
          .modal-content {
            width: 95%;
            margin: 10px;
          }
          
          .action-buttons {
            flex-direction: column;
          }
          
          .contact-item {
            flex-direction: column;
            text-align: center;
          }
        }
      `,document.head.appendChild(e)},truncateDescription(e){return e.length<=60?e:e.substring(0,60)+"..."},handleImageError(e){e.target.src="https://via.placeholder.com/300x200?text=图片加载失败"},prevPage(){this.currentPage>1&&(this.currentPage--,this.loadShelters())},nextPage(){this.currentPage<this.totalPages&&(this.currentPage++,this.loadShelters())}}},P={class:"shelters-page"},C={class:"search-section"},A={class:"container"},M={class:"search-bar"},T={class:"filters"},D={class:"shelters-list"},B={class:"container"},I={key:0,class:"loading"},E={key:1,class:"no-results"},N={key:2,class:"shelters-grid"},q=["onClick"],L={class:"shelter-image"},V=["src","alt"],j={class:"shelter-info"},z={class:"shelter-name"},Q={class:"shelter-address"},U={class:"shelter-stats"},F={class:"stat-item"},Y={class:"stat-number"},H={class:"stat-item"},O={class:"stat-number"},$={class:"stat-item"},G={class:"stat-number"},J={class:"shelter-description"},K={key:0,class:"shelter-activities"},R={class:"activities-list"},W=["onClick"],X={class:"activity-name"},Z={key:0,class:"more-activities"},tt={key:1,class:"shelter-activities empty"},et={class:"shelter-contact"},st={class:"contact-item"},ot={class:"contact-item"},at={class:"shelter-actions"},it=["onClick"],nt=["onClick"],lt={key:3,class:"pagination"},rt=["disabled"],ct={class:"page-info"},dt=["disabled"];function pt(e,t,i,p,n,a){return c(),r("div",P,[t[23]||(t[23]=s("div",{class:"page-header"},[s("div",{class:"container"},[s("h1",null,"动物基地列表"),s("p",null,"发现并了解各个动物救助基地")])],-1)),s("div",C,[s("div",A,[s("div",M,[u(s("input",{type:"text",placeholder:"搜索基地名称或地址...","onUpdate:modelValue":t[0]||(t[0]=o=>n.searchQuery=o),onInput:t[1]||(t[1]=(...o)=>a.handleSearch&&a.handleSearch(...o)),class:"search-input"},null,544),[[k,n.searchQuery]]),s("button",{class:"search-btn",onClick:t[2]||(t[2]=(...o)=>a.searchShelters&&a.searchShelters(...o))},[...t[10]||(t[10]=[s("i",{class:"search-icon"},"🔍",-1),m(" 搜索 ",-1)])])]),s("div",T,[u(s("select",{"onUpdate:modelValue":t[3]||(t[3]=o=>n.selectedProvince=o),onChange:t[4]||(t[4]=(...o)=>a.filterByLocation&&a.filterByLocation(...o)),class:"filter-select"},[...t[11]||(t[11]=[w('<option value="" data-v-7ca5feae>选择省份</option><option value="北京市" data-v-7ca5feae>北京市</option><option value="上海市" data-v-7ca5feae>上海市</option><option value="广东省" data-v-7ca5feae>广东省</option><option value="浙江省" data-v-7ca5feae>浙江省</option><option value="江苏省" data-v-7ca5feae>江苏省</option><option value="四川省" data-v-7ca5feae>四川省</option>',7)])],544),[[g,n.selectedProvince]]),u(s("select",{"onUpdate:modelValue":t[5]||(t[5]=o=>n.sortBy=o),onChange:t[6]||(t[6]=(...o)=>a.sortShelters&&a.sortShelters(...o)),class:"filter-select"},[...t[12]||(t[12]=[s("option",{value:"name"},"按名称排序",-1),s("option",{value:"animals_count"},"按动物数量排序",-1),s("option",{value:"created_at"},"按创建时间排序",-1)])],544),[[g,n.sortBy]])])])]),s("div",D,[s("div",B,[n.loading?(c(),r("div",I,[...t[13]||(t[13]=[s("div",{class:"spinner"},null,-1),s("p",null,"正在加载基地信息...",-1)])])):n.shelters.length===0?(c(),r("div",E,[...t[14]||(t[14]=[s("i",{class:"empty-icon"},"📭",-1),s("h3",null,"暂无符合条件的基地",-1),s("p",null,"请尝试调整搜索条件",-1)])])):(c(),r("div",N,[(c(!0),r(b,null,y(a.displayedShelters,o=>(c(),r("div",{key:o.id,class:"shelter-card",onClick:d=>a.viewShelterDetails(o)},[s("div",L,[s("img",{src:o.image||"https://via.placeholder.com/300x200?text=基地图片",alt:o.name,onError:t[7]||(t[7]=(...d)=>a.handleImageError&&a.handleImageError(...d))},null,40,V),s("div",{class:x(["shelter-status",o.status])},l(o.status==="active"?"运营中":"暂停运营"),3)]),s("div",j,[s("h3",z,l(o.name),1),s("p",Q,[t[15]||(t[15]=s("i",{class:"icon"},"📍",-1)),m(" "+l(o.address),1)]),s("div",U,[s("div",F,[s("span",Y,l(o.current_animals),1),t[16]||(t[16]=s("span",{class:"stat-label"},"救助动物",-1))]),s("div",H,[s("span",O,l(o.capacity),1),t[17]||(t[17]=s("span",{class:"stat-label"},"容纳能力",-1))]),s("div",$,[s("span",G,l(o.adoption_rate)+"%",1),t[18]||(t[18]=s("span",{class:"stat-label"},"领养率",-1))])]),s("p",J,l(a.truncateDescription(o.description)),1),o.activities&&o.activities.length>0?(c(),r("div",K,[t[19]||(t[19]=s("h4",{class:"activities-title"},"可申请活动",-1)),s("div",R,[(c(!0),r(b,null,y(o.activities.slice(0,2),d=>(c(),r("div",{key:d.id,class:"activity-item",onClick:h(mt=>a.applyForActivity(d,o),["stop"])},[s("span",X,l(d.title),1),s("span",{class:x(["activity-type",d.activity_type])},l(a.getActivityTypeText(d.activity_type)),3)],8,W))),128)),o.activities.length>2?(c(),r("div",Z," 还有 "+l(o.activities.length-2)+" 个活动... ",1)):f("",!0)])])):(c(),r("div",tt,[...t[20]||(t[20]=[s("p",null,"暂无可申请的活动",-1)])])),s("div",et,[s("span",st,[t[21]||(t[21]=s("i",{class:"icon"},"📞",-1)),m(" "+l(o.contact_phone),1)]),s("span",ot,[t[22]||(t[22]=s("i",{class:"icon"},"✉️",-1)),m(" "+l(o.email),1)])]),s("div",at,[s("button",{class:"btn btn-primary",onClick:h(d=>a.viewShelterDetails(o),["stop"])}," 查看详情 ",8,it),s("button",{class:"btn btn-secondary",onClick:h(d=>a.contactShelter(o),["stop"])}," 联系基地 ",8,nt)])])],8,q))),128))])),n.shelters.length>0?(c(),r("div",lt,[s("button",{class:"page-btn",disabled:n.currentPage===1,onClick:t[8]||(t[8]=(...o)=>a.prevPage&&a.prevPage(...o))}," 上一页 ",8,rt),s("span",ct," 第 "+l(n.currentPage)+" 页，共 "+l(a.totalPages)+" 页 ",1),s("button",{class:"page-btn",disabled:n.currentPage===a.totalPages,onClick:t[9]||(t[9]=(...o)=>a.nextPage&&a.nextPage(...o))}," 下一页 ",8,dt)])):f("",!0)])])])}const vt=_(S,[["render",pt],["__scopeId","data-v-7ca5feae"]]);export{vt as default};
