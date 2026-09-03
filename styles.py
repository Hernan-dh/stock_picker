"""Visual identity for the stock picker interface."""

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Manrope:wght@400;500;600;700&display=swap');
:root { --bg:#111412; --surface:#181c19; --raised:#202522; --border:#343a35; --text:#e9e9e3; --muted:#909690; --acid:#c7ff37; --orange:#ff6947; --mono:'DM Mono',monospace; --sans:'Manrope',sans-serif; }
footer,.built-with,.show-api,.api-docs { display:none!important; }
html,body,gradio-app { background:var(--bg)!important; color-scheme:dark; }
body { background-image:linear-gradient(rgb(255 255 255 / 2.5%) 1px,transparent 1px),linear-gradient(90deg,rgb(255 255 255 / 2.5%) 1px,transparent 1px)!important; background-size:42px 42px!important; }
.gradio-container { width:100%!important; max-width:920px!important; min-width:0!important; margin:0 auto!important; padding:34px 24px 48px!important; background:transparent!important; color:var(--text)!important; font-family:var(--sans)!important; }
.gradio-container * { min-width:0; }
#title-row { align-items:center!important; flex-wrap:nowrap!important; gap:28px!important; margin-bottom:2.5rem!important; padding-bottom:1.25rem!important; border-bottom:3px solid var(--text)!important; }
#header-copy,#stock-header { margin:0!important; padding:0!important; }
.stock-brand { display:grid; grid-template-columns:auto 1fr; align-items:center; gap:1.4rem; }
.stock-mark { display:flex; flex-direction:column; gap:5px; width:38px; }
.stock-bar { display:block; height:7px; }
.stock-bar-1 { width:100%; background:var(--acid); } .stock-bar-2 { width:70%; background:#209dd7; } .stock-bar-3 { width:45%; background:var(--orange); }
.stock-headings h1 { margin:0!important; color:var(--text)!important; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important; font-size:clamp(1.55rem,3.6vw,2.35rem)!important; font-weight:900!important; line-height:.95!important; letter-spacing:-.045em!important; }
.stock-sep { margin:0 .04em; color:var(--acid); font-weight:300; }
.stock-headings p { margin:.55rem 0 0!important; color:var(--muted)!important; font:400 .7rem var(--mono)!important; letter-spacing:.22em; }
#language-control { width:170px!important; min-width:170px!important; max-width:170px!important; flex:0 0 170px!important; gap:5px!important; margin-left:auto!important; }
#language-label p { margin:0!important; color:var(--muted)!important; font:400 9px var(--mono)!important; letter-spacing:.08em; text-transform:uppercase; }
#language-selector input,#language-selector button { min-height:34px!important; height:34px!important; }
.sector-examples,.sector-examples>div,.sector-examples-label,.sector-examples-label>div { margin:0!important; padding:0!important; border:0!important; background:transparent!important; box-shadow:none!important; }
.sector-examples-label { padding:7px 0!important; }
.sector-examples-label p { margin:0!important; color:var(--muted)!important; font:400 9px var(--mono)!important; letter-spacing:.08em; text-transform:uppercase; }
.sector-examples { gap:8px!important; margin-bottom:12px!important; }
.sector-examples button { min-height:46px!important; height:auto!important; padding:8px 12px!important; border:1px solid var(--border)!important; background:var(--surface)!important; color:var(--text)!important; font:500 12px/1.35 var(--sans)!important; text-align:left!important; white-space:normal!important; }
.sector-examples button:hover { border-color:var(--acid)!important; color:var(--acid)!important; }
.sector-input-row { gap:0!important; margin:0!important; } .sector-input-row button { min-width:118px!important; }
.block,.form { background:transparent!important; box-shadow:none!important; }
.chatbot,.chatbot *,.block,.form,button,input,textarea { border-radius:0!important; }
#stock-chat-en,#stock-chat-es { height:520px!important; min-height:520px!important; border:1px solid var(--border)!important; background:rgb(24 28 25 / 94%)!important; box-shadow:18px 18px 0 rgb(0 0 0 / 18%)!important; }
.message-row .message,.message-row .message-bubble { font-size:14px!important; line-height:1.6!important; }
.message-row.user-row .message,.message-row[data-role='user'] .message { background:var(--acid)!important; color:var(--bg)!important; }
.message-row.bot-row .message,.message-row[data-role='assistant'] .message { border-left:2px solid var(--orange)!important; background:var(--raised)!important; color:var(--text)!important; }
textarea,input[type='text'] { min-height:50px!important; padding:13px 14px!important; border:1px solid var(--border)!important; background:var(--surface)!important; color:var(--text)!important; font:400 14px/1.45 var(--sans)!important; }
textarea:focus,input[type='text']:focus { border-color:var(--acid)!important; outline:none!important; box-shadow:0 0 0 1px var(--acid)!important; }
button { min-height:50px!important; border:1px solid var(--border)!important; background:var(--surface)!important; color:var(--text)!important; font:500 10px var(--mono)!important; letter-spacing:.1em!important; text-transform:uppercase!important; }
button.primary,button[variant='primary'] { border-color:var(--acid)!important; background:var(--acid)!important; color:var(--bg)!important; }
@media (max-width:640px) { .gradio-container{padding:22px 14px 34px!important} #title-row{flex-wrap:wrap!important;gap:16px!important} #language-control{width:100%!important;margin-left:0!important} .sector-examples{flex-direction:column!important} #stock-chat-en,#stock-chat-es{height:500px!important;min-height:500px!important;box-shadow:8px 8px 0 rgb(0 0 0 / 18%)!important} }
"""

JS = r"""
() => {
  document.title = (navigator.language || '').toLowerCase().startsWith('es') ? 'Selector de acciones' : 'Stock Picker';
  setTimeout(() => document.querySelector('textarea')?.focus(), 400);
}
"""
