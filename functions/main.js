export async function onRequestGet({ request }) {
  const ua = request.headers.get("user-agent") || "";
  const isMobile = /iphone|ipad|ipod|android/i.test(ua);

  if (isMobile) {
    return new Response(null, {
      status: 302,
      headers: {
        "Location": new URL("/main.html", request.url).toString(),
      },
    });
  }

  const html = `<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>fundocs</title><style>html,body{height:100%;margin:0}body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Arial,sans-serif;display:flex;align-items:center;justify-content:center}a{color:#fff}._box{max-width:560px;padding:28px 22px;text-align:center}._title{font-size:20px;font-weight:600;line-height:1.3;margin:0 0 12px}._text{font-size:14px;line-height:1.5;opacity:.85;margin:0 0 18px}._btns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}._btn{display:inline-block;padding:12px 16px;border-radius:14px;border:1px solid rgba(255,255,255,.25);text-decoration:none}._btn._primary{background:#fff;color:#000;border-color:#fff}._hint{font-size:12px;line-height:1.4;opacity:.75;margin:14px 0 0}</style></head><body><div class="_box"><h1 class="_title">${isMobile ? "Встановіть на телефон" : "Відкрийте на телефоні"}</h1><p class="_text">Ця версія оптимізована під мобільний режим. Відкрийте сайт на iPhone/Android і додайте на головний екран.</p><div class="_btns"><a class="_btn _primary" href="/main.html">Відкрити зараз</a><a class="_btn" href="/app/docs">Документи</a></div><p class="_hint">iPhone: Share → Add to Home Screen</p></div><script>(function(){try{var isStandalone=false;try{isStandalone=Boolean(window.navigator && window.navigator.standalone);}catch(e){}try{if(!isStandalone && window.matchMedia){isStandalone=window.matchMedia('(display-mode: standalone)').matches;}}catch(e){}if(isStandalone){location.replace('/main.html');}}catch(e){}})();</script></body></html>`;

  return new Response(html, {
    status: 200,
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
