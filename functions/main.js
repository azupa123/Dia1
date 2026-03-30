export async function onRequestGet({ request }) {
  const ua = request.headers.get("user-agent") || "";
  const isDesktop = /windows nt|macintosh|cros|linux x86_64/i.test(ua);

  if (!isDesktop) {
    const upstreamUrl = new URL("/main.html", request.url);
    const upstreamRes = await fetch(upstreamUrl.toString());

    const headers = new Headers(upstreamRes.headers);
    headers.set("Cache-Control", "no-store");
    return new Response(upstreamRes.body, {
      status: upstreamRes.status,
      headers,
    });
  }

  const html = `<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>fundocs</title><style>html,body{height:100%;margin:0}body{background:#000;color:#fff;font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Arial,sans-serif;display:flex;align-items:center;justify-content:center}a{color:#fff}._box{max-width:560px;padding:28px 22px;text-align:center}._title{font-size:20px;font-weight:600;line-height:1.3;margin:0 0 12px}._text{font-size:14px;line-height:1.5;opacity:.85;margin:0 0 18px}._btns{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}._btn{display:inline-block;padding:12px 16px;border-radius:14px;border:1px solid rgba(255,255,255,.25);text-decoration:none}._btn._primary{background:#fff;color:#000;border-color:#fff}</style></head><body><div class="_box"><h1 class="_title">Відкрийте на телефоні</h1><p class="_text">Ця версія оптимізована під мобільний режим. Відкрийте сайт на iPhone/Android.</p><div class="_btns"><a class="_btn _primary" href="/main.html">Відкрити</a><a class="_btn" href="/app/docs">Документи</a></div></div></body></html>`;

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
