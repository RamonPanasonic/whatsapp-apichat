odoo.define('@246fdd94a52907ea2c78f199ed3160b163892e4c0b64ce81ff54b37a4fcdf05c',['@web/core/utils/patch','@whatsapp/components/whatsapp_button/whatsapp_button'],function(require){'use strict';let __exports={};const{patch}=require('@web/core/utils/patch')
const{SendWhatsAppButton}=require('@whatsapp/components/whatsapp_button/whatsapp_button')
patch(SendWhatsAppButton.prototype,{setup(){super.setup(...arguments)
const{doAction:superDoAction}=this.action
this.action={...this.action,doAction:async function(){arguments[0].context.call_from_ui=true
return superDoAction(...arguments)}}},})
return __exports;});;
odoo.define('@85f061a815783861079a98a7e8496c7d05e9df128ae6a559093bb19101ec2505',['@mail/core/web/chatter','@web/core/utils/patch','@odoo/owl'],function(require){'use strict';let __exports={};const{Chatter}=require('@mail/core/web/chatter')
const{patch}=require('@web/core/utils/patch')
const{onWillStart,onWillDestroy}=require('@odoo/owl')
patch(Chatter.prototype,{setup(){super.setup(...arguments)
const superDoAction=this.env.services.action.doAction
onWillStart(()=>{this.env.services.action.doAction=async function(){if(arguments[0]?.res_model==='whatsapp.composer'){arguments[0].context.call_from_ui=true}
return superDoAction(...arguments)}})
onWillDestroy(()=>{this.env.services.action.doAction=superDoAction})},})
return __exports;});;
odoo.define('@644822191b9933ebd145fd420f966358ee252f1a25d6434d790c09bc9436d76c',['@web/core/utils/patch','@mail/discuss/core/common/discuss_core_common_service'],function(require){'use strict';let __exports={};const{patch}=require('@web/core/utils/patch')
const{DiscussCoreCommon}=require('@mail/discuss/core/common/discuss_core_common_service')
patch(DiscussCoreCommon.prototype,{setup(){super.setup(...arguments)
this.messagingService.isReady.then((data)=>{this.busService.addEventListener('notification',({detail:notifications})=>{for(const notif of notifications){if(notif.type==='phone_status'){this.env.bus.trigger('whatsapp_account_phone_status',notif.payload)}}})
return data})},})
return __exports;});;
odoo.define('@30c31322d19943f7a0745710fbc98ae865951272c347fe004854d26e05764c91',['@mail/core/common/thread_model','@mail/utils/common/misc','@web/core/utils/urls','@web/core/utils/patch'],function(require){'use strict';let __exports={};const{Thread}=require('@mail/core/common/thread_model')
const{assignDefined}=require('@mail/utils/common/misc')
const{url}=require('@web/core/utils/urls')
const{patch}=require('@web/core/utils/patch')
patch(Thread.prototype,{update(data){super.update(data)
if(this.type==='whatsapp'){assignDefined(this,data,['account_type'])}},get imgUrl(){let out
if(this.isApichatChannel){out=url(`/discuss/channel/${this.id}/avatar_128`,assignDefined({},{unique:this.avatarCacheKey}))}else{out=super.imgUrl}
return out},get isApichatChannel(){return this.type==='whatsapp'&&this.account_type==='apichat'},})
return __exports;});;
odoo.define('@925bf807434cc398777f684ca8fc08acefcf133a8f81440226731e1c1c12813f',['@web/core/l10n/translation','@web/views/form/form_controller','@odoo/owl'],function(require){'use strict';let __exports={};const{_t}=require('@web/core/l10n/translation')
const{FormController}=require('@web/views/form/form_controller')
const{onWillDestroy}=require('@odoo/owl')
const WhatsappAccountScanQrController=__exports.WhatsappAccountScanQrController=class WhatsappAccountScanQrController extends FormController{setup(){super.setup(...arguments)
const func=this.processApichatNotify.bind(this)
this.env.bus.addEventListener('whatsapp_account_phone_status',func)
onWillDestroy(()=>{this.env.bus.removeEventListener('whatsapp_account_phone_status',func)})}
async processApichatNotify({detail:{id,status}}){if(this.model.root.data.account_id[0]===id){if(status.status==='connected'){await this.env.services.action.doAction({type:'ir.actions.act_window_close'})
await this.env.services.action.doAction({type:'ir.actions.client',tag:'display_notification',params:{title:_t('Connected'),type:'success',message:_t('Your phone is connected.'),}})}else if(status.status==='connecting'){if(status.qr){this.model.root.update({qr_code_img:status.qr})}}else if(status.status==='disconnected'){let reason=''
if(status.reason){reason=status.reason+'\n'}
await this.env.services.action.doAction({type:'ir.actions.act_window_close'})
await this.env.services.action.doAction({type:'ir.actions.client',tag:'display_notification',params:{title:_t('Not Connected'),type:'danger',sticky:true,message:reason+_t('Please try again or check apichat.'),}})}}}}
return __exports;});;
odoo.define('@bedd4fddc5f64e267df47ce47e91f2e763fb20b3e6e1fd776fd34cce01971108',['@web/core/registry','@web/views/form/form_view','@925bf807434cc398777f684ca8fc08acefcf133a8f81440226731e1c1c12813f'],function(require){'use strict';let __exports={};const{registry}=require('@web/core/registry')
const{formView}=require('@web/views/form/form_view')
const{WhatsappAccountScanQrController}=require('@925bf807434cc398777f684ca8fc08acefcf133a8f81440226731e1c1c12813f')
const WhatsappAccountScanQrView=__exports.WhatsappAccountScanQrView={...formView,Controller:WhatsappAccountScanQrController,}
registry.category('views').add('whatsapp_account_scan_qr',WhatsappAccountScanQrView)
return __exports;});;
